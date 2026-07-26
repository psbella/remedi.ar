"""etl/enriquecimiento.py - Enriquecimiento de registros con campos de presentacion/dosis."""

import re

from .config import PAMI_PATH
from .presentacion import _parsear_presentacion


def enriquecer_dosis(medicamentos: list) -> None:
    """
    Promueve campos de presentacion parseada (forma/dosis/unidad/cantidad)
    a cada registro, con fallbacks de rescate de dosis desde el nombre de
    marca y desde el vademecum de PAMI. Modifica los registros in-place.
    """
    # ── Promover campos parseados de presentación a cada registro ────────
    print("\nEnriqueciendo registros con campos de presentación...")
    _RE_DOSIS_MARCA = re.compile(
        r'(\d+[\.,]?\d*)\s*/\s*(\d+[\.,]?\d*)\s*(mg|mcg|g|ui|%)|'  # "750/15 mg"
        r'(\d+[\.,]?\d*)\s*(mg|mcg|µg|g\b|ui|iu|%|meq)',             # "1000 MG" / "1.5%"
        re.IGNORECASE
    )
    # Número al final del nombre sin unidad: ATORMAX 10, LISOVYR 400, BIOCLAVID 875/125
    # Excluye B12, B6, etc. y requiere ≥2 dígitos si no hay unidad
    _RE_DOSIS_NOMBRE = re.compile(
        r'(?<![A-Za-z\d])(\d+[\.,]?\d*)\s*/\s*(\d+[\.,]?\d*)\s*(?:U\.I\.?|UI|MG|MCG|%)?\s*$|'
        r'(?<![A-Za-z])(\d+[\.,]?\d*)\s*(U\.I\.?|UI|MG|MCG|%)\s*$|'
        r'(?<![A-Za-z\d/])(\d{2,})\s*$',
        re.IGNORECASE
    )
    # Categorías donde la dosis no aplica estructuralmente
    _RE_DROGA_SIN_DOSIS = re.compile(
        r'\bvacun|antigen|antigripal|vitamina[^s]|multivitamin|'
        r'anticonceptiv|levonorgestrel|etinil|dienogest|drospirenon|noretisterona|'
        r'acido folic\b|folico\b|herbal|fitoterapia|preparacion herbaria|'
        r'hepatalgina|suero oral|solucion de rehidratacion|'
        r'agua oxigenada|alcohol etilico\b|cloruro de sodio.*0\.9',
        re.IGNORECASE
    )
    _FORMAS_SIN_DOSIS = {
        'CREMA', 'GEL', 'POMADA', 'SHAMPOO', 'LOCIÓN', 'COLIRIO',
        'SOLUCIÓN OFTÁLMICA', 'JABÓN LÍQUIDO', 'PASTA DÉRMICA',
        'ESPUMA', 'TOALLITAS', 'TALQUERA', 'LACA', 'EMULSIÓN',
        'LOCIÓN ATOMIZADOR', 'POTE',
    }
    n_enriquecidos = 0
    n_dosis_marca  = 0
    for m in medicamentos:
        pres = (m.get('presentacion') or '').strip()
        if not pres:
            continue
        r = _parsear_presentacion(pres)
        if r['forma'] or r['dosis']:
            if r['forma']:
                m['pres_forma'] = r['forma']
            if r['dosis']:
                m['pres_dosis'] = r['dosis']
            if r['unidad']:
                m['pres_unidad'] = r['unidad']
            if r['cantidad']:
                m['pres_cantidad'] = r['cantidad']
            n_enriquecidos += 1
        # Fallback: buscar dosis en el nombre de marca si presentacion no la tiene
        if not m.get('pres_dosis'):
            marca = (m.get('marca') or '').strip()
            hm = _RE_DOSIS_MARCA.search(marca)
            if hm:
                if hm.group(1) and hm.group(2):  # patrón barra: 750/15 mg
                    m['pres_dosis']  = f"{hm.group(1)}/{hm.group(2)}"
                    m['pres_unidad'] = hm.group(3).upper()
                elif hm.group(4):                 # patrón simple: 1000 MG
                    m['pres_dosis']  = hm.group(4).replace(',', '.')
                    m['pres_unidad'] = hm.group(5).upper()
                m['pres_dosis_fuente'] = 'marca'
                n_dosis_marca += 1
        # Fallback: dosis al final del nombre de marca (ATORMAX 10, BIOCLAVID 875/125)
        if not m.get('pres_dosis'):
            marca = (m.get('marca') or '').strip()
            hn = _RE_DOSIS_NOMBRE.search(marca)
            if hn:
                if hn.group(1) and hn.group(2):   # barra: 875/125
                    m['pres_dosis']  = f"{hn.group(1)}/{hn.group(2)}"
                    m['pres_unidad'] = 'MG'
                elif hn.group(3):                  # con unidad: 1000 U.I.
                    m['pres_dosis']  = hn.group(3).replace(',', '.')
                    m['pres_unidad'] = re.sub(r'\.', '', hn.group(4)).upper()
                else:                              # solo número: ATORMAX 10
                    m['pres_dosis']  = hn.group(5)
                    m['pres_unidad'] = 'MG'
                m['pres_dosis_fuente'] = 'nombre'
                n_dosis_marca += 1
        # Marcar categorías donde la dosis no aplica estructuralmente
        if not m.get('pres_dosis'):
            droga = (m.get('droga') or '').strip()
            forma = m.get('pres_forma') or ''
            if _RE_DROGA_SIN_DOSIS.search(droga) or forma in _FORMAS_SIN_DOSIS:
                m['pres_dosis_fuente'] = 'no_aplica'
    print(f"   Enriquecidos: {n_enriquecidos}/{len(medicamentos)} ({100*n_enriquecidos/max(len(medicamentos),1):.1f}%)")
    print(f"   Dosis rescatadas de marca: {n_dosis_marca}")

    # ── Fallback dosis desde PAMI (marca+forma+cantidad compatibles) ──────
    _RE_DOSIS_CONC_PAMI = re.compile(r'(\d+[\.,]?\d*)\s*(mg|mcg|µg|ui|iu|%|meq)\b', re.IGNORECASE)
    _RE_FORMA_PAMI      = re.compile(r'(comp|caps|susp|sol|jbe|gts|cr|gel|ung|pomo|sob|a\b|f\.a|vial|amp)', re.IGNORECASE)
    _RE_CANT_PAMI       = re.compile(r'x\s*(\d+)', re.IGNORECASE)

    pami_dosis_idx: dict = {}
    if PAMI_PATH.exists():
        import pandas as _pd
        pami_df = _pd.read_excel(PAMI_PATH)
        pami_df.columns = [c.strip() for c in pami_df.columns]
        for row in pami_df.itertuples(index=False):
            marca_p = str(getattr(row, 'MARCA', '')).strip().upper()
            pres_p  = str(getattr(row, 'PRESENTACION', '')).strip().lower()
            hit     = _RE_DOSIS_CONC_PAMI.search(pres_p)
            if hit:
                pami_dosis_idx.setdefault(marca_p, []).append((pres_p, hit))

    def _forma_compat(ps, pp):
        f1 = _RE_FORMA_PAMI.search(ps.lower())
        f2 = _RE_FORMA_PAMI.search(pp.lower())
        return bool(f1 and f2 and f1.group(1).lower()[:3] == f2.group(1).lower()[:3])

    def _cant_compat(ps, pp):
        c1 = _RE_CANT_PAMI.search(ps)
        c2 = _RE_CANT_PAMI.search(pp)
        return (c1.group(1) == c2.group(1)) if (c1 and c2) else True

    n_dosis_pami = 0
    for m in medicamentos:
        if m.get('pres_dosis'):
            continue
        marca_up    = (m.get('marca') or '').strip().upper()
        pres_siafar = (m.get('presentacion') or '').strip().lower()
        for pres_p, hit in pami_dosis_idx.get(marca_up, []):
            if _forma_compat(pres_siafar, pres_p) and _cant_compat(pres_siafar, pres_p):
                m['pres_dosis']        = hit.group(1).replace(',', '.')
                m['pres_unidad']       = hit.group(2).upper()
                m['pres_dosis_fuente'] = 'pami'
                n_dosis_pami += 1
                break
    print(f"   Dosis rescatadas de PAMI: {n_dosis_pami}")

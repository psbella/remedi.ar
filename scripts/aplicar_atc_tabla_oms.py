"""
scripts/aplicar_atc_tabla_oms.py

Parsea una tabla HTML del índice completo de códigos ATC (nivel 4/5, el más
específico) y completa el campo "atc" de data/info-adicional/info_adicional.json
para medicamentos que todavía no tienen ningún dato.

A diferencia de aplicar_atc_manual.py (que aplica filas curadas a mano una
por una), este script cubre de un saque cualquier principio activo cuyo
nombre aparezca EXACTAMENTE UNA VEZ en toda la tabla ATC (sin ambigüedad).
Si un nombre aparece bajo dos o más códigos distintos (ej. "clorhexidina",
que tiene 8 códigos según la vía/forma), NO se aplica — no hay forma de
saber cuál corresponde sin mirar la forma farmacéutica del producto, y
completar a ciegas ahí sería adivinar, no inferir.

Solo completa "atc". La tabla ATC no trae "clases_terapeuticas" (esa es
una taxonomía propia de AlfaBeta, no de la OMS) -- ese campo queda como
estaba.

Cobertura: solo composiciones de UN SOLO token (principio activo simple).
Los combos no se intentan acá, porque el ATC de una combinación específica
no siempre es la simple concatenación de los ATC individuales (a veces la
OMS le da su propio código a la combinación, a veces no existe ninguno).

Uso:
    python3 scripts/aplicar_atc_tabla_oms.py [--html RUTA] [--dry-run]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enriquecer_info_adicional_por_droga as consenso  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HTML_PATH_DEFAULT = RAIZ / "data" / "info-adicional" / "tabla_atc.html"

PATRON_PAR = re.compile(
    r'<div class="StrCodigo4">([^<]+)</div><div class="StrDesc4">([^<]+)</div>'
)
DESCRIPCIONES_NO_MATCHEABLES = {"combinaciones", "otros", "asociaciones", "otras"}

# Correcciones verificadas a mano sobre la tabla ATC. La tabla no es
# infalible (viene de un scrape externo, aparenta ser una revisión vieja
# del índice ATC de la OMS): esto se detectó comparando contra fuentes
# oficiales (PR Vademécum España, WHO ATC/DDD Index) cuando el código de
# la tabla no encajaba con el grupo terapéutico real o estaba desactualizado.
#
# - ponatinib: la tabla trae L01XC24 (grupo de anticuerpos monoclonales,
#   donde vive trastuzumab) pero ponatinib es un inhibidor de
#   tirosinquinasa de molécula pequeña, no un anticuerpo — el código
#   correcto es L01XE24, confirmado contra prvademecum.es.
# - pregabalina / gabapentina: la tabla las clasifica en N03AX
#   (anticonvulsivantes), la clasificación vieja. La OMS les dio su propio
#   subgrupo "Gabapentinoides" (N02BF) hace años, reflejando que su uso
#   principal es dolor neuropático, no epilepsia. Confirmado contra el
#   índice oficial WHO ATC/DDD (atcddd.fhi.no).
CORRECCIONES_MANUALES = {
    "ponatinib": "L01XE24",
    "pregabalina": "N02BF02",
    "gabapentina": "N02BF01",
}

# Familias de código que la tabla sistemáticamente tiene desactualizadas
# (confirmado cruzando contra ~5100 códigos ya conocidos: 405 discrepancias,
# la mitad de ellas con la tabla proponiendo un código bajo este prefijo en
# vez del subgrupo específico más nuevo al que la OMS reclasificó esas
# drogas — sobre todo inhibidores de tirosinquinasa oncológicos). Se
# excluyen del todo en vez de aplicarlas mal: no hay forma de saber, sin
# revisar cada una a mano, a qué subgrupo nuevo corresponde cada una.
PREFIJOS_DESACTUALIZADOS = ("L01X",)


def parsear_tabla(html_path):
    """Devuelve lista de (codigo, descripcion) tal como aparecen en la tabla."""
    html = html_path.read_text(encoding="utf-8")
    return PATRON_PAR.findall(html)


def construir_mapa_no_ambiguo(pares):
    """
    pares: lista de (codigo, descripcion).
    Devuelve (mapa, ambiguos) donde mapa es nombre_normalizado -> codigo,
    SOLO para nombres que aparecen bajo un único código en toda la tabla.
    ambiguos es el set de nombres normalizados descartados por ambigüedad
    (más de un código para el mismo nombre), para reportar.
    """
    por_nombre = {}
    for codigo, desc in pares:
        desc_limpia = desc.strip().lower()
        if desc_limpia in DESCRIPCIONES_NO_MATCHEABLES:
            continue
        nombre = consenso._normalizar_droga(desc)
        if not nombre:
            continue
        por_nombre.setdefault(nombre, set()).add(codigo)

    mapa = {}
    ambiguos = set()
    for nombre, codigos in por_nombre.items():
        if len(codigos) == 1:
            codigo = next(iter(codigos))
            if codigo.startswith(PREFIJOS_DESACTUALIZADOS):
                ambiguos.add(nombre)  # tratado igual que ambiguo: no se aplica
                continue
            mapa[nombre] = codigo
        else:
            ambiguos.add(nombre)

    for nombre, codigo_correcto in CORRECCIONES_MANUALES.items():
        mapa[nombre] = codigo_correcto
        ambiguos.discard(nombre)

    return mapa, ambiguos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", default=str(HTML_PATH_DEFAULT),
                         help="Ruta a la tabla HTML de códigos ATC")
    parser.add_argument("--dry-run", action="store_true",
                         help="No escribe el archivo, solo muestra el resumen.")
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        print(f"ERROR: no existe {html_path}")
        return 1

    pares = parsear_tabla(html_path)
    mapa, ambiguos = construir_mapa_no_ambiguo(pares)

    medicamentos = consenso._cargar_medicamentos()
    info_adicional = json.loads(consenso.INFO_ADICIONAL_PATH.read_text(encoding="utf-8"))

    cobertura_antes = sum(1 for m in medicamentos if consenso._hash_medicamento(m) in info_adicional)

    agregados = 0
    saltados_por_combo = 0
    saltados_por_ambiguedad = 0
    droga_ambigua_afectada = Counter()

    for m in medicamentos:
        h = consenso._hash_medicamento(m)
        if h in info_adicional:
            continue
        tokens = consenso._tokens_composicion(m.get("droga"))
        if not tokens:
            continue
        if len(tokens) > 1:
            saltados_por_combo += 1
            continue
        nombre = next(iter(tokens))
        if nombre in ambiguos:
            saltados_por_ambiguedad += 1
            droga_ambigua_afectada[nombre] += 1
            continue
        codigo = mapa.get(nombre)
        if not codigo:
            continue
        info_adicional[h] = {
            "drogas": m.get("droga"),
            "atc": codigo,
            "clases_terapeuticas": None,
            "fuente": "tabla_atc_oms",
        }
        agregados += 1

    cobertura_despues = cobertura_antes + agregados

    print(f"Pares código/descripción en la tabla:     {len(pares)}")
    print(f"Nombres únicos no ambiguos (1 solo código): {len(mapa)}")
    print(f"Nombres ambiguos descartados (2+ códigos):  {len(ambiguos)}")
    print(f"Medicamentos totales:                       {len(medicamentos)}")
    print(f"Cobertura antes:                             {cobertura_antes} "
          f"({100 * cobertura_antes / len(medicamentos):.1f}%)")
    print(f"Agregados por tabla ATC (solo ATC, sin clase): {agregados}")
    print(f"Saltados por ser combo (2+ principios):      {saltados_por_combo}")
    print(f"Saltados por nombre ambiguo:                 {saltados_por_ambiguedad}")
    print(f"Cobertura después:                           {cobertura_despues} "
          f"({100 * cobertura_despues / len(medicamentos):.1f}%)")

    if droga_ambigua_afectada:
        print("\nTop nombres ambiguos que más productos afectan (no se completaron):")
        for nombre, n in droga_ambigua_afectada.most_common(10):
            print(f"  {n:4d}  {nombre}")

    if args.dry_run:
        print("\n--dry-run: no se escribió nada.")
        return 0

    consenso.INFO_ADICIONAL_PATH.write_text(
        json.dumps(info_adicional, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"\nEscrito: {consenso.INFO_ADICIONAL_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""etl/presentacion.py - Extraccion, parseo y debug de presentaciones de medicamentos."""

import re
from datetime import datetime

from .config import PRES_DEBUG_PATH, AR_TZ


# ─────────────────────────────────────────────────────────────────────────────
# EXTRACCIÓN DE PRESENTACIÓN DESDE MARCA FUSIONADA
# ─────────────────────────────────────────────────────────────────────────────

# Cuando presentacion está vacía y la marca contiene el nombre comercial
# seguido de la presentación sin separador explícito, este regex detecta
# el punto de corte: dosis numérica o forma farmacéutica conocida.
#
# Ejemplo:
#   "ALLOPURINOL 300 CRAVERI 300 MG COMP.X 60"
#   → marca: "ALLOPURINOL 300 CRAVERI"  presentacion: "300 mg comp.x 60"
#
# No resuelve los casos donde la marca desapareció completamente
# (ej: "COMP.X 30") ni las fusiones droga+marca sin separador.

_FORMAS_FARM = (
    r'COMP|CAPS|CÁPS|CR|GTS|JBE|SOL|SUSP|UNG|GEL|AER|INY|F\.A|LIOF|POMO'
    r'|SOB|OV|GRAG|ENV|COLIRIO|COLIRO|EMULS|AEROSOL'
    r'|BOLSA|VIAL|SPRAY|ESPUMA|LACA|POUCH|JALEA|POTE|FCO|TOALLITAS'
    r'|PCOMP'   # TRB-Pharma: "TRB PCOMP.rec.x 30" donde P precede COMP
)

_RE_EXTRAER_PRES = re.compile(
    r'^(.+?)\s+(\d[\d,./]*\s*(?:MG|MCG|G\b|ML|UI|%|U\b).*'
    r'|(?:' + _FORMAS_FARM + r')[\.\s].+)$',
    re.IGNORECASE
)


def _build_re_lab_pegado(medicamentos: list):
    """
    Construye un regex que detecta cuando un laboratorio conocido (de los
    que YA aparecen correctamente en el campo 'laboratorio' de otros
    registros del propio dataset) quedó pegado SIN espacio a la dosis o
    forma que le sigue dentro del campo 'marca'.

    Caso real (laboratorios que venden genéricos sin marca de fantasía,
    usando "DROGA LABORATORIO" como descripción comercial):
        "BICALUTAMIDA TECHSPHERE50 mg comp.x 30"
        "CARBOPLATINO MICROSULES150 mg iny.f.a.x 1"
        "LEVOMEPROMAZINA VANNIER25 mg comp.x 30"

    Sin este separador, _RE_EXTRAER_PRES se traga la dosis dentro de la
    marca (ej: marca="BICALUTAMIDA TECHSPHERE50 mg" en vez de
    "BICALUTAMIDA TECHSPHERE"), porque el \\s* antes de la unidad es
    opcional y el dígito pegado al laboratorio parece el inicio de la
    dosis igual.

    Se usa solo la ÚLTIMA PALABRA significativa de cada laboratorio
    conocido (no el nombre completo), porque es esa la que queda pegada
    a la dosis en el campo 'marca' — el PDF nunca repite ahí el nombre
    completo del laboratorio. Ej: laboratorio="Delta Farma" pero en la
    marca aparece "...DELTA FARMA500 mg..." (la dosis pegada a "FARMA",
    la última palabra, no a "DELTA"). También se ignoran sufijos
    legales/societarios cortos o puntuados (Arg., S.A.U., (PH), etc.)
    que tampoco se repiten ahí. Se exige un mínimo de 4 caracteres para
    evitar matches espurios con palabras cortas.

    El índice se construye desde el propio dataset (mismo patrón que
    usa rescatar_laboratorios()), no es una lista hardcodeada aparte.
    """
    ultimas_palabras = set()
    for m in medicamentos:
        lab = (m.get('laboratorio') or '').strip()
        if lab in ('', 'Desconocido'):
            continue
        palabras = [p for p in lab.split() if re.match(r'^[A-Za-zÁÉÍÓÚÑáéíóúñ]+$', p)]
        if palabras:
            ultima = palabras[-1]
            if len(ultima) >= 4:
                ultimas_palabras.add(ultima)

    if not ultimas_palabras:
        return None
    labs_validos = sorted(ultimas_palabras, key=len, reverse=True)
    patron_labs = '|'.join(re.escape(lab) for lab in labs_validos)
    # Un laboratorio conocido seguido directamente (sin espacio) de un
    # DÍGITO. Se exige dígito (no letra) a propósito: un lookahead más
    # laxo (cualquier letra) generaba falsos positivos graves en marcas
    # de fantasía que contienen el nombre de un laboratorio como
    # substring por coincidencia, ej. "RAFFOLUTIL" (contiene "Raffo",
    # laboratorio real) se partía en "RAFFO LUTIL" sin que hubiera
    # ningún pegado real que arreglar. Los pocos casos de forma
    # abreviada en mayúscula pegada sin dígito de por medio (ej.
    # "VANNIERAd.gts.x 20 ml") quedan fuera de este fix puntual.
    return re.compile(r'\b(' + patron_labs + r')(?=\d)', re.IGNORECASE)


# Separa formas farmacéuticas pegadas sin espacio al texto previo.
# "NUTRIFLEX OMEGA ESPECIALbolsa x 1250 ml" -> "NUTRIFLEX OMEGA ESPECIAL bolsa x 1250 ml"
_RE_FORMA_PEGADA = re.compile(
    r'(?<=[A-ZÁÉÍÓÚÑa-záéíóúñ])'
    r'(bolsa|vial|spray|espuma|laca|pouch|jalea|pote|fco|toallitas|gel'
    r'|comp\.|caps\.|cáps\.|cr\.|gts\.|jbe\.|sol\.|susp\.|iny\.|aer\.)'
    r'(?=[\sx\d])',
    re.IGNORECASE,
)

# Detecta el patrón TOKEN_MAYUSC + mismoToken_minus (ej. GELgel, BOLSAbolsa)
# para eliminar el duplicado en mayúsculas antes de insertar el espacio.
_RE_TOKEN_DUPLICADO = re.compile(
    r'\b(BOLSA|VIAL|SPRAY|ESPUMA|LACA|POUCH|JALEA|POTE|FCO|GEL)'
    r'(?=\1)',   # lookahead: mismo token inmediatamente después (case-insensitive handled below)
    re.IGNORECASE,
)


def separar_lab_pegado_de_marca(marca: str, re_lab_pegado) -> str:
    """
    Inserta un espacio entre un laboratorio conocido y la dosis/forma
    que le sigue sin separación, y también entre texto y formas
    farmacéuticas pegadas sin espacio.

    "BICALUTAMIDA TECHSPHERE50 mg comp.x 30"
        -> "BICALUTAMIDA TECHSPHERE 50 mg comp.x 30"
    "NUTRIFLEX OMEGA ESPECIALbolsa x 1250 ml"
        -> "NUTRIFLEX OMEGA ESPECIAL bolsa x 1250 ml"
    """
    nueva = _RE_TOKEN_DUPLICADO.sub('', marca)  # eliminar GELgel → gel, BOLSAbolsa → bolsa
    nueva = _RE_FORMA_PEGADA.sub(lambda m: ' ' + m.group(1), nueva)
    if re_lab_pegado is None:
        return nueva
    return re_lab_pegado.sub(lambda m: m.group(1) + ' ', nueva)


def extraer_presentacion_de_marca(medicamentos: list, re_lab_pegado=None) -> tuple:
    """
    Para registros con presentacion vacía, intenta extraer la presentacion
    desde el campo marca cuando ambos campos quedaron fusionados.

    Antes de aplicar el regex de corte, separa los casos donde un
    laboratorio conocido quedó pegado sin espacio a la dosis/forma
    siguiente (ver separar_lab_pegado_de_marca), para que el corte caiga
    en el lugar correcto y no se trague la dosis dentro de la marca.

    Solo actúa cuando el nombre resultante tiene al menos 3 caracteres
    y no empieza con dígito (descarta falsos positivos).

    re_lab_pegado: regex precompilado (ver _build_re_lab_pegado). Si no
    se pasa, se construye acá — se acepta como parámetro para poder
    reutilizar el mismo regex entre esta función y
    limpiar_dosis_residual_en_marca() sin reconstruirlo dos veces sobre
    el dataset completo (ambas dependen solo del campo 'laboratorio',
    que ninguna de las dos modifica).

    Retorna el dataset corregido y la cantidad de registros reparados.
    """
    if re_lab_pegado is None:
        re_lab_pegado = _build_re_lab_pegado(medicamentos)

    reparados = 0
    for m in medicamentos:
        if (m.get("presentacion") or "").strip():
            continue
        if m.get("laboratorio") in ("Desconocido", ""):
            continue

        marca = (m.get("marca") or "").strip()
        marca = separar_lab_pegado_de_marca(marca, re_lab_pegado)
        match = _RE_EXTRAER_PRES.match(marca)
        if match:
            nombre = match.group(1).strip()
            pres   = match.group(2).strip().lower()
            if len(nombre) >= 3 and not nombre[0].isdigit():
                m["marca"]        = nombre
                m["presentacion"] = pres
                reparados += 1

    return medicamentos, reparados


_RE_DOSIS_RESIDUAL = re.compile(
    r'\s+\d[\d,./]*\s*(?:MG|MCG|G|ML|UI|%|U)\b.*$',
    re.IGNORECASE
)


def limpiar_dosis_residual_en_marca(medicamentos: list, re_lab_pegado=None) -> tuple:
    """
    Limpia el residuo de dosis que queda pegado a un laboratorio dentro
    de 'marca' incluso cuando 'presentacion' YA tiene contenido (por eso
    es una pasada aparte de extraer_presentacion_de_marca, que sólo
    actúa con presentacion vacía).

    Ocurre cuando otra capa (ej. reparar_presentacion_desplazada) separó
    correctamente la FORMA hacia 'presentacion' pero dejó la DOSIS
    pegada al laboratorio en 'marca':
        marca="CIPROFLOXACINA SANT GALL500 MG"  presentacion="comp.x 10"
        -> marca="CIPROFLOXACINA SANT GALL"     presentacion sin tocar

    Solo actúa cuando, tras separar el laboratorio pegado (mismo
    mecanismo que separar_lab_pegado_de_marca), el residuo eliminado es
    puramente una dosis numérica al final de la marca — nunca toca
    marcas que terminan en dosis por motivos propios sin laboratorio
    pegado de por medio, para no arriesgar falsos positivos.

    re_lab_pegado: regex precompilado (ver _build_re_lab_pegado). Si no
    se pasa, se construye acá — ver nota en extraer_presentacion_de_marca().

    Retorna el dataset corregido y la cantidad de registros reparados.
    """
    if re_lab_pegado is None:
        re_lab_pegado = _build_re_lab_pegado(medicamentos)
    if re_lab_pegado is None:
        return medicamentos, 0

    reparados = 0
    for m in medicamentos:
        marca = (m.get("marca") or "").strip()
        if not marca:
            continue

        separada = separar_lab_pegado_de_marca(marca, re_lab_pegado)
        if separada == marca:
            continue  # no había laboratorio pegado a un dígito

        # Tras separar, si lo que queda después del laboratorio es
        # exclusivamente una dosis (no una forma farmacéutica completa
        # ni texto adicional con letras no numéricas), se recorta.
        sin_dosis = _RE_DOSIS_RESIDUAL.sub('', separada).strip()
        if sin_dosis != separada and len(sin_dosis) >= 3:
            m["marca"] = sin_dosis
            reparados += 1

    return medicamentos, reparados


# ─────────────────────────────────────────────────────────────────────────────
# PARSER DE PRESENTACIONES (debug CSV)
# ─────────────────────────────────────────────────────────────────────────────

_FORMAS_NORM_PRES = {
    'comp.rec.ran': 'COMPRIMIDOS RECUBIERTOS RANURADOS',
    'comp.rec.gast': 'COMPRIMIDOS GASTRORRESISTENTES',
    'comp.rec.lib.prol': 'COMPRIMIDOS LIBERACIÓN PROLONGADA RECUBIERTOS',
    'comp.rec.acc.prol': 'COMPRIMIDOS ACCIÓN PROLONGADA RECUBIERTOS',
    'comp.rec.ap': 'COMPRIMIDOS ACCIÓN PROLONGADA RECUBIERTOS',
    'comp.lib.prol': 'COMPRIMIDOS LIBERACIÓN PROLONGADA',
    'comp.lib.cont': 'COMPRIMIDOS LIBERACIÓN CONTROLADA',
    'comp.lib.contr': 'COMPRIMIDOS LIBERACIÓN CONTROLADA',
    'comp.lib.modif': 'COMPRIMIDOS LIBERACIÓN MODIFICADA',
    'comp.rec': 'COMPRIMIDOS RECUBIERTOS',
    'comp. rec': 'COMPRIMIDOS RECUBIERTOS',
    'comp.ran': 'COMPRIMIDOS RANURADOS',
    'comp.ranur': 'COMPRIMIDOS RANURADOS',
    'comp.birranur': 'COMPRIMIDOS BIRRANURADOS',
    'comp.birran': 'COMPRIMIDOS BIRRANURADOS',
    'comp.trirran': 'COMPRIMIDOS TRIRRANURADOS',
    'comp.subl': 'COMPRIMIDOS SUBLINGUALES',
    'comp.mast': 'COMPRIMIDOS MASTICABLES',
    'comp.efer': 'COMPRIMIDOS EFERVESCENTES',
    'comp.ef': 'COMPRIMIDOS EFERVESCENTES',
    'comp.dispers': 'COMPRIMIDOS DISPERSABLES',
    'comp.acc.prol': 'COMPRIMIDOS ACCIÓN PROLONGADA',
    'comp.ap': 'COMPRIMIDOS ACCIÓN PROLONGADA',
    'comp': 'COMPRIMIDOS',
    'cáps.blandas': 'CÁPSULAS BLANDAS', 'caps.blandas': 'CÁPSULAS BLANDAS',
    'cáps.duras': 'CÁPSULAS DURAS', 'caps.duras': 'CÁPSULAS DURAS',
    'cáps.bl': 'CÁPSULAS BLANDAS', 'caps.bl': 'CÁPSULAS BLANDAS',
    'cáps. bl': 'CÁPSULAS BLANDAS', 'caps. bl': 'CÁPSULAS BLANDAS',
    'cáps.lib.cont': 'CÁPSULAS LIBERACIÓN CONTROLADA',
    'cáps.lib.contr': 'CÁPSULAS LIBERACIÓN CONTROLADA',
    'caps.lib.cont': 'CÁPSULAS LIBERACIÓN CONTROLADA',
    'cáps.lib.prol': 'CÁPSULAS LIBERACIÓN PROLONGADA',
    'caps.lib.prol': 'CÁPSULAS LIBERACIÓN PROLONGADA',
    'cáps.p/inhalar': 'CÁPSULAS PARA INHALACIÓN',
    'cáps.p/inh': 'CÁPSULAS PARA INHALACIÓN',
    'caps.p/inh': 'CÁPSULAS PARA INHALACIÓN',
    'cáps': 'CÁPSULAS', 'caps': 'CÁPSULAS',
    'iny.liof': 'INYECTABLE LIOFILIZADO',
    'iny.f.a': 'INYECTABLE FRASCO AMPOLLA',
    'iny.a': 'INYECTABLE AMPOLLA',
    'iny': 'INYECTABLE',
    'liof.f.a': 'LIOFILIZADO FRASCO AMPOLLA',
    'f.a.liof': 'FRASCO AMPOLLA LIOFILIZADO',
    'liof': 'LIOFILIZADO',
    'f.a': 'FRASCO AMPOLLA',
    'fco.a': 'FRASCO AMPOLLA', 'fco.gotero': 'FRASCO GOTERO', 'fco': 'FRASCO',
    'a.': 'AMPOLLA', 'a': 'AMPOLLA', 'amp': 'AMPOLLA',
    'vial': 'VIAL', 'bolsa': 'BOLSA',
    'jga.prell': 'JERINGA PRELLENADA', 'lap.prell': 'LAPICERA PRELLENADA',
    'jga': 'JERINGA', 'autoinyector': 'AUTOINYECTOR', 'autoin': 'AUTOINYECTOR',
    'lap': 'LAPICERA', 'pluma': 'LAPICERA', 'env': 'ENVASE',
    'sol.oft': 'SOLUCIÓN OFTÁLMICA', 'sol.of': 'SOLUCIÓN OFTÁLMICA',
    'sol.oral': 'SOLUCIÓN ORAL', 'sol. oral': 'SOLUCIÓN ORAL',
    'sol.top': 'SOLUCIÓN TÓPICA', 'sol.tópica': 'SOLUCIÓN TÓPICA',
    'sol.neb': 'SOLUCIÓN NEBULIZABLE', 'sol.p/neb': 'SOLUCIÓN NEBULIZABLE',
    'sol.p/nebulizar': 'SOLUCIÓN NEBULIZABLE', 'sol.iny': 'SOLUCIÓN INYECTABLE',
    'sol': 'SOLUCIÓN',
    'susp.oral': 'SUSPENSIÓN ORAL', 'susp.nasal': 'SUSPENSIÓN NASAL', 'susp': 'SUSPENSIÓN',
    'jbe': 'JARABE', 'jarabe': 'JARABE', 'liq': 'LÍQUIDO', 'elixir': 'ELIXIR',
    'gts.oft': 'GOTAS OFTÁLMICAS', 'gts.óticas': 'GOTAS ÓTICAS',
    'gts.ót': 'GOTAS ÓTICAS', 'gts.nas': 'GOTAS NASALES', 'gts': 'GOTAS',
    'colirio': 'COLIRIO',
    'cr.dérmica': 'CREMA DÉRMICA', 'cr.dérm': 'CREMA DÉRMICA', 'cr': 'CREMA',
    'gel': 'GEL', 'ung': 'UNGÜENTO', 'pomo': 'POMO', 'jalea': 'JALEA',
    'lot': 'LOCIÓN', 'loc': 'LOCIÓN', 'emuls': 'EMULSIÓN',
    'xamp': 'CHAMPÚ', 'shamp': 'CHAMPÚ',
    'roll-on': 'ROLL-ON', 'parche': 'PARCHE',
    'aer.bronq': 'AEROSOL BRONQUIAL', 'aer': 'AEROSOL', 'aerosol': 'AEROSOL',
    'inhal': 'INHALADOR', 'spray': 'SPRAY', 'nasal': 'SPRAY NASAL', 'puff': 'PUFF',
    'ov.vag': 'ÓVULOS VAGINALES', 'óv.vag': 'ÓVULOS VAGINALES',
    'óv': 'ÓVULOS', 'ov': 'ÓVULOS', 'sup': 'SUPOSITORIOS',
    'polv.p/susp.oral': 'POLVO PARA SUSPENSIÓN ORAL',
    'polv.p/susp': 'POLVO PARA SUSPENSIÓN', 'polv.p/sol': 'POLVO PARA SOLUCIÓN',
    'pvo.p/susp': 'POLVO PARA SUSPENSIÓN', 'pvo.sob': 'POLVO SOBRES',
    'pvo': 'POLVO', 'polv': 'POLVO',
    'gran.sob': 'GRÁNULOS SOBRES', 'gran': 'GRÁNULOS',
    'blist.grag': 'BLÍSTER GRAGEAS', 'blist': 'BLÍSTER',
    'sob': 'SOBRES', 'sobre': 'SOBRES', 'sobres': 'SOBRES', 'sachet': 'SOBRES',
    'pouch': 'POUCH', 'kit': 'KIT',
    'grag': 'GRAGEAS', 'tab': 'TABLETAS', 'caram': 'CARAMELOS', 'film': 'FILM',
    # Formas adicionales no mapeadas previamente
    'caplets': 'TABLETAS',
    'laca': 'LACA',
    'laq': 'LACA',
    'espuma': 'ESPUMA',
    'espuma rectal': 'ESPUMA RECTAL',
    'expend.sob': 'SOBRES EXPENDEDOR',
    'pvo.liof': 'POLVO LIOFILIZADO',
    'pvo.vial': 'POLVO VIAL',
    'jer.prell': 'JERINGA PRELLENADA',
    'jer.pr': 'JERINGA PRELLENADA',
    'jga.pr': 'JERINGA PRELLENADA',
    'sol.f.a': 'SOLUCIÓN FRASCO AMPOLLA',
    'iny.sol': 'SOLUCIÓN INYECTABLE',
    'iv': 'INYECTABLE INTRAVENOSO',
    'tab.dis.inst': 'TABLETAS DISPERSABLES DE DISOLUCIÓN INSTANTÁNEA',
    'tab.disp': 'TABLETAS DISPERSABLES',
    'dis.inst': 'DISOLUCIÓN INSTANTÁNEA',
    'comp.gastr': 'COMPRIMIDOS GASTRORRESISTENTES',
    'comp.laq': 'COMPRIMIDOS LACADOS',
    'comp.rapirtd': 'COMPRIMIDOS LIBERACIÓN RÁPIDA',
    'comp.divis': 'COMPRIMIDOS DIVISIBLES',
    'comp.divids': 'COMPRIMIDOS DIVISIBLES',
    'comp.ran.divids': 'COMPRIMIDOS RANURADOS DIVISIBLES',
    'caps.bl.gastr': 'CÁPSULAS BLANDAS GASTRORRESISTENTES',
    'cáps.bl.gastr': 'CÁPSULAS BLANDAS GASTRORRESISTENTES',
    'sol.oft.esteril': 'SOLUCIÓN OFTÁLMICA ESTÉRIL',
    'sol.oft.estéril': 'SOLUCIÓN OFTÁLMICA ESTÉRIL',
    'fco.vial': 'FRASCO VIAL',
    'iny.vial': 'INYECTABLE VIAL',
    'liof.pvo.vial': 'LIOFILIZADO POLVO VIAL',
    'd.jbe': 'JARABE',
    # Formas vaginales
    'vaginal':           'VAGINAL',
    'caps.vag':          'CÁPSULAS VAGINALES',
    'cap.vag':           'CÁPSULAS VAGINALES',
    'caps.blandas vag':  'CÁPSULAS BLANDAS VAGINALES',
    'caps.bl.vag':       'CÁPSULAS BLANDAS VAGINALES',
    'comp.vag':          'COMPRIMIDOS VAGINALES',
    'tab.vag':           'TABLETAS VAGINALES',
    'ovulo':             'ÓVULO',
    'ovulos':            'ÓVULOS',
    'ovul':              'ÓVULO',
    'crema vag':         'CREMA VAGINAL',
    'cr.vag':            'CREMA VAGINAL',
    'gel vag':           'GEL VAGINAL',
    'sol.vag':           'SOLUCIÓN VAGINAL',
    # Formas añadidas en fix /ml+forma y nuevas (2026-06)
    'tabl':              'TABLETAS',
    'tabs':              'TABLETAS',
    'lapic.prell':       'LAPICERA PRELLENADA',
    'lapic':             'LAPICERA',
    'lapiceras prell':   'LAPICERAS PRELLENADAS',
    'lapiceras':         'LAPICERAS',
    'lapicera desc':     'LAPICERA DESCARTABLE',
    'lapicera':          'LAPICERA',
    'autoiny':           'AUTOINYECTOR',
    'autoinyect':        'AUTOINYECTOR',
    'autoinyec':         'AUTOINYECTOR',
    'autoinyect.prell':  'AUTOINYECTOR PRELLENADO',
    'cart':              'CARTUCHO',
    'cart.prell':        'CARTUCHO PRELLENADO',
    'cartucho':          'CARTUCHO',
    'depot':             'DEPÓSITO',
    'viales':            'VIALES',
    'apos':              'APÓSITO',
    'jab.liq':           'JABÓN LÍQUIDO',
    'jab.sol':           'JABÓN SÓLIDO',
    'inhalador hfa':     'INHALADOR HFA',
    'inh':               'INHALADOR',
    'spr.nasal':         'SPRAY NASAL',
    'spr':               'SPRAY',
    'sh':                'SHAMPOO',
    'shampoo':           'SHAMPOO',
    'pda':               'POMADA',
    'emul':              'EMULSIÓN',
    'emulsión':          'EMULSIÓN',
    'monods':            'MONODOSIS',
    'monodosis':         'MONODOSIS',
    'pomos':             'POMOS',
    'blis':              'BLÍSTER',
    'blister':           'BLÍSTER',
    'dispensador':       'DISPENSADOR',
    'dispenser':         'DISPENSADOR',
    'colir':             'COLIRIO',
    'granul.lp sob':     'GRÁNULOS LP SOBRES',
    'granul':            'GRÁNULOS',
    'divids':            'DIVISIBLES',
    'jgas.prell':        'JERINGAS PRELLENADAS',
    'j.prell':           'JERINGA PRELLENADA',
    'iny.prell':         'INYECTABLE PRELLENADO',
    'iny.a.ol':          'INYECTABLE OLEOSO',
    'parch.matriz':      'PARCHE MATRICIAL',
    'parch.transd':      'PARCHE TRANSDÉRMICO',
    'parches transdérmicos': 'PARCHES TRANSDÉRMICOS',
    'cap.lib.prol':      'CÁPSULAS LIBERACIÓN PROLONGADA',
    'ap.aplic.desc':     'APLICADOR DESCARTABLE',
    # Formas faltantes detectadas en debug (2024-06)
    'champu': 'CHAMPÚ',
    'sachets': 'SOBRES',
    'implante': 'IMPLANTE',
    'pasta': 'PASTA',
    'polvo': 'POLVO',
    'talquera': 'TALQUERA',
    'esp': 'ESPUMA',
    'got': 'GOTAS',
    'got.': 'GOTAS',
    'gotero incoloro': 'FRASCO GOTERO',
    'locion atomizador': 'LOCIÓN ATOMIZADOR',
    'pomada dérm': 'POMADA DÉRMICA',
    'pomada': 'POMADA',
    'tubos': 'TUBOS',
    'implante oft.intravítrea': 'IMPLANTE OFTÁLMICO INTRAVÍTREO',
    'gtas': 'GOTAS',
    'gotas': 'GOTAS',
    'pote': 'POTE',
    'colut': 'COLUTORIO',
    'past': 'PASTILLAS',
    'pastillas': 'PASTILLAS',
    'soluc': 'SOLUCIÓN',
    'parches': 'PARCHES',
    'caramelos': 'CARAMELOS',
    'blister caram': 'BLÍSTER CARAMELOS',
    'pasta dérm': 'PASTA DÉRMICA',
    'pasta derm': 'PASTA DÉRMICA',
    'unidosis': 'UNIDOSIS',
    'toallitas desc': 'TOALLITAS DESCARTABLES',
    'toallitas': 'TOALLITAS',
    'sistemas': 'SISTEMAS',
    'estuche': 'ESTUCHE',
    'frasco': 'FRASCO',
    'efer.gran.sob': 'GRÁNULOS EFERVESCENTES SOBRES',
    'gran.efer.sob': 'GRÁNULOS EFERVESCENTES SOBRES',
    'anillo vaginal sob': 'ANILLO VAGINAL SOBRES',
    'anillo vaginal': 'ANILLO VAGINAL',
    'crema': 'CREMA',
}

_MODS_PRES = {
    'oft':      {'sol': 'SOLUCIÓN OFTÁLMICA',  'gts': 'GOTAS OFTÁLMICAS',  None: 'OFTÁLMICO'},
    'of':       {'sol': 'SOLUCIÓN OFTÁLMICA',  'gts': 'GOTAS OFTÁLMICAS',  None: 'OFTÁLMICO'},
    'oral':     {'sol': 'SOLUCIÓN ORAL', 'susp': 'SUSPENSIÓN ORAL',        None: 'ORAL'},
    'vag':      {'ov': 'ÓVULOS VAGINALES', 'óv': 'ÓVULOS VAGINALES', 'cr': 'CREMA VAGINAL', None: 'VAGINAL'},
    'nasal':    {'susp': 'SUSPENSIÓN NASAL', 'sol': 'SOLUCIÓN NASAL', 'spray': 'SPRAY NASAL', None: 'SPRAY NASAL'},
    'liof':     {'f.a': 'FRASCO AMPOLLA LIOFILIZADO', None: 'LIOFILIZADO'},
    'f.a':      {'iny': 'INYECTABLE FRASCO AMPOLLA', 'liof': 'LIOFILIZADO FRASCO AMPOLLA', None: 'FRASCO AMPOLLA'},
    'gotero':   {'fco': 'FRASCO GOTERO', None: 'FRASCO GOTERO'},
    'rec':      {'comp': 'COMPRIMIDOS RECUBIERTOS', None: 'RECUBIERTO'},
    'acc.prol': {'comp': 'COMPRIMIDOS ACCIÓN PROLONGADA', None: 'ACCIÓN PROLONGADA'},
    'ap':       {'comp': 'COMPRIMIDOS ACCIÓN PROLONGADA', None: 'ACCIÓN PROLONGADA'},
    'prell':    {'lap': 'LAPICERA PRELLENADA', 'jga': 'JERINGA PRELLENADA', None: 'PRELLENADO'},
    'duras':    {'cáps': 'CÁPSULAS DURAS', 'caps': 'CÁPSULAS DURAS', None: None},
    'ur': {None: None}, 'andas': {None: None}, 'solv': {None: None},
    's': {None: None}, 't': {None: None}, 'r': {None: None}, 'er': {None: None},
}

_RE_PP  = re.compile(r'^(?:ad|ped|rtd|hm|ap)\.?\s+', re.IGNORECASE)
# Prefijos que modifican la forma (se conservan como sufijo de forma)
_RE_PM  = re.compile(r'^(sr|lp|xr|er|mr|flash|niños|naranja|menta|frutal|clásico|clasico|vainilla|frutilla|tutti\s*frutti|limón|limon|forte|plus|duo|max)\s+', re.IGNORECASE)
_MODS_FORMA = {
    'sr': 'SR', 'lp': 'LP', 'xr': 'XR', 'er': 'ER', 'mr': 'MR',
    'flash': 'FLASH', 'niños': 'NIÑOS', 'forte': 'FORTE', 'plus': 'PLUS',
    'duo': 'DUO', 'max': 'MAX',
}
_RE_PD  = re.compile(r'^(\d[\d\.,/]*)\s*')
_RE_PU  = re.compile(r'^(mg|mcg|ug|g\b|ml|ui|iu|meq|mmol|kcal|%)\s*', re.IGNORECASE)
_RE_PPR = re.compile(r'^(?:hfa|cfc|/\d*\.?\d*(?:ml|h|24h))\s*', re.IGNORECASE)
_RE_PC  = re.compile(r'^(\d[\d\.,]*)\s*(mg|mcg|g)\s*/\s*(\d[\d\.,]*)\s*(ml|g)\s*', re.IGNORECASE)
_RE_PCT_MID = re.compile(r'^(.*?)(\d+[\.,]?\d*)\s*%\s+', re.IGNORECASE)   # "gel 0.1% " → dosis=0.1, unidad=%
_RE_CONC_BARE = re.compile(r'^(\d[\d\.,]*)\s*(mg|mcg|g|ui|meq)\s*/\s*(ml|g|dose|dosis|comp|amp)\s*$', re.IGNORECASE)  # "f.a.x 250 mg/ml" tail
_RE_PKV = re.compile(r'x\s*\d[\d\.,]*\s*(ml|g)\b', re.IGNORECASE)
_RE_PCO = re.compile(r'\(\d+\+\d+\)')
_RE_PCA = re.compile(r'x\s*(\d[\d\.,]*)\s*(ds\.?|dosis|ml|g\b|u\.?|unid\.?)?', re.IGNORECASE)
_RE_PAE = re.compile(r'(?:dosis\s+x\s+(\d+)|(\d+)\s+dosis)', re.IGNORECASE)
_formas_pres_re = '|'.join(re.escape(k) for k in sorted(_FORMAS_NORM_PRES.keys(), key=len, reverse=True))
_RE_PF  = re.compile(r'^(' + _formas_pres_re + r')(?=$|[\s\.])[\s\.]?', re.IGNORECASE)
_RE_PFF = re.compile(r'\b(' + _formas_pres_re + r')\.?$', re.IGNORECASE)
_UNI_MAP = {'mg':'MG','mcg':'MCG','ug':'MCG','g':'G','ml':'ML',
            'ui':'UI','iu':'UI','u':'U','meq':'MEQ','mmol':'MMOL','kcal':'KCAL','%':'%'}


def _parsear_presentacion(pres: str) -> dict:
    r = {'forma': None, 'dosis': None, 'unidad': None, 'cantidad': None, 'resto': None}
    s = pres.strip().lower()
    # Capturar modificador de forma antes de strippear prefijos (SR, LP, Flash, Niños, etc.)
    _mod_forma = None
    m_mod = _RE_PM.match(s)
    if m_mod:
        _mod_forma = _MODS_FORMA.get(m_mod.group(1).lower())  # None si es sabor (naranja, menta…)
        s = s[m_mod.end():]
    s = _RE_PP.sub('', s).strip()
    m = _RE_PC.match(s)
    if m:
        r['dosis']  = f"{m.group(1)}{m.group(2)}/{m.group(3)}{m.group(4)}"
        r['unidad'] = 'MG/ML'
        s = s[m.end():]
        # Capturar forma que sigue a la concentración (ej: "0.5 mg/ml a.x 1")
        m2 = _RE_PF.match(s.strip())
        if m2:
            fkr2 = m2.group(1).lower().rstrip('. ')
            r['forma'] = _FORMAS_NORM_PRES.get(fkr2, fkr2.upper())
            s = s[m2.end():]
    else:
        m = _RE_PD.match(s)
        if m:
            r['dosis'] = m.group(1)
            s = s[m.end():]
        m = _RE_PU.match(s)
        if m:
            r['unidad'] = _UNI_MAP.get(m.group(1).lower(), m.group(1).upper())
            s = s[m.end():]
    # Patrón "forma N% x cantidad" → ej: "gel 0.1% x 30 g"
    # El % aparece DESPUÉS de la forma: primero buscamos la forma, luego el %
    if not r['dosis']:
        m = re.search(r'(\d+[\.,]?\d*)\s*%(?:\s+|$)', s)
        if m:
            r['dosis'] = m.group(1).replace(',', '.')
            r['unidad'] = '%'
            s = (s[:m.start()] + s[m.end():]).strip()
    # Patrón "mg/ml" al final sin cantidad previa → ej: "f.a.x 50 mg/ml"
    # Solo aplica si la cantidad ya capturada en realidad era la concentración
    if not r['dosis'] and r['cantidad']:
        m = re.search(r'(mg|mcg|g|ui|meq)\s*/\s*(ml|g)\s*$', s, re.IGNORECASE)
        if m:
            # la cantidad capturada es la dosis, la unidad es mg/ml
            r['dosis']    = r['cantidad']
            r['unidad']   = _UNI_MAP.get(m.group(1).lower(), m.group(1).upper()) + '/' + m.group(2).upper()
            r['cantidad'] = None
    # Caso "x 250 mg/ml" → cantidad fue capturada pero resto contiene la unidad
    if not r['dosis'] and r['cantidad'] and r.get('resto'):
        m = re.match(r'^(mg|mcg|g|ui|meq)\s*/\s*(ml|g)\s*$', (r['resto'] or ''), re.IGNORECASE)
        if m:
            r['dosis']    = r['cantidad']
            r['unidad']   = _UNI_MAP.get(m.group(1).lower(), m.group(1).upper()) + '/' + m.group(2).upper()
            r['cantidad'] = None
            r['resto']    = None
    s = _RE_PPR.sub('', s).strip()
    fkr = None
    m = _RE_PF.match(s.strip())
    if m:
        fkr = m.group(1).lower().rstrip('. ')
        r['forma'] = _FORMAS_NORM_PRES.get(fkr, fkr.upper())
        s = s[m.end():]
    if not r['forma']:
        m = _RE_PFF.search(s.strip())
        if m:
            fk = m.group(1).lower().rstrip('. ')
            r['forma'] = _FORMAS_NORM_PRES.get(fk, fk.upper())
            s = s[:m.start()].strip()
    # Fallback: si hay una palabra descriptiva antes de la forma (ej: "aspirina prev.comp.x 60",
    # "clásico comp.mast.x 6", "mentol gts.x 120 ml") buscar forma en cualquier posición.
    if not r['forma']:
        m = re.search(r'\b(' + _formas_pres_re + r')(?=$|[\s.x])', s, re.IGNORECASE)
        if m:
            fk = m.group(1).lower().rstrip('. ')
            r['forma'] = _FORMAS_NORM_PRES.get(fk, fk.upper())
            # Descartar la parte previa a la forma (es texto descriptivo, no dato útil)
            s = s[m.end():]
    s_sk = _RE_PKV.sub('', s)
    m = _RE_PCA.search(s_sk)
    if m:
        cant = m.group(1)
        uc = (m.group(2) or '').strip().rstrip('.')
        if uc == 'dosis':
            uc = 'ds.'
        r['cantidad'] = (cant + (' ' + uc if uc else '')).strip()
        s = (s_sk[:m.start()] + s_sk[m.end():]).strip(' .,+')
    else:
        s = s_sk
        m = _RE_PAE.search(s)
        if m:
            n = m.group(1) or m.group(2)
            r['cantidad'] = n + ' ds.'
            s = (s[:m.start()] + s[m.end():]).strip(' .,+')
    s = _RE_PCO.sub('', s).strip(' .,+')
    if s and fkr:
        mod = s.strip(' .')
        if mod in _MODS_PRES:
            mapa = _MODS_PRES[mod]
            fr = mapa.get(fkr) or mapa.get(None)
            if fr:
                r['forma'] = fr
                s = ''
            elif mapa.get(None) is None:
                s = ''
    s = s.strip(' .,+-')
    if not r['forma'] and not s and r['cantidad']:
        if r['unidad'] == 'ML':
            r['forma'] = 'LÍQUIDO'
        elif r['unidad'] == 'G':
            r['forma'] = 'TÓPICO'
    # Appendear modificador a la forma si corresponde (SR, LP, Flash, Niños…)
    if _mod_forma and r['forma']:
        r['forma'] = f"{r['forma']} {_mod_forma}"
    if s:
        r['resto'] = s
    # Si el string original contiene 'vial' explícito pero la forma capturada es
    # un modificador (liof, pvo, IV, fco, sol), forzar forma = VIAL
    _FORMAS_VIAL_OVERRIDE = {
        'LIOFILIZADO', 'POLVO LIOFILIZADO', 'POLVO', 'FRASCO',
        'INYECTABLE INTRAVENOSO', 'SOLUCIÓN',
    }
    if (r['forma'] in _FORMAS_VIAL_OVERRIDE and
            re.search(r'\bvial\b', pres.lower())):
        r['forma'] = 'VIAL'
    # Caso "f.a.x 250 mg/ml" → cantidad capturada pero resto es "mg/ml" (la unidad)
    if not r['dosis'] and r['cantidad'] and r.get('resto'):
        m = re.match(r'^(mg|mcg|g|ui|meq)\s*/\s*(ml|g)\s*$', r['resto'], re.IGNORECASE)
        if m:
            r['dosis']    = r['cantidad']
            r['unidad']   = _UNI_MAP.get(m.group(1).lower(), m.group(1).upper()) + '/' + m.group(2).upper()
            r['cantidad'] = None
            r['resto']    = None
    return r


def generar_debug_presentaciones(medicamentos: list) -> None:
    import csv as _csv
    PRES_DEBUG_PATH.parent.mkdir(parents=True, exist_ok=True)
    debug_generado = datetime.now(AR_TZ).strftime("%Y-%m-%d %H:%M:%S")
    campos = ['debug_generado', 'droga', 'marca', 'presentacion_original', 'forma', 'dosis', 'unidad', 'cantidad', 'resto']
    sin_forma = con_resto = total = 0
    with open(PRES_DEBUG_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = _csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for m in medicamentos:
            pres = (m.get('presentacion') or '').strip()
            if not pres:
                continue
            r = _parsear_presentacion(pres)
            if not r['forma']:
                sin_forma += 1
            if r['resto']:
                con_resto += 1
            total += 1
            writer.writerow({
                'debug_generado': debug_generado,
                'droga': m.get('droga', ''), 'marca': m.get('marca', ''),
                'presentacion_original': pres,
                'forma': r['forma'] or '', 'dosis': r['dosis'] or '',
                'unidad': r['unidad'] or '', 'cantidad': r['cantidad'] or '',
                'resto': r['resto'] or '',
            })
    limpios = total - sin_forma - con_resto
    print(f"   Total: {total} | Limpio: {limpios} ({100*limpios/max(total,1):.1f}%) | "
          f"Sin forma: {sin_forma} | Con resto: {con_resto}")
    print(f"   Debug: {PRES_DEBUG_PATH}")

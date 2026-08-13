"""tests/test_etl_modulos.py

Tests unitarios de las funciones puras de scripts/etl/, con fixtures
sintéticas. A diferencia de test_etl_sanidad.py y test_schema.py (que
validan el JSON final agregado), estos prueban cada función de reparación
en aislamiento — para que una regresión puntual en, por ejemplo, el fix
de Denver Farma, se detecte acá y no solo si mueve un umbral global.

No cubre funciones con I/O de red/disco (descargar_pdf, _descargar_pami,
cargar_blacklist, generar_debug_presentaciones) — esas necesitarían mocks
y quedan fuera del alcance de esta primera pasada.
"""
from etl.utils import limpiar_precio, es_precio
from etl.blacklist import make_key, filtrar_blacklist, _parece_corrupta
from etl.outliers import calcular_stats_por_droga, evaluar_outlier
from etl.droga_fixes import _separar_droga_marca
from etl.reparaciones import reparar_denver
from etl.parser import deduplicar


# ── utils.py ────────────────────────────────────────────────────────────────

def test_limpiar_precio_formato_argentino():
    assert limpiar_precio("1.234,56") == 1234.56

def test_limpiar_precio_valores_invalidos():
    assert limpiar_precio(None) is None
    assert limpiar_precio("-") is None
    assert limpiar_precio("") is None

def test_es_precio():
    assert es_precio("$ 1.234,56") is True
    assert es_precio("COMP.X 60") is False
    assert es_precio("") is False


# ── blacklist.py ────────────────────────────────────────────────────────────

def test_make_key_normaliza_case_y_espacios():
    a = {"droga": "Ibuprofeno", "marca": " Actron ", "presentacion": "400mg", "laboratorio": "Bayer"}
    b = {"droga": "ibuprofeno", "marca": "actron",   "presentacion": "400mg", "laboratorio": "BAYER"}
    assert make_key(a) == make_key(b)

def test_parece_corrupta_texto_limpio_no_marca_nada():
    assert _parece_corrupta("acetilcisteína|maxvan|600 mg comp.efer.x 10|vannier") is False
    assert _parece_corrupta("bausch & lomb argentina") is False

def test_parece_corrupta_detecta_mojibake_clasico():
    # 'í' mal decodificado como Latin-1 sobre bytes UTF-8 (el bug de admin.js)
    assert _parece_corrupta("acetilcisteÃ\xadna") is True

def test_parece_corrupta_detecta_variantes_que_el_filtro_viejo_no_veia():
    # el detector anterior (solo 'Ã'/'â€'/0x80-0x9f) se perdia estas
    assert _parece_corrupta("acetilcisteã\xadna") is True  # ã minuscula
    assert _parece_corrupta("alb£mina humana") is True     # £
    assert _parece_corrupta("ibumejoral ni¥os") is True    # ¥

def test_filtrar_blacklist_excluye_por_key():
    meds = [
        {"droga": "x", "marca": "y", "presentacion": "z", "laboratorio": "w", "precio": 100},
        {"droga": "a", "marca": "b", "presentacion": "c", "laboratorio": "d", "precio": 200},
    ]
    bl = {make_key(meds[0]): True}
    filtrados, n = filtrar_blacklist(meds, bl)
    assert n == 1
    assert len(filtrados) == 1
    assert filtrados[0]["droga"] == "a"

def test_filtrar_blacklist_vacia_no_toca_nada():
    meds = [{"droga": "x", "marca": "y", "presentacion": "z", "laboratorio": "w", "precio": 100}]
    filtrados, n = filtrar_blacklist(meds, {})
    assert n == 0
    assert filtrados == meds


# ── outliers.py ─────────────────────────────────────────────────────────────

def test_calcular_stats_por_droga_mediana_correcta():
    meds = [
        {"droga": "ibuprofeno", "precio": 100},
        {"droga": "ibuprofeno", "precio": 200},
        {"droga": "ibuprofeno", "precio": 300},
    ]
    stats = calcular_stats_por_droga(meds)
    assert stats["ibuprofeno"]["n"] == 3
    assert stats["ibuprofeno"]["mediana"] == 200

def test_evaluar_outlier_precio_invalido():
    score, flags, tipo, razones = evaluar_outlier({"precio": 0, "droga": "x"}, {})
    assert tipo == "invalido"
    assert "precio_obsoleto" in flags

def test_evaluar_outlier_precio_normal_no_marca_nada():
    stats = {"ibuprofeno": {"n": 5, "mediana": 5000, "fence_low": 2000}}
    score, flags, tipo, razones = evaluar_outlier(
        {"precio": 5000, "droga": "ibuprofeno"}, stats
    )
    assert tipo is None
    assert flags == []

def test_evaluar_outlier_precio_criticamente_bajo():
    stats = {"ibuprofeno": {"n": 5, "mediana": 10000, "fence_low": 5000}}
    score, flags, tipo, razones = evaluar_outlier(
        {"precio": 500, "droga": "ibuprofeno"}, stats
    )
    assert tipo == "bajo_critico"
    assert "precio_obsoleto" in flags


# ── droga_fixes.py ──────────────────────────────────────────────────────────

def test_separar_droga_marca_con_prefijo_conocido():
    droga_completa, resto = _separar_droga_marca("bacilo calmette-guerin (bcg)VACUNA X")
    assert droga_completa == "bacilo calmette-guerin"
    assert resto == "VACUNA X"

def test_separar_droga_marca_sin_match_devuelve_none():
    droga_completa, resto = _separar_droga_marca("esto no matchea ningun prefijo")
    assert droga_completa is None
    assert resto is None


# ── reparaciones.py ─────────────────────────────────────────────────────────

def test_reparar_denver_variante_a_presentacion_pegada_a_marca():
    meds = [{
        "droga": "alprazolam",
        "marca": "ALPRAZOLAM DENVER FARMA1 MG COMP.X 60",
        "presentacion": "",
        "laboratorio": "Denver Farma",
    }]
    _, reparados = reparar_denver(meds)
    assert reparados == 1
    assert meds[0]["marca"] == "ALPRAZOLAM DENVER FARMA"
    assert "1 mg comp.x 60" in meds[0]["presentacion"].lower()

def test_reparar_denver_no_toca_otros_laboratorios():
    meds = [{
        "droga": "ibuprofeno",
        "marca": "ACTRON",
        "presentacion": "400mg x30",
        "laboratorio": "Bayer",
    }]
    _, reparados = reparar_denver(meds)
    assert reparados == 0
    assert meds[0]["marca"] == "ACTRON"


# ── parser.py ────────────────────────────────────────────────────────────────

def test_deduplicar_elimina_solo_duplicados_exactos():
    meds = [
        {"droga": "x", "marca": "y", "presentacion": "z", "laboratorio": "w", "precio": 100},
        {"droga": "x", "marca": "y", "presentacion": "z", "laboratorio": "w", "precio": 100},
        {"droga": "x", "marca": "y", "presentacion": "z", "laboratorio": "w", "precio": 150},
    ]
    dedup, n = deduplicar(meds)
    assert n == 1
    assert len(dedup) == 2

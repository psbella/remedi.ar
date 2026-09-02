"""
Completa atc_por_droga.json con entradas del índice oficial ATC/DDD de la
WHO Collaborating Centre for Drug Statistics Methodology (WHOCC).

Fuente: https://atcddd.fhi.no/atc_ddd_index/
Obtenido vía: https://github.com/fabkury/atcd (CC BY-NC-SA 4.0, uso no comercial)
CSV usado: WHO ATC-DDD <fecha>.csv (nivel 5 = droga individual, 7 caracteres)

El CSV trae nombres INN en inglés. Se generan candidatos en español
aplicando reglas de sufijo INN estándar (ine->ina, in->ina, one->ona,
ide->ida, ate->ato, ic acid->,acido, yl->ilo) y se cruzan SOLO contra
nombres de droga que ya existen en medicamentos.json (no se inventan
entradas para drogas que no vendemos).

Cada candidato generado por regla de sufijo fue revisado manualmente
antes de incorporarse (ver commit correspondiente) — no se aplica el
resultado de la regla a ciegas.

Uso: python3 scripts/traducir_atc_who.py [--dry-run]
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSV_WHO = RAIZ / "scripts" / "who_atc_ddd.csv"  # copiar el CSV descargado acá
ATC_POR_DROGA = RAIZ / "data" / "atc" / "atc_por_droga.json"
MEDICAMENTOS = RAIZ / "data" / "medicamentos.json"

STOPWORDS_DROGA = {
    'asoc', 'clorhidrato', 'clorh', 'diclorh', 'sulfato', 'acetato', 'citrato',
    'bromuro', 'cloruro', 'fosfato', 'sodio', 'potasio', 'calcio', 'maleato',
    'fumarato', 'tartrato', 'besilato', 'mesilato', 'succinato', 'bicarbonato',
    'carbonato', 'nitrato', 'yoduro', 'gluconato', 'lactato', 'picosulfato',
    'valproato', 'fluoruro', 'ranelato',
}

REGLAS_SUFIJO_INN = [
    (r'ine$', 'ina'),
    (r'in$', 'ina'),
    (r'one$', 'ona'),
    (r'ide$', 'ida'),
    (r'ate$', 'ato'),
    (r'ic acid$', ',acido'),
    (r'yl$', 'ilo'),
]


def normalizar(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def candidatos_es(nombre_en: str) -> dict[str, str]:
    """Devuelve {candidato_espanol: regla_usada}. 'identico' = sin transformar."""
    cands = {nombre_en: "identico"}
    for patron, reemplazo in REGLAS_SUFIJO_INN:
        nuevo = re.sub(patron, reemplazo, nombre_en)
        if nuevo != nombre_en:
            cands[nuevo] = f"{patron}->{reemplazo}"
    return cands


def cargar_who() -> dict[str, set[str]]:
    who: dict[str, set[str]] = {}
    with open(CSV_WHO, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = row["atc_code"]
            if len(code) == 7:  # nivel 5 = droga individual
                who.setdefault(normalizar(row["atc_name"]), set()).add(code)
    return who


def drogas_locales_sin_clasificar(atc_por_droga: dict) -> set[str]:
    with open(MEDICAMENTOS, encoding="utf-8") as f:
        meds = json.load(f)["medicamentos"]

    def matchea_local(norm: str) -> bool:
        return norm in atc_por_droga or f"acido {norm}" in atc_por_droga

    partes_sin_clasificar = set()
    for m in meds:
        if not m.get("droga"):
            continue
        partes = [normalizar(p) for p in m["droga"].split(",")]
        partes = [p for p in partes if p and p.replace(".", "") not in STOPWORDS_DROGA]
        if not partes or all(matchea_local(p) for p in partes):
            continue
        partes_sin_clasificar.update(partes)
    return partes_sin_clasificar


def main():
    dry_run = "--dry-run" in sys.argv

    with open(ATC_POR_DROGA, encoding="utf-8") as f:
        atc_por_droga = json.load(f)

    who = cargar_who()
    faltantes = drogas_locales_sin_clasificar(atc_por_droga)

    nuevas = {}
    for nombre_en, codes in who.items():
        for cand, regla in candidatos_es(nombre_en).items():
            if cand in faltantes and cand not in atc_por_droga:
                nuevas.setdefault(cand, (nombre_en, regla, sorted(codes)))

    print(f"Drogas locales sin clasificar: {len(faltantes)}")
    print(f"Nuevas entradas generadas: {len(nuevas)}")
    for droga, (en, regla, codes) in sorted(nuevas.items()):
        marca = "" if regla == "identico" else f"  [{regla}]"
        print(f"  {droga:30s} <- {en:30s} -> {codes}{marca}")

    if dry_run:
        print("\n--dry-run: no se escribió nada.")
        return

    for droga, (_, _, codes) in nuevas.items():
        atc_por_droga[droga] = codes

    with open(ATC_POR_DROGA, "w", encoding="utf-8") as f:
        json.dump(atc_por_droga, f, ensure_ascii=False, sort_keys=True)

    print(f"\n{ATC_POR_DROGA} actualizado con {len(nuevas)} entradas nuevas.")


if __name__ == "__main__":
    main()

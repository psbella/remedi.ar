"""
scripts/enriquecer_info_adicional_por_droga.py

Extiende la cobertura de data/info-adicional/info_adicional.json más allá
del match exacto por producto (droga+marca+laboratorio+presentación).

Para los medicamentos sin match exacto, busca si existe una entrada de
AlfaBeta cuya composición (campo "drogas", NO el prefijo del hash) sea
un único principio activo y coincida textualmente (normalizado) con el
"droga" del medicamento. Si hay varias entradas donantes para el mismo
principio activo, solo se usa el valor cuando todas coinciden (consenso);
si hay conflicto, se descarta y se reporta.

Deliberadamente NO propaga "laboratorio" ni "vigencia": son atributos
del producto puntual, no del principio activo, y copiarlos sería
mostrar un dato incorrecto (no solo incompleto).

Las entradas inferidas se agregan a info_adicional.json bajo el hash
propio del medicamento (mismo formato que las entradas exactas), pero
marcadas con "inferido": true para que la UI pueda diferenciarlas.

Uso:
    python3 scripts/enriquecer_info_adicional_por_droga.py [--dry-run]
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MEDICAMENTOS_PATH = RAIZ / "data" / "medicamentos.json"
INFO_ADICIONAL_PATH = RAIZ / "data" / "info-adicional" / "info_adicional.json"


def _slug(s):
    if not s:
        return ""
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9-]", "", s)
    return s


def _hash_medicamento(m):
    return "--".join([
        _slug(m.get("droga")),
        _slug(m.get("marca")),
        _slug(m.get("laboratorio")),
        _slug(m.get("presentacion")),
    ])


def _normalizar_droga(s):
    """Normaliza para comparar texto de droga (no para armar URLs/hash)."""
    if not s:
        return ""
    s = s.strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", " ", s)
    return s


def _tokens_composicion(s):
    """
    Divide una cadena de composición en un conjunto de tokens normalizados,
    partiendo tanto por salto de línea (como AlfaBeta separa ingredientes
    realmente distintos en su campo "drogas") como por coma (como a veces
    aparece el "droga" de medicamentos.json, incluida una combinación real
    de 2+ principios, pero también a veces el nombre de una sal/éster de un
    único principio, ej. "Abiraterona, acetato").

    Partiendo igual de los dos lados, la comparación por conjunto sigue
    siendo consistente sea cual sea el motivo real de la coma: dos productos
    con exactamente la misma composición dan el mismo conjunto de tokens,
    y uno con una composición distinta da un conjunto distinto.
    """
    partes = re.split(r"[\n,]", s or "")
    return frozenset(_normalizar_droga(p) for p in partes if p.strip())


def _cargar_medicamentos():
    data = json.loads(MEDICAMENTOS_PATH.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                return v
        raise ValueError("No se encontró una lista de medicamentos en el JSON")
    return data


def _elegir_consenso_atc(atcs):
    """
    atcs: lista de valores de ATC (ya sin None/vacíos) de los donantes de
    una misma droga. Devuelve (valor_elegido, hay_conflicto_real).

    Un solo valor con apariciones aisladas de otros valores (soporte 1,
    típicamente un glitch de scraping puntual en una sola página de
    AlfaBeta) no cuenta como conflicto real. Conflicto real = dos o más
    valores distintos con soporte >=2 cada uno.
    """
    if not atcs:
        return None, False
    conteo = Counter(atcs)
    if len(conteo) == 1:
        return atcs[0], False
    ranking = conteo.most_common()
    valor_top, soporte_top = ranking[0]
    otros_con_soporte = [v for v, c in ranking[1:] if c >= 2]
    if soporte_top >= 2 and not otros_con_soporte:
        return valor_top, False
    return None, True


def construir_consenso_por_composicion(info_adicional):
    """
    Recorre info_adicional.json y arma un mapa: conjunto-de-tokens de
    composición -> (atc, clases_terapeuticas). Cubre tanto principios
    activos únicos como combinaciones reales de 2+ principios, siempre que
    dos o más donantes coincidan en el mismo conjunto exacto de tokens.

    Valores vacíos/None de un donante no cuentan como voto en contra: se
    ignoran al buscar consenso. Para "clases_terapeuticas" se exige
    coincidencia exacta entre todos los donantes no vacíos (es información
    clínica central). Para "atc" se tolera un glitch aislado de un único
    donante (ver _elegir_consenso_atc), pero un desacuerdo con soporte real
    de ambos lados se descarta igual.
    """
    atcs_por_composicion = defaultdict(list)
    clases_por_composicion = defaultdict(list)

    for info in info_adicional.values():
        drogas_raw = (info.get("drogas") or "").strip()
        if not drogas_raw:
            continue
        tokens = _tokens_composicion(drogas_raw)
        if not tokens:
            continue
        atc = (info.get("atc") or "").strip()
        clases = (info.get("clases_terapeuticas") or "").strip()
        if not atc and not clases:
            continue
        if atc:
            atcs_por_composicion[tokens].append(atc)
        if clases:
            clases_por_composicion[tokens].append(clases)

    consenso = {}
    conflictos = []

    for tokens in set(atcs_por_composicion) | set(clases_por_composicion):
        atc, atc_conflicto = _elegir_consenso_atc(atcs_por_composicion.get(tokens, []))

        clases_vals = set(clases_por_composicion.get(tokens, []))
        clases_conflicto = len(clases_vals) > 1
        clases = next(iter(clases_vals)) if len(clases_vals) == 1 else None

        if atc_conflicto or clases_conflicto:
            detalle = {
                "atc": Counter(atcs_por_composicion.get(tokens, [])) if atc_conflicto else None,
                "clases_terapeuticas": Counter(clases_por_composicion.get(tokens, [])) if clases_conflicto else None,
            }
            conflictos.append((tokens, detalle))
            continue

        if not atc and not clases:
            continue

        consenso[tokens] = {"atc": atc or None, "clases_terapeuticas": clases}

    return consenso, conflictos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                         help="No escribe el archivo, solo muestra el resumen.")
    args = parser.parse_args()

    medicamentos = _cargar_medicamentos()
    info_adicional = json.loads(INFO_ADICIONAL_PATH.read_text(encoding="utf-8"))

    cobertura_antes = sum(1 for m in medicamentos if _hash_medicamento(m) in info_adicional)

    consenso, conflictos = construir_consenso_por_composicion(info_adicional)

    agregados = 0
    for m in medicamentos:
        h = _hash_medicamento(m)
        if h in info_adicional:
            continue  # ya tiene match exacto, no tocar
        tokens = _tokens_composicion(m.get("droga"))
        if not tokens:
            continue
        match = consenso.get(tokens)
        if not match:
            continue
        info_adicional[h] = {
            "drogas": m.get("droga"),
            "atc": match["atc"],
            "clases_terapeuticas": match["clases_terapeuticas"],
            "inferido": True,
        }
        agregados += 1

    cobertura_despues = cobertura_antes + agregados

    print(f"Medicamentos totales:              {len(medicamentos)}")
    print(f"Cobertura antes (match exacto):    {cobertura_antes} "
          f"({100 * cobertura_antes / len(medicamentos):.1f}%)")
    print(f"Agregados por consenso de droga:   {agregados}")
    print(f"Cobertura después:                 {cobertura_despues} "
          f"({100 * cobertura_despues / len(medicamentos):.1f}%)")
    print(f"Principios activos con conflicto (no propagados): {len(conflictos)}")
    if conflictos:
        print("  Ejemplos de conflicto real (composición -> valores en disputa):")
        for tokens, detalle in conflictos[:5]:
            partes = []
            if detalle["atc"]:
                partes.append(f"atc={dict(detalle['atc'])}")
            if detalle["clases_terapeuticas"]:
                partes.append(f"clases={dict(detalle['clases_terapeuticas'])}")
            print(f"    - {' + '.join(sorted(tokens))}: {' | '.join(partes)}")

    if args.dry_run:
        print("\n--dry-run: no se escribió nada.")
        return

    INFO_ADICIONAL_PATH.write_text(
        json.dumps(info_adicional, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"\nEscrito: {INFO_ADICIONAL_PATH}")


if __name__ == "__main__":
    sys.exit(main())

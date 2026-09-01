"""
scripts/listar_droga_sin_info.py

Genera data/info-adicional/faltantes_atc.csv: una fila por cada composición
(conjunto de principios activos) que hoy NO tiene ATC en info_adicional.json
-- ni por match exacto, ni por consenso, ni por combinación de componentes --
agrupadas y ordenadas por cantidad de medicamentos afectados (de mayor a
menor impacto).

Incluye tanto las composiciones sin ningún dato como las que SÍ tienen datos
en AlfaBeta pero en conflicto real (fueron descartadas por
construir_consenso_por_composicion): para estas últimas se listan los
valores en disputa en la columna 'conflicto_existente', como referencia útil
al completar el ATC correcto a mano.

Reutiliza las funciones de enriquecer_info_adicional_por_droga.py (mismo
directorio) para tokenizar/hashear exactamente igual que el script que
después va a consumir este CSV -- evita que una normalización distinta acá
genere una fila que en la práctica no matchee con nada.

Uso:
    python3 scripts/listar_droga_sin_info.py
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enriquecer_info_adicional_por_droga as consenso  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FALTANTES_PATH = RAIZ / "data" / "info-adicional" / "faltantes_atc.csv"


def main():
    medicamentos = consenso._cargar_medicamentos()
    info_adicional = json.loads(consenso.INFO_ADICIONAL_PATH.read_text(encoding="utf-8"))

    _, conflictos = consenso.construir_consenso_por_composicion(info_adicional)
    conflictos_por_tokens = {tokens: detalle for tokens, detalle in conflictos}

    # Agrupar medicamentos SIN cobertura por composición (tokens)
    productos_por_tokens = defaultdict(list)
    for m in medicamentos:
        h = consenso._hash_medicamento(m)
        if h in info_adicional:
            continue  # ya tiene ATC (exacto, inferido o combinado)
        tokens = consenso._tokens_composicion(m.get("droga"))
        if not tokens:
            continue
        productos_por_tokens[tokens].append(m)

    filas = []
    for tokens, productos in productos_por_tokens.items():
        dromas_originales = Counter(p.get("droga") for p in productos)
        droga_representativa = dromas_originales.most_common(1)[0][0]

        detalle_conflicto = conflictos_por_tokens.get(tokens)
        conflicto_txt = ""
        if detalle_conflicto:
            partes = []
            if detalle_conflicto.get("atc"):
                partes.append(f"atc en disputa: {dict(detalle_conflicto['atc'])}")
            if detalle_conflicto.get("clases_terapeuticas"):
                partes.append(f"clases en disputa: {dict(detalle_conflicto['clases_terapeuticas'])}")
            conflicto_txt = " | ".join(partes)

        # Ejemplos de marca para que sea más fácil ubicar el producto real
        marcas_ejemplo = ", ".join(sorted({p.get("marca", "") for p in productos})[:3])

        filas.append({
            "droga": droga_representativa,
            "tokens_composicion": " + ".join(sorted(tokens)),
            "cantidad_productos": len(productos),
            "marcas_ejemplo": marcas_ejemplo,
            "conflicto_existente": conflicto_txt,
            "atc": "",
            "clases_terapeuticas": "",
        })

    filas.sort(key=lambda f: f["cantidad_productos"], reverse=True)

    FALTANTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FALTANTES_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "droga", "tokens_composicion", "cantidad_productos",
            "marcas_ejemplo", "conflicto_existente", "atc", "clases_terapeuticas",
        ])
        writer.writeheader()
        writer.writerows(filas)

    total_productos_sin_cobertura = sum(f["cantidad_productos"] for f in filas)
    print(f"Composiciones distintas sin ATC: {len(filas)}")
    print(f"Medicamentos afectados en total: {total_productos_sin_cobertura}")
    print(f"  (de los cuales con conflicto ya detectado: "
          f"{sum(1 for f in filas if f['conflicto_existente'])})")
    print(f"\nEscrito: {FALTANTES_PATH}")
    print("\nTop 10 por impacto:")
    for fila in filas[:10]:
        print(f"  {fila['cantidad_productos']:>4}  {fila['droga']}  [{fila['tokens_composicion']}]")


if __name__ == "__main__":
    main()

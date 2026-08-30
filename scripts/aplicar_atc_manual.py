"""
scripts/aplicar_atc_manual.py

Toma el CSV completado a mano (data/info-adicional/faltantes_atc.csv, generado
por listar_droga_sin_info.py) y aplica las filas que ya tienen 'atc' y/o
'clases_terapeuticas' completados a data/info-adicional/info_adicional.json.

A diferencia de las entradas "inferido" (consenso estadístico entre varios
donantes de AlfaBeta) o "combinado" (síntesis de componentes por separado),
estas entradas vienen de una fuente autoritativa verificada a mano (ficha
técnica AEMPS/ANMAT, índice ATC/DDD de la OMS, etc.) -- se marcan
"fuente": "manual" para trazabilidad, pero NO llevan "inferido" ni
"combinado" porque no son estadísticas ni sintéticas.

Matchea por tokens_composicion (no por el texto libre 'droga', que es solo
para lectura humana) usando la misma tokenización que
enriquecer_info_adicional_por_droga.py, para evitar cualquier divergencia
de normalización entre ambos scripts.

Uso:
    python3 scripts/aplicar_atc_manual.py [--csv RUTA] [--dry-run]
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enriquecer_info_adicional_por_droga as consenso  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FALTANTES_PATH_DEFAULT = RAIZ / "data" / "info-adicional" / "faltantes_atc.csv"


def _tokens_desde_csv(tokens_str):
    """Reconstruye el frozenset de tokens desde la columna 'tokens_composicion'
    (formato "token1 + token2 + ..."), tal como la escribió listar_droga_sin_info.py."""
    partes = [p.strip() for p in tokens_str.split(" + ") if p.strip()]
    return frozenset(partes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default=str(FALTANTES_PATH_DEFAULT),
                         help="Ruta al CSV completado (default: data/info-adicional/faltantes_atc.csv)")
    parser.add_argument("--dry-run", action="store_true",
                         help="No escribe el archivo, solo muestra el resumen.")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: no existe {csv_path}")
        return 1

    medicamentos = consenso._cargar_medicamentos()
    info_adicional = json.loads(consenso.INFO_ADICIONAL_PATH.read_text(encoding="utf-8"))

    # Armar mapa tokens -> (atc, clases_terapeuticas) solo con filas completadas
    provistos_por_tokens = {}
    filas_leidas = 0
    filas_completadas = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filas_leidas += 1
            atc = (row.get("atc") or "").strip()
            clases = (row.get("clases_terapeuticas") or "").strip()
            if not atc and not clases:
                continue  # fila todavía sin completar, ignorar
            filas_completadas += 1
            tokens = _tokens_desde_csv(row["tokens_composicion"])
            provistos_por_tokens[tokens] = {
                "atc": atc or None,
                "clases_terapeuticas": clases or None,
            }

    agregados = 0
    cobertura_antes = sum(1 for m in medicamentos if consenso._hash_medicamento(m) in info_adicional)

    for m in medicamentos:
        h = consenso._hash_medicamento(m)
        if h in info_adicional:
            continue  # ya cubierto (exacto, inferido o combinado), no pisar
        tokens = consenso._tokens_composicion(m.get("droga"))
        if not tokens:
            continue
        provisto = provistos_por_tokens.get(tokens)
        if not provisto:
            continue
        info_adicional[h] = {
            "drogas": m.get("droga"),
            "atc": provisto["atc"],
            "clases_terapeuticas": provisto["clases_terapeuticas"],
            "fuente": "manual",
        }
        agregados += 1

    cobertura_despues = cobertura_antes + agregados

    print(f"Filas leídas del CSV:               {filas_leidas}")
    print(f"Filas completadas (con atc/clases):  {filas_completadas}")
    print(f"Composiciones distintas provistas:   {len(provistos_por_tokens)}")
    print(f"Medicamentos totales:                {len(medicamentos)}")
    print(f"Cobertura antes:                     {cobertura_antes} "
          f"({100 * cobertura_antes / len(medicamentos):.1f}%)")
    print(f"Agregados por CSV manual:            {agregados}")
    print(f"Cobertura después:                   {cobertura_despues} "
          f"({100 * cobertura_despues / len(medicamentos):.1f}%)")

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

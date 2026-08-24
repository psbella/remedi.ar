#!/usr/bin/env python3
"""
scripts/snapshot_semanal.py
Genera un CSV con los precios confiables de la semana y lo sube
como asset a la release mensual de GitHub.
Estructura:
  Release:  historial-YYYY-MM
  Asset:    snapshot_semanaX_DD-MM-YYYY.csv
Solo incluye medicamentos con vigencia_score >= 50.
"""
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from github_release_helper import obtener_o_crear_release, api_upload, asset_existe
AR_TZ        = timezone(timedelta(hours=-3))
BASE         = Path(__file__).parent.parent
DATOS_PATH   = BASE / "data" / "medicamentos.json"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
CAMPOS_CSV = ["fecha", "droga", "marca", "laboratorio", "presentacion", "precio", "pami_cobertura"]
def semana_del_mes(fecha: datetime) -> int:
    """Devuelve el numero de semana dentro del mes (1-5)."""
    return (fecha.day - 1) // 7 + 1
def nombre_archivo(fecha: datetime) -> str:
    """Genera el nombre del asset CSV para una fecha dada.

    Formato: snapshot_semana{N}_{DD-MM-YYYY}.csv
    donde N es el numero de semana del mes (1-5) y DD-MM-YYYY es
    la fecha del snapshot. Ejemplo real: snapshot_semana1_06-08-2026.csv
    """
    sem   = semana_del_mes(fecha)
    dia   = fecha.strftime("%d-%m-%Y")
    return f"snapshot_semana{sem}_{dia}.csv"
def generar_csv(fecha: datetime) -> tuple[str, bytes]:
    """Genera el CSV y devuelve (nombre_archivo, contenido_bytes)."""
    with open(DATOS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    meds     = data.get("medicamentos", [])
    fecha_str = fecha.strftime("%Y-%m-%d")
    confiables = [m for m in meds if (m.get("vigencia_score") or 0) >= 50]
    print(f"   Total: {len(meds)} | Confiables (score >= 50): {len(confiables)}")
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CAMPOS_CSV, extrasaction="ignore")
    writer.writeheader()
    for m in confiables:
        writer.writerow({
            "fecha":           fecha_str,
            "droga":           m.get("droga", ""),
            "marca":           m.get("marca", ""),
            "laboratorio":     m.get("laboratorio", ""),
            "presentacion":    m.get("presentacion", ""),
            "precio":          m.get("precio", ""),
            "pami_cobertura":  m.get("pami_cobertura", ""),
        })
    nombre = nombre_archivo(fecha)
    return nombre, buf.getvalue().encode("utf-8")
def main():
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN no disponible.")
        sys.exit(1)
    ahora  = datetime.now(AR_TZ)
    print(f"\nSnapshot semanal - {ahora.strftime('%Y-%m-%d %H:%M')} AR")
    nombre_csv, contenido = generar_csv(ahora)
    mes_tag    = ahora.strftime("historial-%Y-%m")
    mes_nombre = ahora.strftime("Historial %B %Y")
    print(f"   Archivo: {nombre_csv}")
    print(f"   Release: {mes_tag}")
    release = obtener_o_crear_release(
        mes_tag, mes_nombre,
        body=f"Snapshots semanales de precios - {mes_nombre}",
    )
    if asset_existe(release, nombre_csv):
        print(f"   Asset '{nombre_csv}' ya existe, saltando.")
        return
    resultado = api_upload(release["upload_url"], nombre_csv, contenido, "text/csv")
    print(f"   Subido: {resultado['browser_download_url']}")
if __name__ == "__main__":
    main()
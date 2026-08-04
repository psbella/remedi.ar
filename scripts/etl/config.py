"""etl/config.py - Constantes y paths compartidos por todos los módulos del ETL."""

import ssl
from pathlib import Path
from datetime import timezone, timedelta

import certifi

AR_TZ = timezone(timedelta(hours=-3))
ssl_context = ssl.create_default_context(cafile=certifi.where())

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG OUTLIERS
# ─────────────────────────────────────────────────────────────────────────────
OUTLIER_CONFIG = {
    "PRECIO_MINIMO_ARS":  1_800,
    "UMBRAL_CRITICO":     0.10,
    "UMBRAL_RELATIVO":    0.25,
    "MIN_REGISTROS":      3,
    "IQR_FACTOR":         1.5,
    "SCORE_OUTLIER":      20,
    "SCORE_NORMAL":       100,
}

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
BASE              = Path(__file__).parent.parent.parent
BLACKLIST_PATH    = BASE / "data" / "blacklist.json"
OUTLIER_REPORT    = BASE / "data" / "outlier_report.json"
MEDICAMENTOS_PATH = BASE / "data" / "medicamentos.json"
PRES_DEBUG_PATH   = BASE / "data" / "presentaciones_debug.csv"
DROGA_FIXES_PATH  = BASE / "data" / "droga_fixes.json"

# Vademécum PAMI: se actualiza a mano ~1 vez por mes (ver README).
# Fuente: https://datos.pami.org.ar/dataset/vademecum-pami-farmacia
PAMI_PATH = BASE / "data" / "pami.xlsx"

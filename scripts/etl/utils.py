"""etl/utils.py - Helpers de parseo/limpieza básicos."""

import re


def limpiar_precio(valor):
    """Convierte un precio en formato AR (miles con punto, decimales con
    coma, ej. "1.234,56") a float. Devuelve None si el valor es vacio,
    "-" o no se puede convertir.
    """
    if not valor or valor == '-':
        return None
    valor = str(valor).strip()
    valor = valor.replace('.', '').replace(',', '.')
    valor = re.sub(r'[^\d\.]', '', valor)
    try:
        return float(valor)
    except Exception:
        return None

def es_precio(texto):
    """Heuristica para detectar si un string tiene forma de precio (solo
    digitos, puntos y comas, ignorando $ y espacios), sin convertirlo.
    """
    if not texto:
        return False
    limpio = re.sub(r'[\$\s]', '', texto)
    return bool(re.match(r'^[\d\.,]+$', limpio))

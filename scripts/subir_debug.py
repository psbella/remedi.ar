#!/usr/bin/env python3
"""
scripts/subir_debug.py
Sube medicamentos.pretty.json a la release "debug-latest" de GitHub.
"""

import sys
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any

# Intentamos importar el helper, si falla, lanzamos un error claro
try:
    from github_release_helper import obtener_o_crear_release, subir_o_reemplazar_asset
except ImportError as e:
    print(f"ERROR: No se pudo importar 'github_release_helper'. ¿Está en el PYTHONPATH? {e}")
    sys.exit(1)

# --- CONFIGURACIÓN ---
# Usamos un diccionario o una clase de configuración para evitar variables globales sueltas
class Config:
    AR_TZ = timezone(timedelta(hours=-3))
    BASE = Path(__file__).parent.parent
    PRETTY_SRC = BASE / ".debug" / "medicamentos.pretty.json"
    TAG = "debug-latest"
    NOMBRE = "Debug — Última corrida del ETL"
    ASSET_NAME = "medicamentos.pretty.json"
    MIME_TYPE = "application/json"

# Configuración de Logging (Mejor que usar print)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def main() -> None:
    conf = Config()

    # 1. Validación de existencia y contenido
    if not conf.PRETTY_SRC.exists():
        logger.error(f"El archivo fuente no existe: {conf.PRETTY_SRC}")
        sys.exit(1)
    
    if conf.PRETTY_SRC.stat().st_size == 0:
        logger.error(f"El archivo {conf.PRETTY_SRC} está vacío. No hay nada que subir.")
        sys.exit(1)

    ahora = datetime.now(conf.AR_TZ)
    
    try:
        # 2. Lectura de datos
        contenido = conf.PRETTY_SRC.read_bytes()
        tamano_kb = len(contenido) / 1024
        
        logger.info(f"Iniciando subida de debug — {ahora.strftime('%Y-%m-%d %H:%M')} AR")
        logger.info(f"Archivo detectado: {conf.ASSET_NAME} ({tamano_kb:.2f} KB)")

        # 3. Preparación del cuerpo del release
        body = (
            f"JSON formateado (indent=2) de la última corrida del ETL, "
            f"para debug humano. Se sobreescribe en cada actualización.\n\n"
            f"**Última actualización:** {ahora.strftime('%Y-%m-%d %H:%M')} AR"
        )

        # 4. Interacción con la API (con manejo de excepciones)
        logger.info(f"Obteniendo/Creando release con tag: {conf.TAG}...")
        release = obtener_o_crear_release(conf.TAG, conf.NOMBRE, body)

        logger.info("Subiendo/Reemplazando asset en GitHub...")
        resultado: Dict[str, Any] = subir_o_reemplazar_asset(
            release, 
            conf.ASSET_NAME, 
            contenido, 
            conf.MIME_TYPE
        )

        # 5. Resultado final
        url_descarga = resultado.get('browser_download_url')
        if url_descarga:
            logger.info("✅ ¡ÉXITO!")
            logger.info(f"URL de descarga: {url_descarga}")
        else:
            logger.warning("✅ Subido, pero no se pudo obtener la URL de descarga.")

    except PermissionError:
        logger.error("Error de permisos: No se pudo leer el archivo fuente.")
        sys.exit(1)
    except ConnectionError as e:
        logger.error(f"Error de red al conectar con GitHub: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
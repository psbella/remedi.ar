"""etl/parser.py - Descarga del PDF de SIAFAR y parseo a lista de medicamentos."""

import sys
import time
import urllib.request
import urllib.error

import fitz

from .config import ssl_context
from .utils import es_precio, limpiar_precio

PDF_URL = "https://siafar.com/precios/pdf/"


def descargar_pdf(pdf_url=PDF_URL, max_reintentos=3, backoff_segundos=60) -> bytes:
    """Descarga el PDF de precios de SIAFAR con reintentos. Sale del proceso si fallan todos."""
    print(f"Descargando: {pdf_url}")
    pdf_bytes = None

    for intento in range(1, max_reintentos + 1):
        try:
            req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30, context=ssl_context) as r:
                pdf_bytes = r.read()
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            print(f"   Intento {intento}/{max_reintentos} fallido: {e}")
            if intento < max_reintentos:
                print(f"   Reintentando en {backoff_segundos}s...")
                time.sleep(backoff_segundos)
            else:
                print("   ERROR: no se pudo descargar el PDF tras todos los reintentos.")
                sys.exit(1)

    print(f"Tamano: {len(pdf_bytes)} bytes")
    return pdf_bytes


def parsear_pdf(pdf_bytes: bytes) -> list:
    """
    Parsea el PDF de precios de SIAFAR y devuelve la lista cruda de
    medicamentos (sin ninguna capa de reparación aplicada todavía).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    medicamentos = []

    for pagina_num in range(len(doc)):
        texto = doc[pagina_num].get_text()
        lineas = [linea.strip() for linea in texto.split('\n') if linea.strip()]
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            if 'MONODROGA' in linea or 'pag' in linea.lower():
                i += 1
                continue
            if es_precio(linea):
                i += 1
                continue

            # ── CAPA 1: detección de desplazamiento en tiempo de parse ──
            #
            # Estructura normal (5 campos):
            #   i+0  droga
            #   i+1  marca
            #   i+2  presentacion
            #   i+3  laboratorio
            #   i+4  precio
            #
            # Estructura desplazada (4 campos, lab ausente en PDF):
            #   i+0  droga
            #   i+1  marca
            #   i+2  laboratorio  ← ocupa el slot de presentacion
            #   i+3  precio       ← sube un lugar
            #
            # Detección: si lineas[i+3] ya es precio, el laboratorio
            # se desplazó a lineas[i+2] y no hay presentacion separada.

            if i + 3 < len(lineas) and es_precio(lineas[i+3]):
                # Estructura de 4 campos: lab en slot de presentacion
                droga        = linea
                marca        = lineas[i+1]
                presentacion = ''
                laboratorio  = lineas[i+2]
                precio_str   = lineas[i+3]
                avance       = 4
            elif i + 4 < len(lineas):
                # Estructura normal de 5 campos
                droga        = linea
                marca        = lineas[i+1]
                presentacion = lineas[i+2]
                laboratorio  = lineas[i+3]
                precio_str   = lineas[i+4]
                avance       = 5
            else:
                i += 1
                continue

            if es_precio(precio_str):
                precio = limpiar_precio(precio_str)
                if precio and droga:
                    medicamentos.append({
                        'droga':        droga.lower(),
                        'marca':        marca.upper(),
                        'presentacion': presentacion,
                        'laboratorio':  laboratorio if not es_precio(laboratorio) else 'Desconocido',
                        'precio':       precio,
                    })
                i += avance
                continue

            i += 1

        if (pagina_num + 1) % 10 == 0:
            print(f"Pagina {pagina_num + 1}: {len(medicamentos)} medicamentos")

    doc.close()
    print(f"\nTotal extraido: {len(medicamentos)}")

    if not medicamentos:
        print("No se extrajo ningun medicamento")
        sys.exit(1)

    return medicamentos


def deduplicar(medicamentos: list) -> tuple:
    """
    Descarta registros exactamente repetidos (droga+marca+presentacion+
    laboratorio+precio idénticos), que el PDF a veces incluye dos veces.

    Retorna la lista deduplicada y la cantidad de duplicados eliminados.
    """
    n_antes_dedup = len(medicamentos)
    vistos = set()
    medicamentos_dedup = []
    for m in medicamentos:
        clave = (m['droga'], m['marca'], m['presentacion'], m['laboratorio'], m['precio'])
        if clave not in vistos:
            vistos.add(clave)
            medicamentos_dedup.append(m)
    n_duplicados = n_antes_dedup - len(medicamentos_dedup)
    return medicamentos_dedup, n_duplicados

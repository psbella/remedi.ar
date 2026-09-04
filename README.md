<p align="center">
  <img src="https://remedi.ar/img/favicon.svg" width="90" />
</p>

# remedi.ar — Buscador de precios de medicamentos en Argentina

<p align="center">
  <strong>Buscador de precios de medicamentos en Argentina</strong><br>
  <em>Sistema open source que procesa datos oficiales de SIAFAR/COFA/PAMI y genera un comparador de precios con actualización automática dos veces al día.</em>
</p>

<p align="center">
  <a href="https://remedi.ar">https://remedi.ar</a> ·
  <a href="https://github.com/psbella/remediar">GitHub</a>
</p>

---

<p align="left">
<!-- Versión -->
<img src="https://img.shields.io/github/v/release/psbella/remediar">
<img src="https://img.shields.io/github/actions/workflow/status/psbella/remediar/update_prices.yml?label=ETL&logo=github-actions&logoColor=white">
<br>
<!-- Hosting & License -->
<img src="https://img.shields.io/badge/hosted-GitHub%20Pages-181717?logo=github">
<img src="https://img.shields.io/badge/License-MIT-blue.svg">
<img src="https://img.shields.io/github/repo-size/psbella/remediar">
<img src="https://img.shields.io/github/last-commit/psbella/remediar">
<img src="https://img.shields.io/github/issues-raw/psbella/remediar">
<img src="https://img.shields.io/badge/Proxy-Cloudflare-F38020?logo=cloudflare&logoColor=white">
<br>
<!-- Valores -->
<img src="https://img.shields.io/badge/Open_Source-Yes-brightgreen">
<img src="https://img.shields.io/badge/Ads-No-red">
<img src="https://img.shields.io/badge/Tracking-Anonymous_only-success">
<img src="https://img.shields.io/badge/Privacy_First-Yes-success">
<img src="https://img.shields.io/badge/PRs-Welcome-brightgreen">
<br>
<!-- Frontend -->
<img src="https://img.shields.io/badge/Responsive-Yes-brightgreen">
<img src="https://img.shields.io/badge/Mobile_First-Yes-brightgreen">
<img src="https://img.shields.io/badge/PWA-Enabled-5A0FC8?logo=pwa">
<img src="https://img.shields.io/badge/SEO-Optimized-success">
<img src="https://img.shields.io/badge/Lighthouse-94%2F100-success">
<img src="https://img.shields.io/badge/dependencies-0-success">
<img src="https://img.shields.io/badge/Static_Site-Yes-blue">
<br>
<!-- Tecnologías -->
<img src="https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white">
<img src="https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white">
<img src="https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?logo=javascript&logoColor=black">
<img src="https://img.shields.io/badge/JSON-000000?logo=json&logoColor=white">
<img src="https://img.shields.io/badge/SVG-FF9800?logo=svg&logoColor=white">
<br>
<!-- Backend / Automation -->
<img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
<img src="https://img.shields.io/badge/PyMuPDF-ee0000?logo=pypi&logoColor=white">
<img src="https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white">
<img src="https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions">
<img src="https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white">
<img src="https://img.shields.io/badge/SSL-certifi-00897b">
<img src="https://img.shields.io/badge/Analytics-GA4-E37400?logo=googleanalytics&logoColor=white">
<br>
<!-- Datos -->
<img src="https://img.shields.io/badge/CSP-SHA256-success">
<br>
<!-- Diagramas -->
<img src="https://img.shields.io/badge/diagrams-Mermaid-ff3670?logo=mermaid&logoColor=white">
<br>
<!-- Features -->
<img src="https://img.shields.io/badge/Historial-GitHub%20Releases-181717?logo=github">
<img src="https://img.shields.io/badge/Share-Deep%20Link-00897b">
</p>

---

> 🇬🇧 **[English version](./README.en.md)**

---

# 📋 Tabla de Contenidos

- [✨ Demo en Vivo](#-demo-en-vivo)
- [📊 Dataset actual](#-dataset-actual)
- [🎯 Funcionamiento General](#-funcionamiento-general)
- [🧭 Principios del Proyecto](#-principios-del-proyecto)
- [👤 Flujo del Usuario](#-flujo-del-usuario)
- [🧠 Algoritmo de Búsqueda y Filtrado](#-algoritmo-de-búsqueda-y-filtrado)
- [🔄 Actualización Automática de Datos](#-actualización-automática-de-datos)
- [📦 Estructura de Datos JSON](#-estructura-de-datos-json)
- [⚡ Optimizaciones Implementadas](#-optimizaciones-implementadas)
- [⏱️ Tiempos de Respuesta](#️-tiempos-de-respuesta)
- [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
- [📁 Estructura del Repositorio](#-estructura-del-repositorio)
- [🧰 Stack Tecnológico](#-stack-tecnológico)
- [🧠 Decisiones Técnicas](#-decisiones-técnicas)
- [💻 Ejecución Local](#-ejecución-local)
- [🐍 Scripts Python](#-scripts-python)
- [📊 Métricas y Rendimiento](#-métricas-y-rendimiento)
- [🔍 SEO y Metadatos](#-seo-y-metadatos)
- [🔒 Seguridad y Privacidad](#-seguridad-y-privacidad)
- [🔌 API No Oficial](#-api-no-oficial)
- [👥 Guía de Contribución](#-guía-de-contribución)
- [📊 Diagramas de Flujo Detallados](#-diagramas-de-flujo-detallados)
- [🧩 Referencia de Componentes Frontend](#-referencia-de-componentes-frontend)
- [🎨 Guía de Estilos CSS](#-guía-de-estilos-css)
- [🔧 Documentación de Workflows](#-documentación-de-workflows)
- [❓ Preguntas Frecuentes (FAQ)](#-preguntas-frecuentes-faq)
- [⚠️ Limitaciones conocidas](#️-limitaciones-conocidas)
- [🗺️ Roadmap](#️-roadmap)
- [📄 Licencia](#-licencia)
- [🙏 Fuente de Datos](#-fuente-de-datos)

---

# ✨ Demo en Vivo

| Entorno | URL | Propósito |
|---|---|---|
| GitHub Pages (dominio propio, DNS en Cloudflare) | [remedi.ar](https://remedi.ar) | Producción — alojado en GitHub |
| GitHub Pages (dominio por defecto) | [psbella.github.io/remediar](https://psbella.github.io/remediar/) | Mirror/respaldo |
| Cloudflare Workers | [remediar.pablo-s-bella.workers.dev](https://remediar.pablo-s-bella.workers.dev/) | Mirror/respaldo |

> **Headers de seguridad:** `remedi.ar` y `www.remedi.ar` están proxied (nube naranja) en Cloudflare, con GitHub Pages como origen. La CSP, `X-Frame-Options` y el resto de los headers de seguridad se aplican vía **Cloudflare Response Header Transform Rules** (dashboard), no desde el archivo `_headers` del repo — ese archivo solo lo procesa el mirror de Workers. Ver [`_headers`](./_headers) para el detalle de los valores replicados.

---

---

# 📊 Dataset actual

| Métrica | Valor |
|---|---|
| Registros | ~13.400 |
| Drogas únicas | ~1.830 |
| Tamaño JSON | ~3.8 MB |
| Tamaño gzip | ~345 KB |
| Con cobertura PAMI | ~6.400 (48%) |
| Entradas en blacklist | 710 |
| Cobertura parser de presentaciones | ~99.5% |
| Actualizaciones | 2 veces/día (lunes a viernes) |
| Tests de sanidad | 28 checks automáticos post-ETL |

---

# 🎯 Funcionamiento General

El sistema se compone de tres capas principales:

## 1️⃣ Extracción y procesamiento

- GitHub Actions ejecuta un workflow automático dos veces al día (lunes a viernes)
- Se descarga el PDF oficial desde SIAFAR / COFA
- Python extrae y normaliza los registros mediante un pipeline de 8+ capas
- Se cruzan los datos con el vademécum de PAMI para enriquecer cobertura
- Se genera `medicamentos.json`

---

## 2️⃣ Distribución

- El proyecto es 100% estático
- GitHub Pages sirve el contenido como origen (dominio propio `remedi.ar` vía DNS de Cloudflare, y el dominio por defecto `psbella.github.io/remediar`)
- Cloudflare actúa como proxy delante de `remedi.ar`/`www.remedi.ar`: CDN, TLS, y una Transform Rule que inyecta los headers de seguridad (GitHub Pages no soporta headers custom)
- Un mirror adicional corre en Cloudflare Workers (`remediar.pablo-s-bella.workers.dev`), sirviendo los mismos assets estáticos de forma independiente
- No existe backend persistente ni base de datos

---

## 3️⃣ Frontend SPA

- `index.html` carga la aplicación
- Los datos se descargan una sola vez y se indexan en memoria
- La búsqueda ocurre completamente del lado cliente
- El estado UI es reactivo mediante `store.js` (patrón pub/sub)

---

# 🧭 Principios del Proyecto

- Acceso libre a información de medicamentos
- Sin publicidad
- Analítica anónima, sin tracking de terceros
- Performance primero
- Mobile first
- Open source
- Infraestructura simple y transparente
- Datos públicos y auditables

---

# 👤 Flujo del Usuario

```mermaid
sequenceDiagram
    autonumber

    participant U as 👤 Usuario
    participant B as 🌐 Navegador
    participant CDN as ⚡ Cloudflare CDN
    participant CACHE as 💾 sessionStorage
    participant JSON as 📦 medicamentos.json
    participant STORE as 🧠 store.js
    participant UI as 🖥️ uiRenderer.js

    U->>B: Ingresa a remedi.ar

    B->>CDN: GET /index.html
    CDN-->>B: HTML + CSS + JS

    B->>B: Render inicial (skeleton)
    B->>STORE: Inicializar estado

    alt Caché válida (< 2 horas)
        B->>CACHE: Leer medicamentos.json
        CACHE-->>B: Datos cacheados
    else Caché vacía o vencida
        B->>CDN: GET /data/medicamentos.json
        CDN-->>B: JSON comprimido (~520KB gzip)
        B->>CACHE: Guardar datos + timestamp
    end

    B->>STORE: Indexar medicamentos
    STORE->>UI: Render primeros resultados

    U->>B: Escribe "ibuprofeno"

    B->>B: Debounce 250ms
    B->>STORE: Ejecutar búsqueda

    STORE->>STORE: Filtrar + ordenar
    STORE->>UI: Actualizar resultados + dropdowns

    U->>B: Activa filtro PAMI
    STORE->>STORE: Recalcular filtros
    STORE->>UI: Render reactivo

    U->>B: Click en medicamento
    UI-->>U: Mostrar detalles + badge PAMI
```

---

# 🧠 Algoritmo de Búsqueda y Filtrado

## Indexación inicial

`searchEngine.js` construye un índice invertido de prefijos sobre `droga`, `marca` y `laboratorio`. Por cada token de 2 o más caracteres se generan todos sus prefijos, mapeados a conjuntos de índices del array de medicamentos.

```javascript
for (const palabra of txt.split(/\s+/)) {
    for (let k = 2; k <= palabra.length; k++) {
        const pref = palabra.slice(0, k);
        if (!indice[pref]) indice[pref] = new Set();
        indice[pref].add(i);
    }
}
```

La búsqueda realiza una intersección AND entre todos los términos ingresados — "ibuprofeno bago" devuelve solo registros que contengan ambos tokens.

---

## Ranking de relevancia

Los resultados se ordenan por tres criterios en cascada:

1. **Relevancia textual** — score basado en el campo donde ocurre el match:

| Match | Score |
|---|---|
| Droga exacta | +100 |
| Droga empieza con el término | +80 |
| Droga contiene el término | +50 |
| Marca exacta | +40 |
| Marca empieza con el término | +25 |
| Marca contiene el término | +15 |
| Laboratorio contiene el término | +5 |

2. **vigencia_score** — productos con precios confiables primero
3. **precio** — ascendente como desempate final

Los registros con `vigencia_score < 50` siempre van al fondo, independientemente del score de relevancia.

---

# 🔄 Actualización Automática de Datos

## Workflow

```mermaid
flowchart TD

    A[⏰ Cron GitHub Actions]
    B[📥 Descargar PDF SIAFAR]
    C[📄 Extraer registros por página]
    D[🧹 Limpiar y normalizar]
    N1[🔧 Pipeline de normalización 8+ capas]
    BL[🛡️ Aplicar blacklist]
    E[🔍 Detectar outliers]
    F[💾 Generar medicamentos.json]
    R[📋 Generar outlier_report.json]
    CSV[🔬 Generar presentaciones_debug.csv]
    T[🧪 Tests de sanidad pytest]
    H[📤 Commit automático]
    I[🚀 GitHub Pages actualizado, servido vía proxy de Cloudflare]

    A --> B
    B --> C
    C --> D
    D --> N1
    N1 --> BL
    BL --> E
    E --> F
    E --> R
    E --> CSV
    F --> T
    T --> H
    R --> H
    CSV --> H
    H --> I
```

---

## Pipeline de normalización (8+ capas)

El parser aplica correcciones en cascada para resolver los problemas estructurales del PDF de SIAFAR:

| Capa | Función | Descripción |
|---|---|---|
| 0 | `reparar_droga_faltante()` | Cuando el PDF omite la línea del principio activo, todos los campos se desplazan. Separa droga+marca fusionadas usando un diccionario de prefijos truncados |
| 1 | Detección en parse | Detecta registros con 4 campos en lugar de 5 durante la extracción del PDF |
| 2 | `rescatar_laboratorios()` | Recupera `laboratorio="Desconocido"` buscando el lab como sufijo en `presentacion` |
| 3 | `reparar_denver()` | Denver Farma usa droga+lab como nombre comercial; separa marca y presentacion fusionadas (variantes DENCR., DF) |
| 4 | `reparar_marca_desplazada()` | Cuando `marca` empieza con dígito y `presentacion` está vacía, invierte el desplazamiento |
| 5 | `extraer_presentacion_de_marca()` | Extrae la presentacion fusionada en el campo marca. Antes del regex de corte: (1) separa laboratorios pegados sin espacio (`_build_re_lab_pegado()`, dinámico por dataset); (2) separa formas farmacéuticas pegadas (`_RE_FORMA_PEGADA`); (3) elimina duplicados mayúscula+minúscula (`_RE_TOKEN_DUPLICADO`) |
| 5b | `reparar_presentacion_desplazada()` | Separa presentacion+lab fusionados en el campo lab (3 sub-patrones: 2A, 2B, 2C) |
| 5c | `limpiar_dosis_residual_en_marca()` | Limpia la dosis numérica que queda pegada al nombre del laboratorio en `marca` |
| 6 | `crosswalk_pami()` | Cruza contra el vademécum de PAMI (descargado en cada corrida desde la API pública de datos abiertos, ver más abajo): recupera droga vacía, corrige laboratorio, normaliza `presentacion`, agrega `pami_cobertura` |
| 7 | `aplicar_droga_fixes()` | Aplica correcciones manuales desde `data/droga_fixes.json` |

> Cada una de estas funciones vive en su propio módulo dentro de `scripts/etl/` (ver [Paquete `scripts/etl/`](#paquete-scriptsetl-capas-de-normalización)); `pdf_to_json.py` solo orquesta el orden de ejecución.

---

## Workflow GitHub Actions

```yaml
name: 🔃 Actualizar precios

on:
  schedule:
    - cron: '30 13,21 * * 1-5'
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: repo-main-write
  cancel-in-progress: false

jobs:
  update:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7

      - name: Setup Python
        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Instalar dependencias
        run: pip install -r requirements.txt

      - name: Ejecutar pdf_to_json.py
        run: python scripts/pdf_to_json.py

      - name: Generar landings + sitemap
        run: python scripts/generar_landings.py

      - name: Subir debug a GitHub Releases
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/subir_debug.py

      - name: Verificar sanidad del output
        run: pytest tests/ -v

      - name: Snapshot semanal (solo viernes)
        if: github.event_name == 'schedule'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if [ "$(date +%u)" = "5" ]; then
            echo "Viernes detectado — generando snapshot semanal..."
            python scripts/snapshot_semanal.py
          else
            echo "No es viernes, saltando snapshot."
          fi

      - name: Commit y push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "actions@github.com"
          git add data/medicamentos.json
          git add data/outlier_report.json
          git add data/presentaciones_debug.csv
          git add *.html
          git add sitemap.xml
          git commit -m "Actualizar precios $(date +'%Y-%m-%d')" || echo "No changes"
          git pull --rebase origin "${{ github.ref_name }}"
          git push origin "${{ github.ref_name }}"
```

---

# 📦 Estructura de Datos JSON

## Ejemplo de registro

```json
{
  "droga": "ibuprofeno",
  "marca": "IBUPIRAC",
  "presentacion": "400 mg comp.x 20",
  "laboratorio": "Pfizer",
  "precio": 9800.50,
  "pami_cobertura": 55,
  "pres_forma": "COMPRIMIDOS",
  "pres_dosis": "400",
  "pres_unidad": "MG",
  "pres_cantidad": "20",
  "vigencia_score": 100,
  "flags": [],
  "precio_outlier_tipo": null,
  "outlier_razones": []
}
```

---

## Campos

| Campo | Tipo | Descripción |
|---|---|---|
| `droga` | string | Principio activo (nombre genérico) |
| `marca` | string | Nombre comercial |
| `presentacion` | string | Dosis, forma farmacéutica y cantidad |
| `laboratorio` | string | Laboratorio fabricante |
| `precio` | number | PVP en ARS (fuente: SIAFAR) |
| `pami_cobertura` | number\|null | Porcentaje de cobertura PAMI (ej: 55). Null si no está en el vademécum |
| `pres_forma` | string\|null | Forma farmacéutica parseada (ej: `"COMPRIMIDOS RECUBIERTOS"`, `"JARABE"`) |
| `pres_dosis` | string\|null | Dosis numérica (ej: `"400"`, `"500"`) |
| `pres_unidad` | string\|null | Unidad de la dosis (ej: `"MG"`, `"ML"`, `"UI"`) |
| `pres_cantidad` | string\|null | Cantidad de unidades (ej: `"20"`, `"100 ml"`) |
| `vigencia_score` | number | Score de confiabilidad del precio (0-100). < 50 = outlier |
| `flags` | array | Etiquetas de anomalía (`precio_bajo`, `precio_sospechoso`, `precio_obsoleto`) |
| `precio_outlier_tipo` | string\|null | Categoría del outlier detectado |
| `outlier_razones` | array | Descripción de por qué es outlier |

---

## Archivos de referencia

| Archivo | Descripción |
|---|---|
| `data/pami.xlsx` | Vademécum PAMI, descargado automáticamente en cada corrida desde la [API de datos abiertos de PAMI](https://datos.pami.org.ar/dataset/medicamentos-para-afiliados) (no se versiona en git). Usado para: (1) cobertura por marca+presentacion, (2) recuperar droga faltante, (3) corregir laboratorio, (4) normalizar el campo `presentacion` |
| `data/droga_fixes.json` | Correcciones manuales marca→droga para casos no resolubles con regex |
| `data/blacklist.json` | 710 registros excluidos manualmente. Las claves usan el formato `droga\|marca\|presentacion\|laboratorio` en minúsculas |
| `data/outlier_report.json` | Reporte detallado de outliers de la última corrida |
| `data/presentaciones_debug.csv` | Auditoría del parser: `presentacion_original` vs. campos parseados (`forma`, `dosis`, `unidad`, `cantidad`) |
| `.debug/medicamentos.pretty.json` | Versión formateada con `indent=2` del dataset, solo para debug local — **no se publica** en el sitio ni se versiona en git |

### Cómo agregar una corrección a `droga_fixes.json`

`droga_fixes.json` es editable manualmente — no hace falta tocar el código para cubrir nuevas marcas sin principio activo en el PDF.

Dos formatos soportados:

```json
// Solo droga (la marca ya está bien parseada)
"FORXIGA": "dapagliflozina"

// Droga + corrección de marca (droga y marca estaban fusionadas)
"DICLOFENAC POTÁSICO, PARACETAM KINALGIN P": {
  "droga": "diclofenac potásico, paracetamol",
  "marca": "KINALGIN P"
}
```

La clave es siempre el valor del campo `marca` o `droga` en mayúsculas tal como aparece en el JSON. El workflow lo aplica automáticamente en cada corrida.

---

# ⚡ Optimizaciones Implementadas

## ✅ Búsqueda en memoria

El JSON se carga una sola vez y se indexa en memoria con un índice invertido de prefijos. Sin requests adicionales para cada búsqueda.

## ✅ Estado centralizado

`store.js` controla búsqueda, filtros, ordenamiento y render reactivo con un patrón pub/sub manual — sin dependencias externas.

## ✅ Debounce

La búsqueda espera 250ms luego de la última tecla para no saturar el índice.

## ✅ Caché sessionStorage

Los datos se almacenan en `sessionStorage` con TTL de 2 horas. La clave `remedios_data_v2` permite invalidar el caché en deploys sin romper sesiones activas.

## ✅ Dropdowns contextuales

Al buscar un medicamento, los filtros de presentación y laboratorio se actualizan para mostrar solo las opciones disponibles en los resultados actuales.

## ✅ Mobile first

CSS optimizado para móviles, tablets y desktop sin frameworks externos.

## ✅ Renderizado progresivo

300 resultados por render para no bloquear el hilo principal. Los outliers (`vigencia_score < 50`) siempre aparecen al final, independientemente del orden seleccionado.

## ✅ Filtros sin texto

Seleccionar laboratorio o presentación desde el desplegable muestra resultados aunque el campo de búsqueda esté vacío.

## ✅ PWA completa

Service Worker con estrategia network-first para datos y cache-first para assets estáticos. Íconos en SVG + PNG (192×192 y 512×512) para instalación en todos los dispositivos.

## ✅ Seguridad en headers HTTP

CSP via header HTTP (no meta tag) con hash SHA256 del script inline de GA. `style-src` sin `unsafe-inline` (estilos migrados a CSS externo). `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` y `Access-Control-Allow-Origin: *` para el JSON público. ⚠️ En producción (`remedi.ar`/`www.remedi.ar`) estos headers los aplica una Cloudflare Response Header Transform Rule, no el archivo `_headers` del repo — [ver por qué](#por-qué-github-pages--cloudflare-como-proxy).

## ✅ Compartir medicamentos

Cada tarjeta tiene un botón "Compartir" que abre el menú nativo en mobile o copia el link al portapapeles en desktop. Cada medicamento tiene una URL única con hash (`remedi.ar/#droga--marca--laboratorio--presentacion`). Al abrir un link compartido, el medicamento aparece destacado arriba con glow teal y productos similares debajo. Los eventos de compartir se registran en GA4.

## ✅ Tests de sanidad automáticos

31 tests pytest corren después de cada actualización del ETL y antes del commit. Si alguno falla, el workflow se detiene y el sitio sigue sirviendo los datos anteriores. 12 validan umbrales de calidad de negocio (cantidad de registros, % de campos vacíos, rango de precios), 1 valida el contrato estructural completo del JSON contra un [JSON Schema versionado](./tests/medicamentos.schema.json), y 18 son tests unitarios de las funciones puras de scripts/etl/ — si el ETL cambia la forma del output o rompe una función de reparación, alguno de estos avisa.
```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
collected 31 items
tests/test_etl_modulos.py::test_limpiar_precio_formato_argentino PASSED  [  3%]
tests/test_etl_modulos.py::test_limpiar_precio_valores_invalidos PASSED  [  6%]
tests/test_etl_modulos.py::test_es_precio PASSED                        [  9%]
tests/test_etl_modulos.py::test_make_key_normaliza_case_y_espacios PASSED [ 12%]
tests/test_etl_modulos.py::test_parece_corrupta_texto_limpio_no_marca_nada PASSED [ 16%]
tests/test_etl_modulos.py::test_parece_corrupta_detecta_mojibake_clasico PASSED [ 19%]
tests/test_etl_modulos.py::test_parece_corrupta_detecta_variantes_que_el_filtro_viejo_no_veia PASSED [ 22%]
tests/test_etl_modulos.py::test_filtrar_blacklist_excluye_por_key PASSED [ 25%]
tests/test_etl_modulos.py::test_filtrar_blacklist_vacia_no_toca_nada PASSED [ 29%]
tests/test_etl_modulos.py::test_calcular_stats_por_droga_mediana_correcta PASSED [ 32%]
tests/test_etl_modulos.py::test_evaluar_outlier_precio_invalido PASSED   [ 35%]
tests/test_etl_modulos.py::test_evaluar_outlier_precio_normal_no_marca_nada PASSED [ 38%]
tests/test_etl_modulos.py::test_evaluar_outlier_precio_criticamente_bajo PASSED [ 41%]
tests/test_etl_modulos.py::test_separar_droga_marca_con_prefijo_conocido PASSED [ 45%]
tests/test_etl_modulos.py::test_separar_droga_marca_sin_match_devuelve_none PASSED [ 48%]
tests/test_etl_modulos.py::test_reparar_denver_variante_a_presentacion_pegada_a_marca PASSED [ 51%]
tests/test_etl_modulos.py::test_reparar_denver_no_toca_otros_laboratorios PASSED [ 54%]
tests/test_etl_modulos.py::test_deduplicar_elimina_solo_duplicados_exactos PASSED [ 58%]
tests/test_etl_sanidad.py::test_cantidad_minima PASSED                  [ 61%]
tests/test_etl_sanidad.py::test_cantidad_maxima PASSED                  [ 64%]
tests/test_etl_sanidad.py::test_campos_presentes PASSED                 [ 67%]
tests/test_etl_sanidad.py::test_precios_positivos PASSED                [ 70%]
tests/test_etl_sanidad.py::test_precio_mediana_razonable PASSED         [ 74%]
tests/test_etl_sanidad.py::test_drogas_vacias PASSED                    [ 77%]
tests/test_etl_sanidad.py::test_laboratorios_desconocidos PASSED        [ 80%]
tests/test_etl_sanidad.py::test_marcas_vacias PASSED                    [ 83%]
tests/test_etl_sanidad.py::test_vigencia_score_rango PASSED             [ 87%]
tests/test_etl_sanidad.py::test_pami_cobertura_rango PASSED             [ 90%]
tests/test_etl_sanidad.py::test_estructura_raiz PASSED                  [ 93%]
tests/test_etl_sanidad.py::test_fecha_presente PASSED                   [ 96%]
tests/test_schema.py::test_schema_valido PASSED                         [100%]
31 passed in 1.58s
```
---

# ⏱️ Tiempos de Respuesta

| Métrica | Valor |
|---|---|
| FCP | 0.8 - 1.2s |
| LCP | 1.5 - 2.0s |
| TTI | 1.8 - 2.5s |
| Búsqueda en índice | 25 - 100ms |
| TTFB | 50 - 150ms |

---

# 🏗️ Arquitectura del Sistema

```mermaid
flowchart LR

    subgraph ONE["🌐 FUENTE EXTERNA"]
        A[("SIAFAR / COFA\nPDF Oficial")]
        B["📄 Publicación diaria"]
    end

    subgraph TWO["⚙️ AUTOMATIZACIÓN"]
        C["⏰ Cron GitHub Actions\n10:30 y 18:30 AR"]
        D["🔄 Workflow manual"]
    end

    subgraph THREE["🐍 ETL Python"]
        E["pdf_to_json.py\n(orquestador)"]
        E2["scripts/etl/\n8+ capas normalización\nen módulos independientes"]
        G["📊 medicamentos.json"]
    end

    subgraph REF["📋 REFERENCIA"]
        H["Vademécum PAMI\n(API, descarga en runtime)"]
        I["droga_fixes.json"]
        J["blacklist.json (710)"]
    end

    subgraph ATC["🏷️ CLASIFICACIÓN ATC (generado offline)"]
        H2["info_adicional.json\n(laboratorio, droga(s), clases)"]
        I2["atc_por_droga.json\n(dataset propio, fuente ANMAT)"]
    end

    subgraph FIVE["🌐 FRONTEND"]
        K["index.html"]
        L["store.js (pub/sub)"]
        M["searchEngine.js\n(índice invertido)"]
        N["uiRenderer.js"]
    end

    subgraph SEVEN["☁️ HOSTING"]
        Q["GitHub Pages\n(origen real)"]
        R["Cloudflare\n(proxy + headers de seguridad)"]
    end

    A --> B
    B --> C
    D --> C
    C --> E
    E --> E2
    H --> E2
    I --> E2
    J --> E2
    E2 --> G
    G --> K
    K --> L
    L --> M
    M --> N
    H2 --> N
    I2 --> N
    G --> Q
    Q --> R
```

---

# 📁 Estructura del Repositorio

```text
remediar/
├── index.html
├── manifest.json
├── requirements.txt
├── robots.txt
├── sitemap.xml           # generado por scripts/generar_landings.py
├── sitemap.xsl           # transforma sitemap.xml en tabla HTML legible en el navegador
├── sw.js
├── privacidad.html
├── terminos.html
├── about.html
├── admin-panel.html      # panel interno (outliers/lista negra), noindex, auth por GitHub PAT
├── mantenimiento.html    # pagina de mantenimiento, se copia a index.html vía workflow
├── {droga}.html          # 100 landing pages SEO (una por droga), generadas — ver más abajo
├── README.md
├── _headers
├── .nojekyll
├── .gitignore
│
├── css/
│   ├── style.css
│   ├── admin-panel.css
│   └── mantenimiento.css
│
├── img/
│   ├── favicon.svg
│   ├── logo_banner.svg
│   ├── icon-192.png
│   ├── icon-512.png
│   └── og-image.png
│
├── js/
│   ├── main.js
│   ├── store.js
│   ├── dataLoader.js
│   ├── filters.js
│   ├── searchEngine.js
│   ├── uiRenderer.js
│   ├── utils.js
│   ├── about.js
│   ├── admin-panel.js
│   ├── landing.js        # compartido por las 100 landing pages
│   ├── infoAdicional.js  # modal "+Info" (laboratorio, droga, clases terapéuticas)
│   └── atcClasificacion.js  # jerarquía ATC oficial ANMAT en el modal +Info
│
├── data/
│   ├── medicamentos.json
│   ├── outlier_report.json
│   ├── presentaciones_debug.csv
│   ├── blacklist.json
│   ├── droga_fixes.json
│   ├── pami.xlsx          # descargado en runtime, no versionado
│   ├── atc/
│   │   ├── atc_por_droga.json   # clasificación ATC propia por droga
│   │   └── atc_niveles.json     # jerarquía Nivel1-4 (dataset codigos-atc-anmat)
│   └── info-adicional/
│       └── info_adicional.json  # laboratorio, droga(s), clases terapéuticas por medicamento
│
├── scripts/
│   ├── pdf_to_json.py       # orquestador: encadena las capas de etl/
│   ├── generar_landings.py  # genera las 100 landing pages + sitemap.xml
│   ├── github_release_helper.py  # helper compartido de releases (usado por snapshot_semanal.py y subir_debug.py)
│   ├── subir_debug.py
│   ├── checks/
│   │   └── a11y-check.mjs   # chequeo de accesibilidad con axe-core, no bloqueante
│   ├── mantenimiento/
│   │   └── fix_blacklist_encoding.py  # reparación puntual de encoding en blacklist.json
│   ├── etl/
│   │   ├── config.py            # constantes y paths compartidos
│   │   ├── parser.py             # descarga del PDF y parseo a lista de medicamentos
│   │   ├── reparaciones.py       # capas de reparación de campos mal parseados
│   │   ├── droga_fixes.py        # fixes manuales + reparación de droga faltante
│   │   ├── presentacion.py       # extracción/parseo/debug de presentaciones
│   │   ├── pami.py               # crosswalk contra el vademécum PAMI
│   │   ├── blacklist.py          # carga y filtrado de la lista negra
│   │   ├── outliers.py           # detección de outliers y cálculo de vigencia
│   │   ├── enriquecimiento.py    # enriquecimiento de campos de presentación/dosis
│   │   └── utils.py              # helpers de parseo/limpieza básicos
│   └── snapshot_semanal.py
│
├── tests/
│   ├── conftest.py
│   ├── test_etl_sanidad.py
│   ├── test_schema.py
│   └── medicamentos.schema.json
│
└── .github/workflows/
    ├── update_prices.yml
    ├── maintenance-on.yml
    ├── maintenance-off.yml
    ├── accessibility.yml
    └── codeql.yml
```

---

# 🧰 Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | HTML5 + CSS3 + Vanilla JS (ES Modules) |
| Estado UI | Patrón pub/sub manual (`store.js`) |
| Backend ETL | Python 3.11 |
| Parsing PDF | PyMuPDF |
| Crosswalk PAMI | pandas + openpyxl |
| Datos | JSON estático |
| CI/CD | GitHub Actions |
| Testing | pytest |
| Lint | Ruff (Python) + ESLint (JS) — configurados, no bloquean CI |
| Hosting | GitHub Pages (origen) + Cloudflare (proxy/DNS) + Cloudflare Workers (mirror) |
| SEO | JSON-LD + Open Graph + Twitter Cards |
| Caché | sessionStorage (TTL 2h) + Service Worker |
| Seguridad | CSP via header HTTP + SHA256 hash |
| PWA | Service Worker + Web App Manifest |

---

# 🧠 Decisiones Técnicas

## ¿Por qué Vanilla JS?

- Cero dependencias en runtime
- Mejor tiempo de carga
- Sin actualizaciones de seguridad por dependencias transitivas
- Mantenimiento sencillo a largo plazo

## ¿Por qué JSON plano y no base de datos?

- Hosting estático con costo prácticamente cero
- CDN extremadamente eficiente
- Menor complejidad operacional
- El dataset (~13.400 registros) cabe perfectamente en memoria

## ¿Por qué 8+ capas de normalización?

El PDF de SIAFAR no tiene un esquema tabular estricto. Distintos laboratorios omiten campos, fusionan droga+marca sin separador, o desplazan la presentación al campo laboratorio. Las capas se aplican en cascada de menor a mayor complejidad, garantizando que cada corrección no interfiera con las anteriores.

## ¿Por qué GitHub Pages + Cloudflare como proxy?

- GitHub Pages es gratuito, confiable, y ya aloja el repo — cero infraestructura extra que mantener
- **Importante**: GitHub Pages **no soporta un archivo `_headers`** para headers HTTP personalizados (esa convención es de Cloudflare Pages/Netlify, no de GitHub Pages). El archivo [`_headers`](./_headers) del repo documenta los valores deseados, pero quien los aplica de verdad en `remedi.ar`/`www.remedi.ar` es una **Cloudflare Response Header Transform Rule**, configurada en el dashboard (no en el repo) — ver la nota en la sección de Arquitectura
- Cloudflare como proxy (nube naranja) suma CDN global, HTTPS gestionado, y la posibilidad de inyectar esos headers sin tocar el origen
- El mirror en Cloudflare Workers (`remediar.pablo-s-bella.workers.dev`) sirve como respaldo independiente: al ser Workers Static Assets, sí procesa el `_headers` del repo nativamente, así que ese archivo no queda del todo huérfano

---

# 💻 Ejecución Local

## Python (servidor de desarrollo)

```bash
git clone https://github.com/psbella/remediar.git
cd remediar
python -m http.server 8000
```

## Node.js

```bash
npx http-server -p 8000 --cors -c-1
```

## Ejecutar el ETL manualmente

```bash
pip install -r requirements.txt
python scripts/pdf_to_json.py
```

## Ejecutar los tests

```bash
pytest tests/ -v
```

## Docker

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
```

```bash
docker build -t remediar .
docker run -p 8080:80 remediar
```

---

# 🐍 Scripts Python

| Script | Función |
|---|---|
| `scripts/pdf_to_json.py` | Orquestador: encadena las capas de `scripts/etl/` en orden y persiste `medicamentos.json`, `outlier_report.json` y `presentaciones_debug.csv`. Ya no contiene la lógica de las capas — solo el flujo. |
| `scripts/snapshot_semanal.py` | Genera un CSV con los precios confiables (`vigencia_score ≥ 50`) de la semana y lo sube como asset a la release mensual de GitHub (`historial-YYYY-MM`). Se ejecuta automáticamente cada viernes. |
| `scripts/generar_landings.py` | Genera las 100 landing pages estáticas (una por droga) a partir de `medicamentos.json`, y regenera `sitemap.xml` con las 100 URLs. Ver [Landing pages (long-tail SEO)](#landing-pages-long-tail-seo). |
| `scripts/github_release_helper.py` | Funciones compartidas para crear/obtener releases de GitHub y subir/reemplazar/verificar assets. Usado por `snapshot_semanal.py` y `subir_debug.py`, no se ejecuta directamente. |
| `scripts/checks/a11y-check.mjs` | Chequeo de accesibilidad con axe-core + Puppeteer contra las páginas estáticas servidas localmente. No bloquea el CI (mismo criterio que Ruff/ESLint en este repo) — avisa, no rompe el build. |
| `scripts/mantenimiento/fix_blacklist_encoding.py` | Reparación puntual de entradas con encoding corrupto en `blacklist.json`, vía cross-reference e historial de git. Ejecución manual, no forma parte del pipeline automático. |
| `tests/test_etl_sanidad.py` | 12 tests de sanidad sobre el output del ETL: cantidad de registros, campos obligatorios, rangos de precios, calidad de datos y estructura del JSON |

### Paquete `scripts/etl/` (capas de normalización)

| Módulo | Función |
|---|---|
| `etl/config.py` | Constantes y paths compartidos por todos los módulos del ETL |
| `etl/parser.py` | Descarga del PDF de SIAFAR, parseo a lista de medicamentos y deduplicación de registros exactos |
| `etl/reparaciones.py` | Capas de reparación de campos mal parseados desde el PDF (laboratorios desplazados, fusiones Denver Farma, marca desplazada, presentación desplazada) |
| `etl/droga_fixes.py` | Fixes manuales de droga y reparación de registros con droga faltante |
| `etl/presentacion.py` | Extracción de presentación fusionada en marca, limpieza de dosis residual y generación del debug de presentaciones |
| `etl/pami.py` | Crosswalk contra el vademécum PAMI vigente para recuperar droga y corregir laboratorio |
| `etl/blacklist.py` | Carga y filtrado de la lista negra de medicamentos |
| `etl/outliers.py` | Detección de precios outlier/obsoletos y cálculo de vigencia |
| `etl/enriquecimiento.py` | Enriquecimiento de registros con campos de presentación y dosis |
| `etl/utils.py` | Helpers de parseo y limpieza básicos |

---

# 📊 Métricas y Rendimiento

| Métrica | Valor |
|---|---|
| Lighthouse Performance | 94-96 |
| Accessibility | 98 |
| Best Practices | 100 |
| SEO | 100 |
| CLS | 0.02 |
| FID | 12ms |

---

# 🔍 SEO y Metadatos

## Implementaciones

- JSON-LD (`WebSite` + `SearchAction`)
- Open Graph
- Twitter Cards
- Sitemap.xml (+ visor HTML vía XSL, ver más abajo)
- robots.txt con `crawl-delay` para bots agresivos
- 100 landing pages estáticas para long-tail SEO (ver más abajo)

## Landing pages (long-tail SEO)

Además de la SPA (`index.html`), el sitio publica **100 páginas estáticas**, una por droga (`omeprazol.html`, `metformina.html`, `ibuprofeno.html`, etc.), pensadas para capturar búsquedas del tipo *"precio de X en Argentina"* que no indexan bien contra una SPA con contenido cargado por JS.

- Generadas por `scripts/generar_landings.py` a partir de `data/medicamentos.json` — no se editan a mano
- Cada landing incluye: precio min/prom/max, tabla de marcas y laboratorios, FAQ, drogas relacionadas, JSON-LD `Drug` + `BreadcrumbList`, y metadatos Open Graph/Twitter propios
- Comparten `js/landing.js` (volver arriba, scroll de tabla, buscador de footer) en vez de JS inline, cubierto por `script-src 'self'` en la CSP sin necesidad de hash
- El mismo script regenera `sitemap.xml` con las 100 URLs (prioridad `0.9`) + home (`1.0`) + páginas institucionales (`0.5`/`0.3`)
- Un mapeo manual (`SLUG_A_DROGA_REAL` en el script) resuelve los casos donde el slug de la URL no coincide textualmente con el campo `droga` del dataset (tildes, combos con coma, truncamientos del PDF de origen)

```mermaid
flowchart LR
    A["📦 medicamentos.json"]
    B["🐍 generar_landings.py"]
    C["📄 100 landing pages\n{droga}.html"]
    D["🗺️ sitemap.xml\n100 URLs + home + institucionales"]
    E["🎨 sitemap.xsl\n(vista humana en navegador)"]

    A --> B
    B --> C
    B --> D
    D -.->|"<?xml-stylesheet?>"| E
```

Se ejecuta automáticamente como parte de `update_prices.yml`, inmediatamente después de `pdf_to_json.py` — es decir, las 100 landings y el sitemap se regeneran en cada corrida del ETL (dos veces al día), no solo cuando cambia el catálogo de drogas.

## Sitemap legible (`sitemap.xsl`)

`sitemap.xml` referencia una hoja de estilos XSL (`<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>`) que transforma el XML en una tabla HTML cuando se abre en un navegador. Los crawlers (Google incluido) ignoran esa instrucción y parsean el XML crudo sin cambios — es puramente para inspección manual (Search Console, debugging). Ver el XML sin la vista con `view-source:` antes de la URL.

## Ejemplo JSON-LD

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "remedi.ar",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://remedi.ar/?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
```

---

# 🔒 Seguridad y Privacidad

- No se recopilan datos personales
- No se utilizan cookies de tracking
- No existe backend persistente
- Todo el frontend es auditable públicamente
- **Content Security Policy** via header HTTP con hash SHA256 de los dos scripts inline ejecutables (config de Google Analytics y registro del Service Worker): `script-src 'self' 'sha256-...' 'sha256-...' https://www.googletagmanager.com`. El script JSON-LD no necesita hash: no es JavaScript ejecutable.
- **CORS** habilitado en `/data/medicamentos.json` para consumo externo (`Access-Control-Allow-Origin: *`)
- `robots.txt` bloquea explícitamente GPTBot y ClaudeBot
- Google Analytics configurado en modo anónimo — ver [política de privacidad](https://remedi.ar/privacidad.html)

---

# 🔌 API No Oficial

El JSON de medicamentos es público y accesible libremente bajo licencia MIT.

## Endpoints

| Método | URL |
|---|---|
| GET | https://remedi.ar/data/medicamentos.json |
| GET | https://raw.githubusercontent.com/psbella/remediar/main/data/medicamentos.json |

## JavaScript

```javascript
const response = await fetch('https://remedi.ar/data/medicamentos.json');
const { medicamentos } = await response.json();

// Filtrar por droga con cobertura PAMI
const conPami = medicamentos.filter(m => m.pami_cobertura > 0);

// Calcular copago PAMI
const copago = m => Math.round(m.precio * (1 - m.pami_cobertura / 100));

// Filtrar por forma farmacéutica
const comprimidos = medicamentos.filter(m => m.pres_forma?.includes('COMPRIMIDOS'));
```

## Python

```python
import pandas as pd

df = pd.read_json("https://remedi.ar/data/medicamentos.json")
meds = pd.json_normalize(df['medicamentos'])

# Filtrar solo los que tienen cobertura PAMI
con_pami = meds[meds['pami_cobertura'].notna()]
```

---

# 👥 Guía de Contribución

## Reportar un problema

- **¿Un precio, laboratorio o cobertura PAMI están mal?** Abrí un issue con el template ["🩺 Precio o dato incorrecto"](.github/ISSUE_TEMPLATE/dato_incorrecto.md) — es el tipo de reporte más útil para este proyecto.
- **¿Algo no funciona en la web?** Usá el template ["🐛 Bug del sitio"](.github/ISSUE_TEMPLATE/bug.md).
- **¿Una idea o mejora?** Template ["💡 Idea o mejora"](.github/ISSUE_TEMPLATE/idea.md) — revisá primero el [Roadmap](#️-roadmap) por si ya está anotado.

## Flujo

```bash
git clone https://github.com/psbella/remediar.git
git checkout -b feature/nueva-funcion
# hacer cambios
git commit -m "feat: descripción del cambio"
git push origin feature/nueva-funcion
# abrir Pull Request (se completa solo con el template del repo)
```

Antes de abrir el PR: si tocaste el ETL, corré `pytest tests/` y confirmá que pasen los 31 tests (12 de sanidad + 1 de schema + 18 unitarios de scripts/etl/); si tocaste JS/CSS/HTML, probá el cambio en el navegador, no alcanza con leer el diff. También conviene correr `ruff check .` (Python) y `eslint js/` (JS) — todavía no bloquean el CI, pero sirven para agarrar errores antes de mergear.

## Convenciones de commits

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Documentación |
| `perf` | Performance |
| `chore` | Mantenimiento / limpieza |
| `security` | Cambios de seguridad |

## Sobre la rama `main`

`main` no tiene branch protection activa. Es una decisión consciente: el repo tiene un solo colaborador con acceso de escritura, y GitHub no permite eximir al bot de `github-actions` de las reglas de protección en cuentas personales — activarla hubiera roto el workflow automático que pushea 2 veces al día. Si en algún momento se suma otro colaborador con acceso de escritura, esto se reevalúa.

## ⚠️ Ojo con el Service Worker al tocar assets estáticos

Si modificás `index.html`, `css/style.css` o cualquier archivo en `js/`, **acordate de bumpear `CACHE_NAME` en `sw.js`** (ej. `remediar-v7` → `remediar-v8`). Esos archivos están precacheados por el Service Worker (`CACHE_STATIC`), así que sin el bump los usuarios que ya visitaron el sitio van a seguir viendo la versión vieja indefinidamente, sin ningún error visible — simplemente no se actualiza nada hasta que el navegador decida revalidar el cache por su cuenta.

---

# 📊 Diagramas de Flujo Detallados

## Pipeline ETL completo

```mermaid
flowchart TD

    A[PDF SIAFAR]
    B[Descarga + extracción por página]
    C0[Capa 0: reparar_droga_faltante]
    C1[Capa 1: desplazamiento en parse]
    C2[Capa 2: rescatar_laboratorios]
    C3[Capa 3: reparar_denver]
    C4[Capa 4: reparar_marca_desplazada]
    C5[Capa 5: extraer_presentacion_de_marca]
    C5B[Capa 5b: reparar_presentacion_desplazada]
    C5C[Capa 5c: limpiar_dosis_residual_en_marca]
    C6[Capa 6: crosswalk_pami]
    C7[Capa 7: aplicar_droga_fixes]
    BL[Blacklist 710 entradas]
    OUT[Detección de outliers IQR]
    PRES[Parser de presentaciones]
    T[🧪 pytest 31 tests]
    JSON[medicamentos.json]
    DEBUG[presentaciones_debug.csv]
    REPORT[outlier_report.json]

    A --> B
    B --> C0
    C0 --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5
    C5 --> C5B
    C5B --> C5C
    C5C --> C6
    C6 --> C7
    C7 --> BL
    BL --> OUT
    OUT --> PRES
    PRES --> T
    T --> JSON
    PRES --> DEBUG
    OUT --> REPORT
```

---

## Detalle de la Capa 5: extraer_presentacion_de_marca

```mermaid
flowchart TD
    IN["marca='CARBOPLATINO MICROSULES150 mg iny.f.a.x 1'\npresentacion=''"]

    subgraph PRE["Pre-limpieza (en orden)"]
        A["1. _RE_TOKEN_DUPLICADO\nElimina token mayúscula duplicado\nGELgel → gel\nBOLSAbolsa → bolsa"]
        B["2. _RE_FORMA_PEGADA\nInserta espacio antes de forma pegada\nBENZOCAINA GELgel → BENZOCAINA gel"]
        C["3. _build_re_lab_pegado (dinámico)\nInserta espacio entre lab conocido y dosis pegada\nMICROSULES150 → MICROSULES 150"]
    end

    D{"¿_RE_EXTRAER_PRES\nhace match?"}
    E["marca = grupo 1\npresentacion = grupo 2"]
    F["Registro sin cambios\n(caso no resuelto)"]

    IN --> A --> B --> C --> D
    D -- Sí --> E
    D -- No --> F

    style PRE fill:#f0f8f0,stroke:#aaa
```

El regex `_build_re_lab_pegado` se construye dinámicamente en cada corrida a partir de los laboratorios ya presentes en el dataset. Esto evita mantener una lista hardcodeada que se desactualiza.

---

## Parser de presentaciones

```mermaid
flowchart TD
    P["presentacion: '400 mg comp.rec.x 20'"]
    P1["Normalizar prefijos: Ad. Ped. Rtd."]
    P2["Extraer dosis + unidad"]
    P3["Buscar forma farmacéutica en FORMAS_MAP (60+ entradas)"]
    P4{"¿Forma encontrada?"}
    P5["Fallback: scan en cualquier posición"]
    P6["Extraer cantidad"]
    P7["pres_forma / pres_dosis / pres_unidad / pres_cantidad"]

    P --> P1 --> P2 --> P3 --> P4
    P4 -- Sí --> P6
    P4 -- No --> P5 --> P6
    P6 --> P7
```

| Campo generado | Ejemplo |
|---|---|
| `pres_forma` | `"COMPRIMIDOS RECUBIERTOS"` |
| `pres_dosis` | `"400"` |
| `pres_unidad` | `"MG"` |
| `pres_cantidad` | `"20"` |

Cobertura actual: **~99.5%**. El archivo `data/presentaciones_debug.csv` permite auditar los casos no resueltos después de cada corrida.

---

## Ciclo de vida de una búsqueda

```mermaid
sequenceDiagram
    participant U as 👤 Usuario
    participant M as main.js
    participant S as store.js
    participant SE as searchEngine.js
    participant F as filters.js
    participant R as uiRenderer.js

    U->>M: input "ibuprofeno bago"
    M->>M: debounce 250ms
    M->>S: setFiltroTexto("ibuprofeno bago")

    S->>SE: buscar("ibuprofeno bago")
    Note over SE: Normaliza → ["ibuprofeno","bago"]
    Note over SE: Intersección AND de índices de prefijos
    Note over SE: Ordena por relevancia + vigencia + precio
    SE-->>S: resultados ordenados

    S->>F: aplicarFiltros(resultados, presentacion, laboratorio, soloPami)
    F-->>S: resultados filtrados

    S->>S: notificar()
    S->>R: suscribirse callback

    R->>R: cargarOpcionesFiltros(resultados)
    Note over R: Dropdowns muestran solo opciones del resultado actual
    R->>R: mostrarResultados(resultados)
    Note over R: renderPresentacion() y renderPrecios() — funciones nombradas
    R-->>U: Tarjetas con chips de presentación + badge PAMI
```

---

## Flujo reactivo del store

```mermaid
flowchart TD
    subgraph ACCIONES["Acciones"]
        A1[setFiltroTexto]
        A2[setFiltroPresentacion]
        A3[setFiltroLaboratorio]
        A4[setFiltroOrden]
        A5[setSoloPami]
        A6[limpiarFiltros]
    end

    subgraph RECALC["recalcularResultados()"]
        R1{"¿hay texto\no filtro activo?"}
        R2["buscar(texto)\n→ índice invertido"]
        R3["todos los medicamentos"]
        R4["aplicarFiltros()"]
        R5{"orden ≠\n'relevancia'?"}
        R6["ordenar()"]
        R7["state.resultados = …"]
    end

    subgraph UI["UI (suscriptores)"]
        U1["cargarOpcionesFiltros()"]
        U2["mostrarResultados()"]
        U3["mostrarMensajeInicial()"]
    end

    ACCIONES --> RECALC
    R1 -- No --> U3
    R1 -- hayTexto --> R2 --> R4
    R1 -- soloFiltros --> R3 --> R4
    R4 --> R5
    R5 -- Sí --> R6 --> R7
    R5 -- No --> R7
    R7 --> notificar
    notificar --> U1
    notificar --> U2
```

---

## Anatomía de un registro

```mermaid
flowchart LR
    subgraph SIAFAR["📄 SIAFAR / PDF"]
        S1[droga]
        S2[marca]
        S3[presentacion]
        S4[laboratorio]
        S5[precio]
    end

    subgraph PAMI["📋 Vademécum PAMI (API)"]
        P1[pami_cobertura]
        P2["droga (recuperación)"]
        P3["laboratorio (corrección)"]
        P4["presentacion (normalización)"]
    end

    subgraph PARSER["🔧 _parsear_presentacion()"]
        PR1[pres_forma]
        PR2[pres_dosis]
        PR3[pres_unidad]
        PR4[pres_cantidad]
    end

    subgraph OUTLIER["📊 Detección outliers (IQR)"]
        O1[vigencia_score]
        O2[flags]
        O3[precio_outlier_tipo]
        O4[outlier_razones]
    end

    subgraph JSON["📦 medicamentos.json"]
        J[Registro final]
    end

    S1 & S2 & S3 & S4 & S5 --> J
    P1 & P2 & P3 & P4 --> J
    PR1 & PR2 & PR3 & PR4 --> J
    O1 & O2 & O3 & O4 --> J
```

---

# 🧩 Referencia de Componentes Frontend

## store.js

- Estado global reactivo con patrón pub/sub (`suscribirse` / `notificar`)
- Filtros: texto, laboratorio, presentacion, orden, soloPami
- Sin texto ni filtros activos → `resultados = []` (muestra mensaje inicial)
- Con filtros activos y sin texto → parte del dataset completo y aplica filtros
- Ordenamiento con conciencia de vigencia: `vigencia_score < 50` siempre al fondo

## uiRenderer.js

- Render de tarjetas con principio activo en mayúsculas
- Chips de presentación: usa `pres_forma` / `pres_dosis` / `pres_unidad` / `pres_cantidad` del JSON cuando están disponibles; cae a `parsearPresentacion()` (JS) como fallback
- En modo PAMI activo, muestra el copago estimado como precio principal y el PVP como referencia secundaria
- Chip PAMI con formato "Cobertura PAMI 55% · $4.500"
- Skeleton loaders + mensajes de error/vacío
- Scroll-to-top automático al superar 300px de scroll
- Renderizado modular: `renderPresentacion(med)` y `renderPrecios(med, soloPami)` son funciones nombradas — sin IIFEs anónimas en template literals
- `hashMedicamento(med)`: genera hash único por medicamento (`droga--marca--laboratorio--presentacion`) para deep links
- `compartirMedicamento(med)`: `navigator.share` en mobile, fallback a clipboard en desktop, con evento GA4
- Tarjeta destacada con glow teal permanente y badge "Producto compartido" al abrir un link compartido
- Separador "Productos similares" entre la tarjeta destacada y los resultados por droga

## utils.js

- `normalizar()`: lowercase + quita tildes para búsqueda
- `formatearPrecio()`: formato ARS con `toLocaleString`
- `escapeHtml()`: escape de `&`, `<`, `>`, `"`, `'` para prevenir XSS
- `normalizarLaboratorio()`: resuelve laboratorios truncados por el PDF
- `parsearPresentacion()`: parser JS de fallback (60+ formas en `FORMAS_MAP`)
- `extraerFiltros()`: construye sets de presentaciones y laboratorios válidos para dropdowns

## dataLoader.js

- Caché con `sessionStorage` (clave `remedios_data_v2`, TTL 2 horas)
- Fetch con `priority: 'high'`
- Fallback silencioso si `sessionStorage` está bloqueado

## searchEngine.js

- Índice invertido de prefijos sobre `droga`, `marca` y `laboratorio`
- Búsqueda AND multi-término normalizada (sin tildes, lowercase)
- Ranking por relevancia textual (droga > marca > lab), `vigencia_score` y precio
- Registros con `vigencia_score < 50` degradados al fondo

## filters.js

- `aplicarFiltros()`: filtrado por presentación, laboratorio y PAMI
- `ordenar()`: ordenamiento con conciencia de vigencia (`vigencia_score < 50` siempre al fondo)
- `esValorCorrupto()`: detección de laboratorios con valores numéricos o de presentación en el campo lab

---

# 🎨 Guía de Estilos CSS

## Variables principales

```css
:root {
  --teal:          #008B8B;
  --teal-dark:     #005f5f;
  --teal-darker:   #003f3f;
  --teal-light:    #e6f2f2;
  --teal-accent:   #0e7490;
  --text-1:        #111111;
  --text-4:        #777777;
  --r-sm: 8px; --r-md: 12px; --r-lg: 16px;
}
```

## Responsive

Un único breakpoint mobile-first en `600px` — no hay un nivel intermedio de tablet separado, el layout de mobile se extiende hasta desktop.

| Breakpoint | Tamaño |
|---|---|
| Mobile | ≤ 600px |
| Desktop | > 600px |

---

# 🔧 Documentación de Workflows

| Workflow | Trigger | Función |
|---|---|---|
| `update_prices.yml` | Cron `30 13,21 * * 1-5` + manual | ETL principal: descarga PDF, genera JSON, corre tests, hace commit |
| `maintenance-on.yml` | Manual | Reemplaza `index.html` con página de mantenimiento |
| `maintenance-off.yml` | Manual | Restaura `index.html` desde backup |
| `codeql.yml` | Push/PR a `main` + cron semanal (sábado 01:33 UTC) | Análisis estático de seguridad (CodeQL) sobre JS, Python y los propios workflows de GitHub Actions |
| `accessibility.yml` | Push/PR a `main` que toque cualquier `*.html`, `css/style.css`, `js/**` o el propio check + cron semanal (domingo 05:00 UTC) + manual | Corre `scripts/checks/a11y-check.mjs` (axe-core + Puppeteer). Modo rápido (`index.html`, `about.html`, `terminos.html`, `privacidad.html`) en push/PR/manual; modo completo (todas las .html) solo en la corrida semanal. `admin-panel.html` queda excluido siempre. No bloquea el build — avisa, no rompe, mismo criterio que Ruff/ESLint |
| `dependabot.yml` (config, no workflow) | Semanal | Propone actualizaciones de `requirements.txt` (pip), de las actions usadas en los workflows (`github-actions`) y de `package.json` (`npm` — `axe-core`/`puppeteer`, usados solo por `a11y-check.mjs`) |

| Parámetro | Valor |
|---|---|
| Schedule | 10:30 y 18:30 AR (lunes a viernes) |
| Runtime | Ubuntu latest |
| Python | 3.11 |
| Caché de dependencias | `cache: 'pip'` en `setup-python@v6` |
| Dependencias | Ver `requirements.txt` |
| Trigger manual | Sí (`workflow_dispatch`) |
| Pull antes de push | Sí (`git pull --rebase`) |
| Tests | pytest antes de cada commit |
| Snapshot semanal | Viernes — CSV subido a GitHub Releases (`historial-YYYY-MM`) |

---

# ❓ Preguntas Frecuentes (FAQ)

## ¿De dónde salen los datos?

Del PDF oficial publicado por SIAFAR / COFA dos veces al día, de lunes a viernes.

## ¿Qué es el vigencia_score?

Un score de 0 a 100 que indica la confiabilidad del precio. Se calcula usando estadística IQR (rango intercuartílico) por droga + detección de inconsistencias de escala. Un score < 50 indica que el precio es probable outlier (obsoleto, cero, o estadísticamente anómalo respecto a la mediana de la droga).

## ¿Qué significa el chip PAMI?

Muestra la cobertura y el copago estimado en un solo chip: **"Cobertura PAMI 55% · $4.500"**.

El copago se calcula como `precio × (1 - cobertura / 100)`.

```
PVP SIAFAR:       $10.000
Cobertura PAMI:   55%
Copago estimado:  $10.000 × (1 - 0.55) = $4.500
```

Es una aproximación — el copago real puede variar porque el porcentaje de cobertura es del vademécum PAMI y el precio base es el PVP actualizado de SIAFAR.

## ¿Cada cuánto se actualiza?

Dos veces al día, de lunes a viernes (10:30 y 18:30 hora Argentina).

## ¿Tiene publicidad?

No.

## ¿Tiene tracking?

No. Usamos Google Analytics en modo anónimo para entender el uso del sitio.

## ¿Se puede usar el JSON libremente?

Sí, bajo licencia MIT. El endpoint está habilitado con `Access-Control-Allow-Origin: *`.

## ¿Cómo funciona el link para compartir un medicamento?

Cada medicamento tiene una URL única con hash: `remedi.ar/#droga--marca--laboratorio--presentacion`. Al abrirlo, la app muestra ese medicamento destacado arriba y productos similares debajo. El botón "Compartir" en cada tarjeta abre el menú nativo en mobile o copia el link en desktop.

## ¿Hay historial de precios?

Sí, desde el primer viernes de implementación. Cada viernes se genera un snapshot CSV con los precios confiables de la semana y se sube como asset a la release mensual de GitHub (`historial-YYYY-MM`). Los snapshots están disponibles públicamente en la sección [Releases](https://github.com/psbella/remediar/releases) del repositorio.

---

# ⚠️ Limitaciones conocidas

| Limitación | Descripción |
|---|---|
| ~9 registros sin presentación | El PDF de SIAFAR no incluye la presentación para estas marcas (KETOSTERIL, FRENALER D, DEXALERGIN, VIXALERG, KINALGIN P, ASFARADIL, FEMIDEN, SIGNORINA, VAXNEUVANCE). No son errores del parser — el dato simplemente no está en la fuente. |
| `pami_cobertura` es aproximado | El porcentaje proviene del vademécum PAMI (que se actualiza con menor frecuencia) aplicado sobre el PVP actual de SIAFAR. El copago real puede diferir. |
| Precios de SIAFAR en ARS | Con la inflación argentina, los precios pueden quedar desactualizados entre corridas. El `vigencia_score` ayuda a identificar los registros más sospechosos. |
| PDF de SIAFAR sin esquema fijo | Distintos laboratorios aplican su propia semántica al PDF. El pipeline de 8+ capas resuelve los patrones conocidos; pueden aparecer casos nuevos en futuras corridas. |
| SSL de SIAFAR | El servidor de SIAFAR tiene un certificado con chain incompleta. La verificación SSL usa `certifi` como CA bundle. |

---

# 🗺️ Roadmap

## Corto plazo

- ~~Corrección de verificación SSL en descarga de SIAFAR~~ ✅
- ~~Tests automatizados del ETL~~ ✅
- ~~Refactor IIFEs en uiRenderer.js~~ ✅
- ~~Compartir medicamentos con deep link~~ ✅
- ~~Snapshots semanales de precios en GitHub Releases~~ ✅
- Filtro por forma farmacéutica en la UI (usando `pres_forma`, ya disponible en el JSON)
- Historial de precios (visualización en frontend)

## Mediano plazo

- Integración con API REST de precios de medicamentos (gestión de acceso vía Ley 27.275 en curso, derivada al Ministerio de Salud el 14/07/2026)
- IOMA como segunda fuente de crosswalk
- API REST pública documentada
- Dashboard estadístico de variación de precios
- Instagram con contenido generado automáticamente

## Largo plazo

- Evolución histórica de precios
- App móvil nativa
- Integración con farmacias en tiempo real

---

# 📄 Licencia

[MIT License](https://opensource.org/license/mit). Uso libre para proyectos personales y comerciales con atribución. Texto completo en [`LICENSE`](./LICENSE).

---

# 🙏 Fuente de Datos

Datos proporcionados por [SIAFAR / COFA](https://siafar.com/precios/pdf/) (precios) y el [vademécum oficial de PAMI](https://datos.pami.org.ar/dataset/medicamentos-para-afiliados) (cobertura).

La clasificación ATC parte de la [página oficial de códigos ATC de ANMAT](https://www.anmat.gob.ar/atc/CodigosATC.asp), extraída al dataset propio [Codigos-ATC-ANMAT](https://github.com/psbella/Codigos-ATC-ANMAT) (`data/atc/atc_por_droga.json` / `atc_niveles.json`). Se completa con el índice oficial [ATC/DDD de la WHO Collaborating Centre for Drug Statistics Methodology (WHOCC)](https://atcddd.fhi.no/atc_ddd_index/), obtenido vía el scraper [fabkury/atcd](https://github.com/fabkury/atcd) (licencia [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), uso no comercial). Los nombres de droga en inglés se cruzan contra el dataset local mediante reglas de sufijo INN estándar (ver `scripts/traducir_atc_who.py`).

---

## 🌐 Enlaces del Proyecto

| Recurso | URL |
|---|---|
| Producción | https://remedi.ar |
| GitHub Pages (dominio por defecto) | https://psbella.github.io/remediar/ |
| Mirror (Cloudflare Workers) | https://remediar.pablo-s-bella.workers.dev/ |
| Repositorio | https://github.com/psbella/remediar |
| Actions / CI | https://github.com/psbella/remediar/actions |
| medicamentos.json | https://remedi.ar/data/medicamentos.json |
| Sitemap | https://remedi.ar/sitemap.xml |
| Política de privacidad | https://remedi.ar/privacidad.html |
| Términos y condiciones | https://remedi.ar/terminos.html |
| Cómo funciona | https://remedi.ar/about.html |

---

<p align="center">
  <strong>Hecho con ❤️ para que los medicamentos sean más accesibles en Argentina.</strong>
</p>


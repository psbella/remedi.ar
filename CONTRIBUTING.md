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

Antes de abrir el PR: si tocaste el ETL, corré `pytest tests/` y confirmá que pasen los 28 tests (12 de sanidad + 1 de schema + 15 unitarios de scripts/etl/); si tocaste JS/CSS/HTML, probá el cambio en el navegador, no alcanza con leer el diff. También conviene correr `ruff check .` (Python) y `eslint js/` (JS) — todavía no bloquean el CI, pero sirven para agarrar errores antes de mergear.

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

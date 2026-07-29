# Roadmap

Ítems pendientes reales, verificados contra el estado del repo al 2026-07-20.
No es una lista de deseos: cada ítem tiene una razón concreta y verificable
para estar acá. Se van tachando (no borrando) a medida que se cierran, y el
motivo del cierre queda documentado en el CHANGELOG.

## Corto plazo — heredado de la auditoría original

- [x] `<h2>Por qué remedi.ar</h2>` en `index.html`: hoy es un `<span>` dentro
      del divisor de sección (línea ~221). Salta de `<h1>` a `<h3>` sin
      nivel intermedio en la sección institucional.
- [x] Resolver el origen del doble encoding en `blacklist.json`
      (`scripts/etl/blacklist.py`, función `cargar_blacklist`): hoy se
      corrige en tiempo de carga con un try/except silencioso. Funciona,
      pero indica que algo en el proceso de generación de ese archivo
      escribe las claves mal codificadas. Vale la pena encontrar el punto
      real y sacar el parche.

## Corto plazo — surgido en la revisión de julio 2026

- [x] Verificar en producción que el CSP/headers reales de `remedi.ar`
      (servidos vía Cloudflare) coincidan con lo declarado en `_headers`.
      No verificable desde un entorno de auditoría sin acceso al dominio;
      es un `curl -sI https://remedi.ar` de dos minutos.

## Mediano plazo

- [x] Algún chequeo automático de accesibilidad en CI (por ejemplo
      `axe-core` corriendo sobre `index.html`). El bug del checkbox PAMI
      (`display: none` sacándolo del tab order) se encontró por lectura
      manual de CSS — nada impide que se reintroduzca sin que nadie lo note.
- [x] Los 24 findings de estilo restantes de Ruff (`E701`/`E702`, ver
      `pyproject.toml`) — bajo impacto, sin bloquear CI a propósito.

## Largo plazo — evaluar si vale la pena antes de encarar

- [ ] SEO long-tail: hoy no hay URLs individuales por droga+marca (todo
      el listado es client-side vía `fetch` a `medicamentos.json`), así
      que no se puede rankear para búsquedas específicas de un
      medicamento puntual. Evaluar páginas estáticas livianas para las
      combinaciones de mayor volumen, sin introducir un framework nuevo.

## No es un ítem de roadmap — nota estructural

Bus factor 1: un solo mantenedor revisa, mergea y decide qué se revierte.
Ningún ítem de esta lista lo resuelve; es una característica del proyecto
en su tamaño actual, no un bug a corregir.

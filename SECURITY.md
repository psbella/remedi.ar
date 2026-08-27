# Política de seguridad

## Alcance

remedi.ar es un sitio estático (sin backend propio, sin base de datos, sin cuentas de
usuario) que procesa datos públicos de precios de medicamentos. No maneja datos
personales de los visitantes del sitio más allá de analítica anónima (Google Analytics).

El único componente con superficie de ataque no trivial es el panel de administración
(`admin-panel.html`), de uso exclusivo del mantenedor del proyecto. `admin-panel.html`
vive commiteado en `main` de forma permanente. El modelo anterior (subirlo manualmente al
hosting solo cuando se necesitaba usarlo y retirarlo después — ver commit `5af65b2`,
"security: saca admin.html del repo público") quedó descartado: la mitigación real no
es ocultar el archivo del repo público, sino dos cosas — no está indexado (`noindex,
nofollow`) y las acciones que expone requieren un GitHub Personal Access Token que el
mantenedor ingresa manualmente y que se guarda solo en memoria del navegador (nunca en
el repo ni en el archivo servido). Quien acceda a `admin-panel.html` sin ese token ve el
panel pero no puede ejecutar ninguna acción contra la API de GitHub. La descripción de
riesgo de este documento sigue aplicando igual mientras ese archivo exista.

## Versiones soportadas

Al ser un sitio con una sola rama de producción (`main`, desplegada de forma continua),
solo se da soporte de seguridad a la última versión publicada en el
[CHANGELOG](./CHANGELOG.md). No se mantienen versiones anteriores.

## Cómo reportar una vulnerabilidad

Si encontrás una vulnerabilidad de seguridad en este repositorio, **no la reportes en un
issue público**. En su lugar, escribime directamente a:

**pablo.s.bella@gmail.com** (asunto sugerido: `remedi.ar - Reporte de seguridad`)

Incluí, en la medida de lo posible:

- Descripción del problema y su impacto potencial.
- Pasos para reproducirlo.
- Versión o commit del repositorio donde lo verificaste.

### Qué podés esperar

- Confirmación de recepción en un plazo razonable (días, no semanas — este es un
  proyecto de un solo mantenedor, sin SLA formal).
- Una vez confirmado y corregido el problema, se documentará en el
  [CHANGELOG](./CHANGELOG.md) bajo la sección "🔒 Seguridad", dando crédito a quien lo
  reportó si así lo desea.
- Se pide un período razonable de divulgación responsable (coordinated disclosure)
  antes de hacer pública cualquier prueba de concepto, para dar tiempo a aplicar el fix.

## Qué no es un problema de seguridad

- El dataset de `data/medicamentos.json` es intencionalmente público y descargable
  (CORS abierto) — no reportar esto como una "exposición de datos".
- `admin-panel.html` no aparece en buscadores (`noindex, nofollow`), pero esto no es
  una medida de seguridad real: el código del panel es público en este mismo
  repositorio. La única barrera de acceso es el token, que se pide en cada sesión y
  nunca se persiste.

## Alcance fuera de este repositorio

Si el reporte involucra la infraestructura de hosting (GitHub Pages, Cloudflare como
proxy/DNS, o el mirror en Cloudflare Workers) o servicios de terceros integrados
(Google Analytics/Tag Manager), por favor reportalo directamente al proveedor
correspondiente además de avisarme a mí si el proyecto se ve afectado.

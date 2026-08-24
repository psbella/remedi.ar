// scripts/checks/a11y-check.mjs
//
// Chequeo de accesibilidad automatizado con axe-core, corrido contra las
// páginas estáticas del sitio servidas localmente. No bloquea el CI --
// mismo criterio que Ruff/ESLint en este repo (ver .github/workflows/*):
// avisa, no rompe el build. La idea es que una regresión como la del
// checkbox PAMI (display:none sacándolo del tab order, encontrada por
// lectura manual de CSS) se vea acá antes que en producción.
//
// Dos modos, elegidos por el workflow vía la env var A11Y_FULL:
//   - Rápido (default): solo las páginas núcleo (PAGINAS_RAPIDAS) --
//     corre en cada push/PR/manual sin sumar minutos de CI.
//   - Completo (A11Y_FULL=1): TODAS las .html de la raíz, descubiertas
//     dinámicamente -- pensado para la corrida semanal programada.
// admin-panel.html queda excluido siempre: panel interno, no público, no
// forma parte de la superficie que le importa a este chequeo.
//
// Uso: node scripts/checks/a11y-check.mjs
//      A11Y_FULL=1 node scripts/checks/a11y-check.mjs

import http from 'node:http';
import { readFile, readdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import puppeteer from 'puppeteer';

const require = createRequire(import.meta.url);
const axeSource = require.resolve('axe-core/axe.min.js');

const ROOT = path.resolve(import.meta.dirname, '..', '..');
const PORT = 4173;
const EXCLUIDAS = new Set(['admin-panel.html']);
const PAGINAS_RAPIDAS = ['index.html', 'about.html', 'terminos.html', 'privacidad.html'];

async function listarPaginas() {
    const entries = await readdir(ROOT, { withFileTypes: true });
    return entries
        .filter(e => e.isFile() && e.name.endsWith('.html') && !EXCLUIDAS.has(e.name))
        .map(e => e.name)
        .sort();
}

async function resolverPaginas() {
    const todas = await listarPaginas();
    if (process.env.A11Y_FULL === '1') return todas;
    const disponibles = new Set(todas);
    return PAGINAS_RAPIDAS.filter(p => disponibles.has(p));
}

const MIME = {
    '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
    '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png',
};

function servirEstaticos() {
    return http.createServer(async (req, res) => {
        const rawPath = (req.url || '/').split('?')[0];
        let decodedPath;
        try {
            decodedPath = decodeURIComponent(rawPath);
        } catch {
            res.writeHead(400);
            res.end('bad request');
            return;
        }

        const filePath = path.resolve(ROOT, `.${decodedPath}`);
        const relativePath = path.relative(ROOT, filePath);
        if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
            res.writeHead(403);
            res.end('forbidden');
            return;
        }

        try {
            const data = await readFile(filePath);
            const ext = path.extname(filePath);
            res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
            res.end(data);
        } catch {
            res.writeHead(404);
            res.end('not found');
        }
    }).listen(PORT);
}

async function chequearPagina(page, pagina) {
    await page.goto(`http://localhost:${PORT}/${pagina}`, { waitUntil: 'networkidle0' });
    await page.addScriptTag({ path: axeSource });
    return page.evaluate(async () => {
        return await axe.run(document, {
            runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'best-practice'] },
        });
    });
}

async function main() {
    const server = servirEstaticos();
    const puppeteerArgs = process.env.CI ? ['--no-sandbox', '--disable-setuid-sandbox'] : [];
    const browser = await puppeteer.launch({ headless: true, args: puppeteerArgs });
    // Una sola page reutilizada para todo el recorrido -- evita el costo de
    // abrir/cerrar contexto por cada una de las ~100+ páginas del sitio.
    const page = await browser.newPage();

    const paginas = await resolverPaginas();
    const modo = process.env.A11Y_FULL === '1' ? 'completo' : 'rápido';
    console.log(`Chequeando ${paginas.length} página(s) (modo ${modo})...`);

    let totalViolaciones = 0;
    const conViolaciones = [];

    for (const pagina of paginas) {
        let violations;
        try {
            ({ violations } = await chequearPagina(page, pagina));
        } catch (err) {
            console.log(`\n=== ${pagina} ===`);
            console.log(`  ERROR al chequear: ${err.message}`);
            continue;
        }
        if (violations.length === 0) continue;
        totalViolaciones += violations.length;
        conViolaciones.push(pagina);
        console.log(`\n=== ${pagina} ===`);
        for (const v of violations) {
            console.log(`  [${v.impact}] ${v.id}: ${v.help} (${v.nodes.length} elemento(s))`);
            console.log(`    -> ${v.helpUrl}`);
        }
    }

    await browser.close();
    server.close();

    if (totalViolaciones > 0) {
        console.log(`\nAVISO: ${totalViolaciones} tipo(s) de violación en ${conViolaciones.length}/${paginas.length} página(s). No bloquea el build (mismo criterio que ruff/eslint en este repo) -- revisar a mano.`);
    } else {
        console.log(`\nOK: sin violaciones de accesibilidad en las ${paginas.length} páginas chequeadas.`);
    }
    // Salida siempre 0 a propósito: chequeo informativo, no gate.
    process.exit(0);
}

main().catch(err => {
    console.error('Error corriendo el chequeo de accesibilidad:', err);
    // Tampoco bloquea si el chequeo en sí falla (ej. Chromium no disponible) --
    // es una señal para revisar el workflow, no para tumbar el build de precios.
    process.exit(0);
});

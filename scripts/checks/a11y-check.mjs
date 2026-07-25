// scripts/checks/a11y-check.mjs
//
// Chequeo de accesibilidad automatizado con axe-core, corrido contra las
// páginas estáticas del sitio servidas localmente. No bloquea el CI --
// mismo criterio que Ruff/ESLint en este repo (ver .github/workflows/*):
// avisa, no rompe el build. La idea es que una regresión como la del
// checkbox PAMI (display:none sacándolo del tab order, encontrada por
// lectura manual de CSS) se vea acá antes que en producción.
//
// Uso: node scripts/checks/a11y-check.mjs

import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import puppeteer from 'puppeteer';

const require = createRequire(import.meta.url);
const axeSource = require.resolve('axe-core/axe.min.js');

const ROOT = path.resolve(import.meta.dirname, '..', '..');
const PORT = 4173;
const PAGINAS = ['index.html', 'about.html'];

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

async function chequearPagina(browser, pagina) {
    const page = await browser.newPage();
    await page.goto(`http://localhost:${PORT}/${pagina}`, { waitUntil: 'networkidle0' });
    await page.addScriptTag({ path: axeSource });
    const resultado = await page.evaluate(async () => {
        return await axe.run(document, {
            runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'best-practice'] },
        });
    });
    await page.close();
    return resultado;
}

async function main() {
    const server = servirEstaticos();
    const puppeteerArgs = process.env.CI ? ['--no-sandbox', '--disable-setuid-sandbox'] : [];
    const browser = await puppeteer.launch({ headless: true, args: puppeteerArgs });

    let totalViolaciones = 0;

    for (const pagina of PAGINAS) {
        const { violations } = await chequearPagina(browser, pagina);
        console.log(`\n=== ${pagina} ===`);
        if (violations.length === 0) {
            console.log('  Sin violaciones.');
            continue;
        }
        totalViolaciones += violations.length;
        for (const v of violations) {
            console.log(`  [${v.impact}] ${v.id}: ${v.help} (${v.nodes.length} elemento(s))`);
            console.log(`    -> ${v.helpUrl}`);
        }
    }

    await browser.close();
    server.close();

    if (totalViolaciones > 0) {
        console.log(`\nAVISO: ${totalViolaciones} tipo(s) de violación encontrados. No bloquea el build (mismo criterio que ruff/eslint en este repo) -- revisar a mano.`);
    } else {
        console.log('\nOK: sin violaciones de accesibilidad en ninguna página chequeada.');
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

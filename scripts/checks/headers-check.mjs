// scripts/checks/headers-check.mjs
//
// Compara los headers HTTP servidos en producción (remedi.ar y
// www.remedi.ar) contra el bloque /* de _headers, que documenta la
// Transform Rule de Cloudflare pero no la aplica -- ver el comentario al
// inicio de _headers. Sin este chequeo, un cambio manual en el dashboard
// de Cloudflare que no se replique acá (o al revés) no lo detecta nadie
// hasta que alguien lo pega a mano.
//
// A diferencia de a11y-check.mjs y de ruff/eslint en este repo (que
// avisan sin romper el build), acá SÍ se falla con exit code != 0 si hay
// una divergencia: es un chequeo de seguridad, no de estilo, y esta
// Action no bloquea ningún deploy -- corre sola, así que fallar no tiene
// costo de bloquear nada.
//
// Uso: node scripts/checks/headers-check.mjs

import { readFile } from 'node:fs/promises';
import path from 'node:path';
import https from 'node:https';

const ROOT = path.resolve(import.meta.dirname, '..', '..');
const HOSTS = ['remedi.ar', 'www.remedi.ar'];

// Headers de _headers que son responsabilidad de la Transform Rule de
// Cloudflare (ver comentario en _headers). Cache-Control por tipo de
// asset queda afuera a propósito: no depende 100% de esa config manual
// como sí dependen estos 6.
const HEADERS_A_VERIFICAR = [
    'content-security-policy',
    'permissions-policy',
    'referrer-policy',
    'strict-transport-security',
    'x-content-type-options',
    'x-frame-options',
];

async function leerHeadersEsperados() {
    const raw = await readFile(path.join(ROOT, '_headers'), 'utf-8');
    const lineas = raw.split('\n');
    const inicio = lineas.findIndex(l => l.trim() === '/*');
    if (inicio === -1) throw new Error('_headers no tiene un bloque /*');

    const esperados = {};
    for (let i = inicio + 1; i < lineas.length; i++) {
        const l = lineas[i];
        if (l.trim() === '') break; // fin del bloque /*
        const idx = l.indexOf(':');
        if (idx === -1) continue;
        const nombre = l.slice(0, idx).trim().toLowerCase();
        const valor = l.slice(idx + 1).trim();
        if (HEADERS_A_VERIFICAR.includes(nombre)) esperados[nombre] = valor;
    }
    return esperados;
}

function pedirHeaders(host) {
    return new Promise((resolve, reject) => {
        const req = https.request(
            { hostname: host, path: '/', method: 'HEAD', timeout: 10_000 },
            res => resolve(res.headers)
        );
        req.on('timeout', () => req.destroy(new Error(`timeout consultando ${host}`)));
        req.on('error', reject);
        req.end();
    });
}

async function main() {
    const esperados = await leerHeadersEsperados();
    const faltantes = HEADERS_A_VERIFICAR.filter(h => !esperados[h]);
    if (faltantes.length > 0) {
        console.error(`_headers no define: ${faltantes.join(', ')} -- revisar el bloque /*`);
        process.exit(1);
    }

    let huboDivergencia = false;

    for (const host of HOSTS) {
        console.log(`\n== ${host} ==`);
        let reales;
        try {
            reales = await pedirHeaders(host);
        } catch (err) {
            console.error(`  No se pudo consultar ${host}: ${err.message}`);
            huboDivergencia = true;
            continue;
        }

        for (const nombre of HEADERS_A_VERIFICAR) {
            const esperado = esperados[nombre];
            const real = reales[nombre];
            if (real === esperado) {
                console.log(`  OK  ${nombre}`);
            } else {
                huboDivergencia = true;
                console.log(`  DIVERGE  ${nombre}`);
                console.log(`    _headers:   ${esperado}`);
                console.log(`    servido:    ${real ?? '(ausente)'}`);
            }
        }
    }

    if (huboDivergencia) {
        console.error('\nHay headers de producción que no coinciden con _headers. Revisar la Transform Rule en el dashboard de Cloudflare o actualizar _headers si el cambio fue intencional.');
        process.exit(1);
    }
    console.log('\nTodos los headers de producción coinciden con _headers.');
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});

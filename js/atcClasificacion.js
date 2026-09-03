// js/atcClasificacion.js — Carga en segundo plano de los lookups ATC
// (fuente: dataset propio ANMAT https://github.com/psbella/Codigos-ATC-ANMAT).
// Mismo patrón de cache/errores que infoAdicional.js: dato secundario,
// no crítico, con fallback silencioso si falla la carga.
const CACHE_TTL_MS = 2 * 60 * 60 * 1000; // 2 horas, igual criterio que dataLoader.js

const _promesasCarga = {};

function _cargarJsonConCache(url, cacheKey) {
    if (_promesasCarga[cacheKey]) return _promesasCarga[cacheKey];
    _promesasCarga[cacheKey] = (async () => {
        try {
            const cached = sessionStorage.getItem(cacheKey);
            if (cached) {
                const { ts, data } = JSON.parse(cached);
                if (Date.now() - ts < CACHE_TTL_MS) return data;
            }
        } catch (_) { }
        try {
            const res = await fetch(url, { cache: 'default' });
            if (!res.ok) throw new Error(`Error al cargar ${url}: ${res.status}`);
            const data = await res.json();
            try {
                sessionStorage.setItem(cacheKey, JSON.stringify({ ts: Date.now(), data }));
            } catch (_) { }
            return data;
        } catch (err) {
            console.warn(`[atcClasificacion] No se pudo cargar ${url}:`, err);
            return {};
        }
    })();
    return _promesasCarga[cacheKey];
}

export function cargarClasificacionATC() {
    return _cargarJsonConCache('data/atc/atc_niveles.json', 'atc_niveles_v1');
}

export function cargarAtcPorDroga() {
    return _cargarJsonConCache('data/atc/atc_por_droga.json', 'atc_por_droga_v1');
}

function normalizarDroga(s) {
    return (s || '')
        .trim()
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');
}

const STOPWORDS_DROGA = new Set([
    'asoc',
    'clorhidrato', 'clorh', 'diclorh', 'sulfato', 'acetato', 'citrato',
    'bromuro', 'cloruro', 'fosfato', 'sodio', 'potasio', 'calcio',
    'maleato', 'fumarato', 'tartrato', 'besilato', 'mesilato', 'succinato',
    'bicarbonato', 'carbonato', 'nitrato', 'yoduro', 'gluconato', 'lactato',
    'picosulfato', 'valproato', 'fluoruro', 'ranelato'
]);

function variantesAcido(norm) {
    const variantes = [norm];
    if (norm.startsWith('ac.')) {
        const resto = norm.slice(3).trim();
        variantes.push('acido ' + resto, resto);
    } else if (!norm.startsWith('acido ')) {
        variantes.push('acido ' + norm);
    }
    return variantes;
}

export function obtenerJerarquiaATC(atcRaw, mapaNiveles) {
    if (!atcRaw || !mapaNiveles || !mapaNiveles.n1) return null;
    const codigos = atcRaw.split('\n').map(c => c.trim()).filter(Boolean);
    const breadcrumbs = [];
    for (const cod of codigos) {
        const partes = [];
        if (cod.length >= 1) {
            const desc = mapaNiveles.n1[cod.slice(0, 1)];
            if (desc) partes.push(desc);
        }
        if (cod.length >= 4) {
            const desc = mapaNiveles.n23[cod.slice(0, 4)];
            if (desc) partes.push(desc);
        }
        if (cod.length >= 5) {
            const desc = mapaNiveles.n4[cod.slice(0, 5)];
            if (desc) partes.push(desc);
        }
        if (partes.length > 0) {
            const breadcrumb = partes.join(' › ');
            if (!breadcrumbs.includes(breadcrumb)) breadcrumbs.push(breadcrumb);
        }
    }
    return breadcrumbs.length > 0 ? breadcrumbs.join('\n') : null;
}

const EXCEPCIONES_COMBO = [
    {
        requiere: ['amoxicilina', 'clavulanico'],
        codigos: ['J01CR02'],
    },
];

function _clasificacionPorExcepcion(drogaNormCompleta) {
    for (const exc of EXCEPCIONES_COMBO) {
        if (exc.requiere.every(tok => drogaNormCompleta.includes(tok))) {
            return exc.codigos;
        }
    }
    return null;
}

export function obtenerClasificacionPorDroga(drogaMed, mapaPorDroga, mapaNiveles) {
    if (!drogaMed || !mapaPorDroga || !mapaNiveles || !mapaNiveles.n1) return null;

    const normCompleta = normalizarDroga(drogaMed);
    const codigosExcepcion = _clasificacionPorExcepcion(normCompleta);
    if (codigosExcepcion) {
        const jerarquia = obtenerJerarquiaATC(codigosExcepcion.join('\n'), mapaNiveles);
        return jerarquia ? { codigos: codigosExcepcion.join('\n'), jerarquia } : null;
    }

    const partes = drogaMed.split(',')
        .map(normalizarDroga)
        .filter(Boolean)
        .filter(p => !STOPWORDS_DROGA.has(p.replace(/\.$/, '')));
    if (partes.length === 0) return null;

    const codigos = [];
    for (const norm of partes) {
        let cods = null;
        for (const variante of variantesAcido(norm)) {
            if (mapaPorDroga[variante]) { cods = mapaPorDroga[variante]; break; }
        }
        if (!cods) return null;
        for (const cod of cods) {
            if (!codigos.includes(cod)) codigos.push(cod);
        }
    }

    const jerarquia = obtenerJerarquiaATC(codigos.join('\n'), mapaNiveles);
    if (!jerarquia) return null;

    return { codigos: codigos.join('\n'), jerarquia };
}

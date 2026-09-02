// js/atcClasificacion.js — Carga en segundo plano de los lookups ATC
// (fuente: dataset propio ANMAT https://github.com/psbella/Codigos-ATC-ANMAT).
// Mismo patrón de cache/errores que infoAdicional.js: dato secundario,
// no crítico, con fallback silencioso si falla la carga.
const CACHE_TTL_MS = 2 * 60 * 60 * 1000; // 2 horas, igual criterio que dataLoader.js

const _promesasCarga = {};

/**
 * Carga (una sola vez por url, con cache en sessionStorage) un JSON
 * estático. Es un dato secundario y no crítico: si falla la carga, no
 * debe interrumpir la app — se resuelve con un objeto vacío y se loguea
 * el error, dejando la lista principal de medicamentos intacta.
 */
function _cargarJsonConCache(url, cacheKey) {
    if (_promesasCarga[cacheKey]) return _promesasCarga[cacheKey];

    _promesasCarga[cacheKey] = (async () => {
        try {
            const cached = sessionStorage.getItem(cacheKey);
            if (cached) {
                const { ts, data } = JSON.parse(cached);
                if (Date.now() - ts < CACHE_TTL_MS) return data;
            }
        } catch (_) { /* sessionStorage bloqueado: continuar */ }

        try {
            const res = await fetch(url, { cache: 'default' });
            if (!res.ok) throw new Error(`Error al cargar ${url}: ${res.status}`);
            const data = await res.json();
            try {
                sessionStorage.setItem(cacheKey, JSON.stringify({ ts: Date.now(), data }));
            } catch (_) { /* sessionStorage lleno: no es crítico */ }
            return data;
        } catch (err) {
            console.warn(`[atcClasificacion] No se pudo cargar ${url}:`, err);
            return {};
        }
    })();

    return _promesasCarga[cacheKey];
}

/**
 * Lookup jerárquico ATC: { n1: {cod: desc}, n23: {cod: desc}, n4: {cod: desc} }.
 */
export function cargarClasificacionATC() {
    return _cargarJsonConCache('data/atc/atc_niveles.json', 'atc_niveles_v1');
}

/**
 * Lookup droga (normalizada) -> lista de códigos N5_COD que le
 * corresponden según el dataset ANMAT. Algunas drogas tienen más de un
 * código (mismo principio activo, distinta vía/uso) — de ahí la lista.
 */
export function cargarAtcPorDroga() {
    return _cargarJsonConCache('data/atc/atc_por_droga.json', 'atc_por_droga_v1');
}

/**
 * Normaliza un nombre de droga para matchear contra el dataset ANMAT:
 * minúsculas, sin acentos, sin espacios sobrantes. Debe coincidir con
 * la normalización usada al generar data/atc/atc_por_droga.json.
 */
function normalizarDroga(s) {
    return (s || '')
        .trim()
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');
}

/**
 * Tokens que aparecen en el campo `droga` como parte de un combo pero no
 * son un principio activo en sí — son palabras del dataset ANMAT que
 * indican "combinado con otras drogas" o el sufijo de sal de una droga
 * escrita en formato invertido "droga,sal" (ej: "morfina,sulfato" es UNA
 * sola droga — sulfato de morfina — no un combo de dos). Si se tratan
 * como una droga más del combo, nunca van a matchear en
 * atc_por_droga.json y el combo entero queda sin clasificar aunque la
 * droga principal sí esté clasificada.
 * Ej: "fenilefrina, asoc." → sin filtrar "asoc.", el combo da null.
 * Ej: "bencidamina,clorhidrato" → sin filtrar "clorhidrato", da null.
 * Se comparan sin el punto final.
 *
 * Verificado (2026-09-02) que ninguno de estos sufijos de sal tiene
 * entrada propia en atc_por_droga.json, y que filtrarlos no cambia el
 * código de ningún medicamento que ya clasificaba correctamente antes
 * del cambio (0 regresiones sobre las 13127 entradas de medicamentos.json).
 * Riesgo conocido y aceptado: en un caso hipotético donde la sal
 * específica cambie el código ATC real (no observado en los 33 casos
 * recuperados), este filtro daría el código de la droga base en vez del
 * código específico de esa sal.
 */
const STOPWORDS_DROGA = new Set([
    'asoc',
    'clorhidrato', 'clorh', 'diclorh', 'sulfato', 'acetato', 'citrato',
    'bromuro', 'cloruro', 'fosfato', 'sodio', 'potasio', 'calcio',
    'maleato', 'fumarato', 'tartrato', 'besilato', 'mesilato', 'succinato',
    'bicarbonato', 'carbonato', 'nitrato', 'yoduro', 'gluconato', 'lactato',
    'picosulfato', 'valproato', 'fluoruro', 'ranelato'
]);

/**
 * Variantes de "ácido" a probar cuando el nombre normalizado no matchea
 * tal cual: remedi.ar a veces lo abrevia ("ac.clavulanico") y a veces lo
 * omite directamente ("acetilsalicilico" en vez de "acido acetilsalicilico").
 * Devuelve el nombre original primero (caso más común) y después las
 * variantes, en ese orden — se usa la primera que matchee.
 *
 * Se probaron además abreviaturas de sales (clorh., fosf., sulf., etc.,
 * incluso respetando el formato invertido real del CSV "droga, sal de")
 * y no recuperaron ningún match adicional — no vale la pena la
 * complejidad extra, así que no se incluyen.
 */
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

/**
 * Arma el "breadcrumb" jerárquico oficial ANMAT (Nivel 1 › Nivel 2-3 ›
 * Nivel 4) a partir de uno o más códigos ATC crudos (separados por '\n').
 * Cada código puede llegar truncado a distintos niveles (1, 4, 5 o 7
 * caracteres) — se arma con los niveles que el código alcance y que
 * existan en el lookup, ignorando el resto.
 *
 * Devuelve null si no hay lookup cargado, no hay código, o ningún
 * código matcheó ningún nivel (para que el llamador pueda hacer fallback
 * a otro campo).
 */
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

/**
 * Excepciones manuales verificadas: combos donde el nombre que usa ANMAT
 * para el código ATC no tiene relación textual con los nombres de sus
 * componentes, así que ningún matching por texto (por más variantes que
 * se prueben) puede llegar solo. Cada excepción se aplica si el nombre
 * completo de la droga (normalizado, sin partir por comas) contiene TODOS
 * los tokens de `requiere` — así es tolerante a cómo esté puntuado o
 * fragmentado el campo `droga` de origen (ver casos reales abajo).
 *
 * Lista deliberadamente corta y explícita — no es un sistema de consenso
 * automático, cada entrada se agrega a mano y se verifica contra el CSV
 * ANMAT antes de sumarla.
 */
const EXCEPCIONES_COMBO = [
    {
        // "amoxicilina, clavulánico,ác." (64 productos, ej. Amoxidal Duo,
        // Amoclav, Clavulox Duo) y "amoxicilina, ác.clavulánico, a" (2
        // productos, mismo principio activo con el campo droga
        // fragmentado distinto) — ninguna variante de "clavulanico"
        // aparece como principio activo propio en el CSV ANMAT: ahí
        // figura como N5_COD=J01CR02, PRINCIPIO ACTIVO="AMOXICILINA E
        // INHIBIDORES DE LA ENZIMA". Sin esta excepción, el match parcial
        // de "amoxicilina" sola daría J01CR02→J01CA04 (incorrecto:
        // penicilina simple en vez de combinación con inhibidor de
        // betalactamasa). Verificado contra codigos_atc.csv el 2026-09-02.
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

/**
 * Clasificación ATC a partir de la droga propia del medicamento (campo
 * `droga` de medicamentos.json — combos separados por ', '), matcheada
 * contra el dataset ANMAT. Es la fuente primaria: propia y verificable,
 * sin depender del scrape de terceros.
 *
 * Primero revisa EXCEPCIONES_COMBO (ver arriba). Si no aplica ninguna,
 * intenta el match automático por componente: para combos (más de una
 * droga), exige que TODAS las partes matcheen antes de devolver algo. Si
 * solo matchea una parte (ej. "amoxicilina" dentro de "amoxicilina,
 * clavulánico,ác." sin la excepción), mostrar solo esa clasificación
 * sería incorrecto: un combo con inhibidor de betalactamasa tiene un
 * código ATC propio (J01CR02), distinto al de la droga base sola
 * (J01CA04) — mostrar el de la droga base sería mostrar el dato
 * equivocado, no uno incompleto.
 *
 * Un mismo principio activo puede tener más de un código ATC (distinta
 * vía o uso clínico) — para esos sí se muestran todos, deduplicados.
 *
 * Devuelve null si no hay lookups cargados, si alguna droga del combo no
 * matcheó (y ninguna excepción aplica), o si ninguna matcheó.
 */
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
        if (!cods) return null; // esta parte del combo no matcheó: no mostrar nada
        for (const cod of cods) {
            if (!codigos.includes(cod)) codigos.push(cod);
        }
    }

    const jerarquia = obtenerJerarquiaATC(codigos.join('\n'), mapaNiveles);
    if (!jerarquia) return null;

    return { codigos: codigos.join('\n'), jerarquia };
}

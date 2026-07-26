// js/filters.js — Filtros y ordenamiento con soporte de vigencia

/**
 * Detecta si un valor de laboratorio quedó corrupto por un mal parseo del PDF
 * (por ejemplo, un precio o una dosis que terminó en el campo equivocado).
 */
function esValorCorrupto(valor) {
    if (!valor) return true;
    const limpio = valor.toString().trim();
    if (/^[\d\.,\$]+$/.test(limpio)) return true;
    if (/mg|ml|compr?|comp\.|rec\.|x\s?\d+|susp\.|sol\.|gts\.|crema|ung\.|iny\./i.test(limpio)) return true;
    if (/^\d+\s*(mg|ml|g|ui)/i.test(limpio)) return true;
    return false;
}

/**
 * Aplica los filtros de presentación, laboratorio y cobertura PAMI sobre la
 * lista de medicamentos. Los laboratorios con valor corrupto (ver
 * esValorCorrupto) nunca matchean, aunque coincida el texto.
 */
export function aplicarFiltros(lista, presentacion = '', laboratorio = '', mostrarSospechosos = true, soloPami = false) {
    let r = [...lista];
    if (presentacion) r = r.filter(m => m.presentacion === presentacion);
    if (laboratorio) {
        r = r.filter(m => {
            const lab = m.laboratorio || '';
            return !esValorCorrupto(lab) && lab === laboratorio;
        });
    }
    if (soloPami) r = r.filter(m => m.pami_cobertura != null);
    // Opción: ocultar sospechosos al final (ya los ordena buscar(), pero el filtro es explícito)
    if (!mostrarSospechosos) {
        r = r.filter(m => (m.vigencia_score ?? 100) >= 50);
    }
    return r;
}

/**
 * Ordenamiento con conciencia de vigencia.
 * Nunca sube un producto sospechoso arriba de uno normal.
 */
export function ordenar(lista, modo = 'relevancia') {
    return [...lista].sort((a, b) => {
        const vigA = a.vigencia_score ?? 100;
        const vigB = b.vigencia_score ?? 100;
        const suspA = vigA < 50;
        const suspB = vigB < 50;

        // Sospechosos siempre al fondo
        if (suspA !== suspB) return suspA ? 1 : -1;

        if (modo === 'precio_asc') {
            return (a.precio || 0) - (b.precio || 0);
        }
        if (modo === 'precio_desc') {
            return (b.precio || 0) - (a.precio || 0);
        }
        // 'relevancia': mantener orden que viene del searchEngine
        return 0;
    });
}

/**
 * Devuelve la lista de laboratorios únicos y ordenados alfabéticamente,
 * excluyendo los que parecen corruptos (ver esValorCorrupto). Se usa para
 * poblar el dropdown de filtro por laboratorio.
 */
export function obtenerLaboratoriosValidos(lista) {
    const labs = new Set();
    lista.forEach(m => {
        const lab = m.laboratorio;
        if (lab && !esValorCorrupto(lab)) labs.add(lab);
    });
    return [...labs].sort();
}

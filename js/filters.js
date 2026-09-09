// js/filters.js — Filtros y ordenamiento con soporte de vigencia
import { esLaboratorioCorrupto, normalizarLaboratorio } from './utils.js';

/**
 * Aplica los filtros de presentación, laboratorio y cobertura PAMI sobre la
 * lista de medicamentos. Los laboratorios con valor corrupto (ver
 * esLaboratorioCorrupto en utils.js) nunca matchean, aunque coincida el
 * texto. `laboratorio` llega como el nombre NORMALIZADO (el que arma
 * extraerFiltros() para el dropdown), así que el valor crudo de cada
 * medicamento se normaliza antes de comparar.
 */
export function aplicarFiltros(lista, presentacion = '', laboratorio = '', mostrarSospechosos = true, soloPami = false) {
    let r = [...lista];
    if (presentacion) r = r.filter(m => m.presentacion === presentacion);
    if (laboratorio) {
        r = r.filter(m => {
            const lab = m.laboratorio || '';
            return !esLaboratorioCorrupto(lab) && normalizarLaboratorio(lab) === laboratorio;
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

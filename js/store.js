// js/store.js — Estado Centralizado.
// Usa searchEngine para búsqueda real (índice invertido + ranking).
// Sin texto → resultados vacíos (mensaje inicial), no lista completa.

import { buscar } from './searchEngine.js';
import { aplicarFiltros, ordenar } from './filters.js';

// ── Estado inicial ────────────────────────────────────────────────────
let state = {
    todos:      [],
    resultados: [],
    resultadosSinFiltros: [],

    filtros: {
        texto:        '',
        presentacion: '',
        laboratorio:  '',
        orden:        'relevancia',
        soloPami:     false,
    },

    estaCargando: true,
    error:        null,

    filtrosDisponibles: {
        presentaciones: [],
        laboratorios:   [],
    },
};

// ── Suscriptores ──────────────────────────────────────────────────────
const suscriptores = [];

/**
 * Registra una función que se ejecuta con el estado completo cada vez que
 * el store cambia (ver notificar).
 */
export function suscribirse(fn) {
    suscriptores.push(fn);
}

function notificar() {
    suscriptores.forEach(fn => fn(state));
}

// ── Getters ───────────────────────────────────────────────────────────
// Todos devuelven una copia superficial (spread), nunca la referencia
// interna, para que nadie mute el estado del store desde afuera.
export function getState()     { return { ...state }; }
export function getFiltros()   { return { ...state.filtros }; }
export function getResultados(){ return [...state.resultados]; }
export function getResultadosSinFiltros(){ return [...state.resultadosSinFiltros]; }
export function getTodos()     { return [...state.todos]; }

// ── Recalcular resultados ─────────────────────────────────────────────
/**
 * Recalcula state.resultados a partir de los filtros actuales: sin texto
 * ni filtro activo deja resultados vacío (para el mensaje inicial en UI);
 * si no, busca (o parte del dataset completo), guarda una copia pre-filtro
 * en resultadosSinFiltros (para poblar los dropdowns), aplica filtros y,
 * si el orden no es "relevancia", reordena explícitamente.
 */
function recalcularResultados() {
    const { texto, presentacion, laboratorio, orden, soloPami } = state.filtros;
    const hayTexto  = texto && texto.trim().length >= 2;
    const hayFiltro = !!(presentacion || laboratorio || soloPami);

    // Sin texto ni filtro: no mostrar nada (mensaje inicial en UI)
    if (!hayTexto && !hayFiltro) {
        state.resultados = [];
        return;
    }

    // 1. Búsqueda: si hay texto usar el índice; si no, partir del dataset completo
    let resultados = hayTexto ? buscar(texto) : [...state.todos];

    // Guardar resultados antes de filtros (para poblar dropdowns)
    state.resultadosSinFiltros = resultados;

    // 2. Filtros adicionales
    resultados = aplicarFiltros(resultados, presentacion, laboratorio, true, soloPami);

    // 3. Ordenamiento explícito si no es "relevancia"
    if (orden !== 'relevancia') {
        resultados = ordenar(resultados, orden);
    }

    state.resultados = resultados;
}

// ── Acciones ──────────────────────────────────────────────────────────
// Todas siguen el mismo patrón: mutar el filtro correspondiente,
// recalcular resultados y notificar a los suscriptores.
export function setFiltroTexto(texto) {
    state.filtros.texto = texto;
    recalcularResultados();
    notificar();
}

export function setFiltroPresentacion(presentacion) {
    state.filtros.presentacion = presentacion;
    recalcularResultados();
    notificar();
}

export function setFiltroLaboratorio(laboratorio) {
    state.filtros.laboratorio = laboratorio;
    recalcularResultados();
    notificar();
}

export function setFiltroOrden(orden) {
    state.filtros.orden = orden;
    recalcularResultados();
    notificar();
}

export function setSoloPami(valor) {
    state.filtros.soloPami = valor;
    recalcularResultados();
    notificar();
}
/**
 * Resetea todos los filtros a su valor inicial y vacía resultados
 * directamente (no llama a recalcularResultados: volver al estado inicial
 * siempre implica mostrar el mensaje de bienvenida, no una búsqueda).
 */
export function limpiarFiltros() {
    state.filtros = { texto: '', presentacion: '', laboratorio: '', orden: 'relevancia', soloPami: false };
    state.resultados = [];
    notificar();
}

/**
 * Marca el estado de carga inicial (usado antes de que initStore() reciba
 * el dataset).
 */
export function setLoading(loading) {
    state.estaCargando = loading;
    notificar();
}

/**
 * Registra un error de carga y apaga el estado de "cargando" (se muestran
 * mutuamente excluyentes en la UI).
 */
export function setError(error) {
    state.error        = error;
    state.estaCargando = false;
    notificar();
}

// ── Inicialización ────────────────────────────────────────────────────
/**
 * Carga el dataset inicial en el store: setea todos, limpia resultados
 * (para mostrar el mensaje inicial en vez de la lista completa), apaga
 * el loading y calcula las opciones de filtro disponibles.
 */
export function initStore(medicamentos) {
    state.todos            = medicamentos;
    state.resultados       = [];   // ← vacío: muestra mensaje inicial
    state.estaCargando     = false;
    state.filtrosDisponibles = _extraerFiltros(medicamentos);
    notificar();
}


// ── Privado ───────────────────────────────────────────────────────────
/**
 * Extrae los valores únicos de presentación y laboratorio del dataset
 * completo (sin filtrar), excluyendo laboratorio "Desconocido", para
 * poblar los dropdowns de filtro al iniciar.
 */
function _extraerFiltros(meds) {
    const presentaciones = new Set();
    const laboratorios   = new Set();
    for (const m of meds) {
        if (m.presentacion) presentaciones.add(m.presentacion);
        if (m.laboratorio && m.laboratorio !== 'Desconocido') laboratorios.add(m.laboratorio);
    }
    return {
        presentaciones: [...presentaciones].sort(),
        laboratorios:   [...laboratorios].sort(),
    };
}

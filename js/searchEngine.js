// js/searchEngine.js — Índice invertido + ranking por relevancia y vigencia
import { normalizar } from './utils.js';

let indice = {};
let _todos  = [];

/**
 * Construye el índice invertido por prefijos de palabra (droga, marca,
 * laboratorio normalizados) para permitir búsqueda por coincidencia parcial
 * desde 2 caracteres. Reemplaza el índice anterior por completo.
 */
export function construirIndice(medicamentos) {
    _todos  = medicamentos;
    indice  = {};

    for (let i = 0; i < medicamentos.length; i++) {
        const m   = medicamentos[i];
        const txt = [m.droga, m.marca, m.laboratorio]
            .filter(Boolean).map(normalizar).join(' ');

        for (const palabra of txt.split(/\s+/)) {
            if (palabra.length < 2) continue;
            for (let k = 2; k <= palabra.length; k++) {
                const pref = palabra.slice(0, k);
                if (!indice[pref]) indice[pref] = new Set();
                indice[pref].add(i);
            }
        }
    }
}

/**
 * Calcula un score de relevancia textual para un medicamento dado un término.
 * Prioriza matches exactos de droga sobre marca sobre laboratorio.
 */
function scoreRelevancia(m, terminoNorm) {
    let score = 0;
    const droga = normalizar(m.droga || '');
    const marca = normalizar(m.marca || '');
    const lab   = normalizar(m.laboratorio || '');

    // Match exacto de droga: máxima prioridad
    if (droga === terminoNorm)       score += 100;
    else if (droga.startsWith(terminoNorm)) score += 80;
    else if (droga.includes(terminoNorm))   score += 50;

    // Match de marca
    if (marca === terminoNorm)       score += 40;
    else if (marca.startsWith(terminoNorm)) score += 25;
    else if (marca.includes(terminoNorm))   score += 15;

    // Match de laboratorio
    if (lab.includes(terminoNorm))   score += 5;

    return score;
}

/**
 * Busca y retorna resultados ordenados por:
 * 1. Relevancia textual (match de droga > marca > lab)
 * 2. vigencia_score (productos confiables primero)
 * 3. Precio (ascendente dentro del mismo nivel de vigencia)
 *
 * Productos con vigencia_score < 50 son degradados al final.
 */
export function buscar(texto) {
    const terminos = normalizar(texto).split(/\s+/).filter(t => t.length >= 2);
    if (!terminos.length) return [..._todos];

    // Intersección AND entre términos
    let sets = terminos.map(t => indice[t] || new Set());
    let ids  = sets[0];
    for (let i = 1; i < sets.length; i++) {
        ids = new Set([...ids].filter(id => sets[i].has(id)));
    }

    const terminoPrincipal = terminos[0];
    const resultados = [...ids].map(i => _todos[i]);

    // Ordenar: relevancia DESC, vigencia DESC, precio ASC
    return resultados.sort((a, b) => {
        const vigA = a.vigencia_score ?? 100;
        const vigB = b.vigencia_score ?? 100;

        // Sospechosos van al fondo (score < 50)
        const aEsSospechoso = vigA < 50;
        const bEsSospechoso = vigB < 50;
        if (aEsSospechoso !== bEsSospechoso) return aEsSospechoso ? 1 : -1;

        // Entre no-sospechosos: relevancia textual
        const relA = scoreRelevancia(a, terminoPrincipal);
        const relB = scoreRelevancia(b, terminoPrincipal);
        if (relA !== relB) return relB - relA;

        // Mismo nivel de relevancia: vigencia
        if (vigA !== vigB) return vigB - vigA;

        // Precio ascendente como desempate
        return (a.precio || 0) - (b.precio || 0);
    });
}

/**
 * Devuelve la lista completa de medicamentos cargados en el índice actual.
 */
export function getTodos() { return _todos; }

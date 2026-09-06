// js/infoAdicional.js — Carga en segundo plano de la info complementaria
const CACHE_KEY = 'info_adicional_v1';
const CACHE_TTL_MS = 2 * 60 * 60 * 1000; // 2 horas, igual criterio que dataLoader.js

let _promesaCarga = null;

/**
 * Carga (una sola vez, con cache en sessionStorage) el mapa hash -> info
 * complementaria. Es un dato secundario y no crítico: si falla
 * la carga, no debe interrumpir la app — se resuelve con un objeto vacío
 * y se loguea el error, dejando la lista principal de medicamentos intacta.
 */
export function cargarInfoAdicional() {
    if (_promesaCarga) return _promesaCarga;

    _promesaCarga = (async () => {
        try {
            const cached = sessionStorage.getItem(CACHE_KEY);
            if (cached) {
                const { ts, data } = JSON.parse(cached);
                if (Date.now() - ts < CACHE_TTL_MS) return data;
            }
        } catch { /* sessionStorage bloqueado: continuar */ }

        try {
            const res = await fetch('data/info-adicional/info_adicional.json', { cache: 'default' });
            if (!res.ok) throw new Error(`Error al cargar info adicional: ${res.status}`);
            const data = await res.json();
            try {
                sessionStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data }));
            } catch { /* sessionStorage lleno: no es crítico */ }
            return data;
        } catch (err) {
            console.warn('[infoAdicional] No se pudo cargar la info complementaria:', err);
            return {};
        }
    })();

    return _promesaCarga;
}

// js/uiRenderer.js — Renderizado con badges de vigencia y escape seguro
import { formatearPrecio, escapeHtml, extraerFiltros, normalizarLaboratorio, parsearPresentacion } from './utils.js';

// Mapa hash -> info complementaria. null mientras no se cargó
// todavía (ver infoAdicional.js, cargado en segundo plano desde main.js).
let _infoAdicionalMap = null;
// Elemento al que devolver el foco al cerrar el modal de info.
let _elQueVolverFoco = null;

/**
 * Registra el mapa de info adicional ya cargado para que
 * renderizarTarjeta() pueda decidir si mostrar el botón "+ Info".
 */
export function setInfoAdicionalMap(mapa) {
    _infoAdicionalMap = mapa || {};
}

/**
 * Muestra tarjetas placeholder animadas mientras cargan los datos reales.
 */
export function mostrarSkeleton() {
    const el = document.getElementById('resultados');
    if (!el || el.querySelector('.skeleton-card')) return;
    el.innerHTML = Array.from({length: 5}, () => `
        <div class="skeleton-card">
            <div class="sk sk-title"></div>
            <div class="sk sk-line"></div>
            <div class="sk sk-short"></div>
            <div class="sk sk-price"></div>
        </div>`).join('');
}

/**
 * Muestra el mensaje de bienvenida cuando todavía no hay búsqueda ni
 * filtro activo.
 */
export function mostrarMensajeInicial() {
    const el = document.getElementById('resultados');
    if (!el) return;
    el.innerHTML = `
        <div class="mensaje-inicial">
            <svg width="36" height="36" fill="none" stroke="#c8d8d8" stroke-width="1.5" viewBox="0 0 24 24">
                <circle cx="10" cy="10" r="7"/><line x1="15" y1="15" x2="21" y2="21"/>
            </svg>
            <p>Buscá por nombre comercial, principio activo o laboratorio</p>
        </div>`;
    document.getElementById('contador').innerHTML = '';
    _ocultarChip();
}

/**
 * Muestra un mensaje de error con botón de reintentar en el área de
 * resultados (ej. cuando falla la carga inicial de datos).
 */
export function mostrarError(msg) {
    const el = document.getElementById('resultados');
    if (!el) return;
    el.innerHTML = `
        <div class="mensaje-inicial">
            <svg width="32" height="32" fill="none" stroke="#e53935" stroke-width="1.5" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <p>${escapeHtml(msg)}</p>
            <button id="btnReintentar" class="btn-reintentar">Reintentar</button>
        </div>`;
    document.getElementById('contador').innerHTML = '';
    _ocultarChip();
}

/**
 * Rellena los dropdowns de presentación y laboratorio con los valores
 * únicos presentes en la lista, preservando la selección activa si sigue
 * siendo válida.
 */
export function cargarOpcionesFiltros(medicamentos, filtrosActivos = {}) {
    const { presentaciones, laboratorios } = extraerFiltros(medicamentos);
    const selP = document.getElementById('filtroPresentacion');
    const selL = document.getElementById('filtroLaboratorio');

    if (selP) {
        const presActual = filtrosActivos.presentacion || selP.value;
        selP.innerHTML = '<option value="">Presentación: Todas</option>';
        presentaciones.forEach(p => {
            const o = document.createElement('option');
            o.value = p;
            o.textContent = p.length > 60 ? p.slice(0,60)+'…' : p;
            if (p === presActual) o.selected = true;
            selP.appendChild(o);
        });
    }

    if (selL) {
        const labActual = filtrosActivos.laboratorio || selL.value;
        selL.innerHTML = '<option value="">Laboratorio: Todos</option>';
        laboratorios.forEach(l => {
            const o = document.createElement('option');
            o.value = l; o.textContent = l;
            if (l === labActual) o.selected = true;
            selL.appendChild(o);
        });
    }
}

/**
 * Escribe la fecha de última actualización del dataset en los elementos
 * de footer correspondientes, formateada como dd/mm/aaaa hh:mm.
 */
export function actualizarFechaEnFooter(fecha) {
    const ids = ['fecha-actualizacion', 'fecha-actualizacion-footer'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        if (!fecha) { el.textContent = ''; return; }
        try {
            const d   = new Date(fecha);
            const pad = n => String(n).padStart(2, '0');
            el.textContent = `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())} hs`;
        } catch { el.textContent = fecha; }
    });
}

/**
 * Muestra u oculta el chip que indica el criterio de orden activo.
 */
export function actualizarSortChip(texto) {
    const chip  = document.getElementById('sortChip');
    const label = document.getElementById('sortChipLabel');
    if (!chip || !label) return;
    if (!texto) { chip.classList.remove('visible'); return; }
    label.textContent = texto;
    chip.classList.add('visible');
}

function _ocultarChip() {
    document.getElementById('sortChip')?.classList.remove('visible');
}

// ── Hash de medicamento para compartir ────────────────────────────────
/**
 * Genera un hash legible y estable (slug de droga/marca/laboratorio/
 * presentación) para identificar un medicamento en la URL al compartirlo.
 */
export function hashMedicamento(med) {
    const slug = s => (s || '').toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '');
    return `${slug(med.droga)}--${slug(med.marca)}--${slug(med.laboratorio)}--${slug(med.presentacion)}`;
}

/**
 * Busca en la lista el medicamento cuyo hash (ver hashMedicamento) coincide
 * con el recibido, para resolver un link compartido.
 */
export function buscarPorHash(todos, hash) {
    return todos.find(m => hashMedicamento(m) === hash) || null;
}

// ── Compartir ─────────────────────────────────────────────────────────
/**
 * Comparte un medicamento vía Web Share API si está disponible, o copia
 * el link al portapapeles como fallback. Registra el evento en GA4 si
 * gtag está presente.
 */
export async function compartirMedicamento(med) {
    const hash = hashMedicamento(med);
    const url  = `${location.origin}${location.pathname}#${hash}`;
    const text = `${med.marca} (${med.droga}) — ${formatearPrecio(med.precio)} | remedi.ar`;

    // Tracker GA4
    if (typeof gtag === 'function') {
        gtag('event', 'share', {
            method: navigator.share ? 'native' : 'clipboard',
            content_type: 'medicamento',
            item_id: `${med.droga}--${med.marca}`,
        });
    }

    if (navigator.share) {
        try {
            await navigator.share({ title: med.marca, text, url });
            return;
        } catch (e) {
            if (e.name === 'AbortError') return;
        }
    }

    try {
        await navigator.clipboard.writeText(url);
        _mostrarToast('¡Link copiado!');
    } catch {
        _mostrarToast('No se pudo copiar el link');
    }
}

function _mostrarToast(msg) {
    let toast = document.getElementById('share-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'share-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('visible');
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => toast.classList.remove('visible'), 2000);
}

// ── SVG íconos ────────────────────────────────────────────────────────
const SVG_SHARE = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
    <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
</svg>`;

const SVG_COPY = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
</svg>`;

const SVG_INFO = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
</svg>`;

function renderBotonCompartir() {
    const tieneShare = !!navigator.share;
    const icono = tieneShare ? SVG_SHARE : SVG_COPY;
    const texto = tieneShare ? 'Compartir' : 'Copiar link';
    return `<button class="btn-compartir" aria-label="Compartir medicamento">
        ${icono}<span>${texto}</span>
    </button>`;
}

/**
 * Botón "+ Info" que abre el modal con info adicional. Solo se renderiza
 * si el mapa ya cargó Y tiene una entrada para este hash (el mapa cubre
 * ~56% de los medicamentos; para el resto no hay nada que mostrar).
 */
function renderBotonInfo(hash) {
    if (!_infoAdicionalMap || !_infoAdicionalMap[hash]) return '';
    return `<button class="btn-info-adicional" aria-label="Ver información adicional del medicamento" data-hash="${escapeHtml(hash)}">
        ${SVG_INFO}<span>+ Info</span>
    </button>`;
}

// ── Presentación y precios ────────────────────────────────────────────
/**
 * Arma los chips de dosis/forma/cantidad para una tarjeta. Prioriza los
 * campos pres_forma/pres_dosis/pres_cantidad ya extraídos por el ETL; si
 * no están, cae a parsear el campo presentacion crudo en el cliente.
 */
function renderPresentacion(med) {
    const p = (med.pres_forma || med.pres_dosis)
        ? { forma: med.pres_forma || null, dosis: med.pres_dosis ? `${med.pres_dosis}${med.pres_unidad ? ' ' + med.pres_unidad : ''}` : null, cantidad: med.pres_cantidad || null }
        : parsearPresentacion(med.presentacion);
    if (!p) return `<span class="celda valor">${escapeHtml(med.presentacion || 'N/A')}</span>`;
    return `<div class="pres-tabla">
        ${p.dosis    ? `<span class="pres-chip pres-dosis">${escapeHtml(p.dosis)}</span>` : ''}
        ${p.forma    ? `<span class="pres-chip pres-forma">${escapeHtml(p.forma)}</span>` : ''}
        ${p.cantidad ? `<span class="pres-chip pres-cant">× ${escapeHtml(p.cantidad)}</span>` : ''}
    </div>`;
}

/**
 * Renderiza el precio público y, si aplica, el copago PAMI calculado.
 * Con soloPami activo, prioriza mostrar el precio con cobertura primero.
 */
function renderPrecios(med, soloPami) {
    const copago = med.pami_cobertura
        ? Math.round(med.precio * (1 - med.pami_cobertura / 100))
        : null;
    if (soloPami && copago != null) {
        return `
        <span class="precio-publico precio-pami">${formatearPrecio(copago)}</span>
        <span class="precio-sin-cobertura">Precio sin cobertura ${formatearPrecio(med.precio)}</span>`;
    }
    return `
    <span class="precio-publico">${formatearPrecio(med.precio)}</span>
    ${med.pami_cobertura ? `
    <div class="pami-info">
        <span class="pami-chip">Cobertura PAMI ${med.pami_cobertura}% · ${formatearPrecio(copago)}</span>
    </div>` : ''}`;
}

// ── Tarjeta ───────────────────────────────────────────────────────────
/**
 * Arma el HTML completo de una tarjeta de medicamento: header, principio
 * activo, presentación, precios y botón de compartir. Todo el contenido
 * dinámico pasa por escapeHtml antes de insertarse.
 */
function renderizarTarjeta(med, soloPami = false, destacada = false) {
    const esSosp = (med.vigencia_score ?? 100) < 50;
    const hash = hashMedicamento(med);
    const clases = [
        'tarjeta',
        esSosp    ? 'tarjeta-sospechosa' : '',
        destacada ? 'tarjeta-destacada'  : '',
    ].filter(Boolean).join(' ');

    return `
        <article class="${clases}" data-hash="${escapeHtml(hash)}">
            ${destacada ? '<div class="badge-compartida">Producto compartido</div>' : ''}
            ${badgeVigencia(med)}
            <div class="tarjeta-header">
                <h3 class="marca-tarjeta">${escapeHtml(med.marca || 'N/A')}</h3>
                <span class="laboratorio-badge">${escapeHtml(normalizarLaboratorio(med.laboratorio) || 'N/A')}</span>
            </div>
            <div class="fila-tabla">
                <span class="celda etiqueta">
                    <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                        <path d="M2 15c6.667-6 13.333 0 20-6"/><path d="M2 9c6.667 6 13.333 0 20 6"/>
                    </svg>
                    Principio activo
                </span>
                <span class="celda valor uppercase">${escapeHtml(med.droga || 'N/A')}</span>
            </div>
            <div class="fila-tabla fila-presentacion">
                <span class="celda etiqueta">
                    <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                    </svg>
                    Presentación
                </span>
                ${renderPresentacion(med)}
            </div>
            <div class="fila-precios">
                ${renderPrecios(med, soloPami)}
            </div>
            <div class="tarjeta-footer">
                ${renderBotonInfo(hash)}
                ${renderBotonCompartir()}
            </div>
        </article>`;
}

// ── Render principal ──────────────────────────────────────────────────
/**
 * Renderiza la lista de resultados: mensaje de "sin resultados" si está
 * vacía, contador con aviso de sospechosos si corresponde, y hasta 300
 * tarjetas (el medicamento destacado, si hay, siempre primero).
 */
export function mostrarResultados(lista, termino = '', soloPami = false, medDestacada = null) {
    const cont = document.getElementById('resultados');
    const ctr  = document.getElementById('contador');
    if (!cont) return;

    if (!lista?.length && !medDestacada) {
        cont.innerHTML = `
            <div class="mensaje-inicial">
                <svg width="32" height="32" fill="none" stroke="#c8d8d8" stroke-width="1.5" viewBox="0 0 24 24">
                    <circle cx="10" cy="10" r="7"/><line x1="15" y1="15" x2="21" y2="21"/>
                </svg>
                <p>No se encontraron resultados${termino ? ` para "<strong>${escapeHtml(termino)}</strong>"` : ''}.</p>
            </div>`;
        ctr.innerHTML = '0 resultados';
        _ocultarChip();
        return;
    }

    const MAX       = 300;
    const total     = lista.length;
    const suspCount = lista.filter(m => (m.vigencia_score ?? 100) < 50).length;
    const unidad    = total === 1 ? 'resultado' : 'resultados';

    let ctrHtml = total > MAX
        ? `<strong>${total.toLocaleString('es-AR')} ${unidad}</strong> (mostrando los primeros ${MAX})`
        : `<strong>${total.toLocaleString('es-AR')} ${unidad}</strong>`;

    if (suspCount > 0) {
        ctrHtml += ` <span class="ctr-sospechosos">(${suspCount} con precio a verificar, al final)</span>`;
    }

    ctr.innerHTML = ctrHtml;

    const hashDest    = medDestacada ? hashMedicamento(medDestacada) : null;
    const similares   = hashDest ? lista.filter(m => hashMedicamento(m) !== hashDest) : lista;
    const htmlDest    = medDestacada ? renderizarTarjeta(medDestacada, soloPami, true) : '';
    const separador   = medDestacada && similares.length
        ? '<div class="separador-similares"><span>Productos similares</span></div>'
        : '';

    cont.innerHTML = htmlDest + separador + similares.slice(0, MAX).map(m => renderizarTarjeta(m, soloPami)).join('');

    _ocultarChip();
}

/**
 * Genera el badge de vigencia (precio sospechoso/desactualizado/a verificar)
 * según vigencia_score y flags calculados por el ETL. Sin badge si el score
 * es alto y no hay flags. Definición ubicada después de las funciones que
 * la usan para mantener el archivo en orden de "flujo de renderizado".
 */
function badgeVigencia(med) {
    const flags = med.flags || [];
    const score = med.vigencia_score ?? 100;

    if (score >= 70 && flags.length === 0) return '';

    let msg = '';
    let cls = '';

    if (flags.includes('precio_obsoleto') && score < 50) {
        msg = '⚠ Precio posiblemente desactualizado';
        cls = 'badge-sospechoso';
    } else if (flags.includes('precio_bajo') && score < 50) {
        msg = '⚠ Precio bajo - verificar';
        cls = 'badge-sospechoso';
    } else if (flags.includes('precio_bajo')) {
        msg = '⚠ Precio bajo';
        cls = 'badge-verificar';
    } else if (flags.includes('precio_sospechoso')) {
        msg = '⚠ Precio a verificar';
        cls = 'badge-verificar';
    } else {
        return '';
    }

    return `<div class="vigencia-badge ${escapeHtml(cls)}" title="Score: ${score}/100 — Flags: ${escapeHtml(flags.join(', '))}">
        ${escapeHtml(msg)}
    </div>`;
}

// ── Modal de información complementaria ─────────────────────────────────
/**
 * Escapa texto para HTML preservando saltos de línea como <br>. Algunos
 * campos (drogas, clases_terapeuticas) traen varios ítems
 * separados por '\n' cuando el medicamento tiene más de un valor.
 */
function _escapeConSaltos(texto) {
    return (texto || '').split('\n').map(escapeHtml).join('<br>');
}

/**
 * Abre el modal con la información complementaria para el
 * medicamento cuyo hash se recibe. No hace nada si el mapa todavía no
 * cargó o no hay info para ese hash (no debería ocurrir: el botón que
 * dispara esto solo se renderiza cuando sí hay datos).
 */
export function abrirModalInfo(hash) {
    const info = _infoAdicionalMap && _infoAdicionalMap[hash];
    if (!info) return;

    const modal = _obtenerModalInfo();
    const panel = modal.querySelector('.modal-info-panel');

    const filas = [
        ['Laboratorio', info.laboratorio],
        ['Droga(s)', info.drogas],
        ['Clasificación ATC', info.atc],
        ['Clases terapéuticas', info.clases_terapeuticas],
    ].filter(([, valor]) => valor);

    let vigenciaHtml = '';
    if (info.vigencia?.estado) {
        const esVigente = info.vigencia.estado === 'vigente';
        vigenciaHtml = `<div class="modal-info-vigencia ${esVigente ? 'vigente' : 'discontinuado'}">
            ${esVigente ? '✓ Alta vigente' : '⚠ Baja registrada'}
            ${info.vigencia.fecha_alta ? ` · alta ${escapeHtml(info.vigencia.fecha_alta)}` : ''}
            ${info.vigencia.fecha_baja ? ` · baja ${escapeHtml(info.vigencia.fecha_baja)}` : ''}
        </div>`;
    }

    panel.innerHTML = `
        <button type="button" class="modal-info-cerrar" aria-label="Cerrar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
        <h3 class="modal-info-titulo">Información adicional</h3>
        ${vigenciaHtml}
        <dl class="modal-info-lista">
            ${filas.map(([label, valor]) => `
                <dt>${escapeHtml(label)}</dt>
                <dd>${_escapeConSaltos(valor)}</dd>
            `).join('')}
        </dl>
        <p class="modal-info-fuente">${info.inferido
            ? 'Clasificación general de la droga, no específica de este producto — puede no reflejar cambios recientes.'
            : 'Información de referencia, puede no reflejar cambios recientes.'}</p>`;

    _elQueVolverFoco = document.activeElement;
    modal.classList.add('visible');
    modal.querySelector('.modal-info-cerrar')?.focus();
    document.body.style.overflow = 'hidden';
}

function _cerrarModalInfo() {
    const modal = document.getElementById('info-adicional-modal');
    if (!modal || !modal.classList.contains('visible')) return;
    modal.classList.remove('visible');
    document.body.style.overflow = '';
    _elQueVolverFoco?.focus?.();
    _elQueVolverFoco = null;
}

/**
 * Crea (una sola vez, de forma perezosa) el overlay del modal y sus
 * listeners de cierre (click en backdrop, click en botón cerrar, tecla
 * Escape). Mismo patrón que _mostrarToast: crear el elemento en el DOM
 * la primera vez que hace falta, reusarlo después.
 */
function _obtenerModalInfo() {
    let modal = document.getElementById('info-adicional-modal');
    if (modal) return modal;

    modal = document.createElement('div');
    modal.id = 'info-adicional-modal';
    modal.className = 'modal-info-overlay';
    modal.innerHTML = `<div class="modal-info-panel" role="dialog" aria-modal="true" aria-label="Información adicional del medicamento"></div>`;
    document.body.appendChild(modal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal || e.target.closest('.modal-info-cerrar')) _cerrarModalInfo();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') _cerrarModalInfo();
    });

    return modal;
}

// js/main.js — Orquestador principal
import { cargarDatos }                            from './dataLoader.js';
import { construirIndice, buscar }                from './searchEngine.js';
import { aplicarFiltros, ordenar }               from './filters.js';
import {
    mostrarSkeleton, mostrarMensajeInicial, mostrarError,
    mostrarResultados, cargarOpcionesFiltros, actualizarFechaEnFooter,
    hashMedicamento, buscarPorHash, compartirMedicamento,
    setInfoAdicionalMap, abrirModalInfo,
} from './uiRenderer.js';
import { cargarInfoAdicional } from './infoAdicional.js';
import {
    getState, getResultados, getFiltros, getTodos,
    setFiltroTexto, setFiltroPresentacion,
    setFiltroLaboratorio, setFiltroOrden, setSoloPami, limpiarFiltros, getResultadosSinFiltros,
    setLoading, setError, initStore, suscribirse,
} from './store.js';

let timeout       = null;
let medDestacada  = null;  // medicamento llegado por hash en URL

// ── Suscripción al store ───────────────────────────────────────────────
function _render(state) {
    const { resultados, filtros } = state;

    const hayTexto  = filtros.texto && filtros.texto.trim().length >= 2;
    const hayFiltro = !!(filtros.presentacion || filtros.laboratorio);

    if (!hayTexto && !hayFiltro && !medDestacada) {
        mostrarMensajeInicial();
        return;
    }

    const sinFiltros    = getResultadosSinFiltros();
    const baseDropdown  = sinFiltros.length > 0 ? sinFiltros : getTodos();
    cargarOpcionesFiltros(baseDropdown, filtros);

    mostrarResultados(resultados, filtros.texto, filtros.soloPami, medDestacada);
}

suscribirse(_render);

// ── Handlers ──────────────────────────────────────────────────────────
function onInput() {
    clearTimeout(timeout);
    const q = document.getElementById('buscador').value.trim();

    const btnLimpiar = document.getElementById('btnLimpiar');
    if (btnLimpiar) btnLimpiar.style.display = q ? 'flex' : 'none';

    if (!q || q.length < 2) {
        const hayFiltro = !!(document.getElementById('filtroPresentacion')?.value || document.getElementById('filtroLaboratorio')?.value);
        if (!hayFiltro && !medDestacada) mostrarMensajeInicial();
        setFiltroTexto('');
        _actualizarURL('');
        return;
    }

    timeout = setTimeout(() => {
        medDestacada = null;  // nueva búsqueda limpia la destacada
        setFiltroTexto(q);
        _actualizarURL(q);
    }, 250);
}

function onBuscar() {
    clearTimeout(timeout);
    const q = document.getElementById('buscador').value.trim();
    medDestacada = null;
    setFiltroTexto(q);
    _actualizarURL(q);
}

function onFiltroPresentacionChange() {
    setFiltroPresentacion(document.getElementById('filtroPresentacion')?.value || '');
}

function onFiltroLaboratorioChange() {
    setFiltroLaboratorio(document.getElementById('filtroLaboratorio')?.value || '');
}

function onOrdenChange() {
    setFiltroOrden(document.getElementById('ordenPrecio')?.value || 'relevancia');
}

function onLimpiar() {
    const ids = ['buscador', 'filtroPresentacion', 'filtroLaboratorio'];
    ids.forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    const sel = document.getElementById('ordenPrecio');
    if (sel) sel.value = 'relevancia';
    const togglePami = document.getElementById('togglePami');
    if (togglePami) togglePami.checked = false;

    medDestacada = null;
    history.replaceState(null, '', location.pathname + location.search.replace(/[?&]?q=[^&]*/g, ''));
    location.hash = '';

    limpiarFiltros();
    mostrarMensajeInicial();
    cargarOpcionesFiltros(getTodos());
    _actualizarURL('');

    const btnLimpiar = document.getElementById('btnLimpiar');
    if (btnLimpiar) btnLimpiar.style.display = 'none';

    document.getElementById('buscador')?.focus();
}

// ── Compartir: escuchar evento delegado desde uiRenderer ──────────────
function _initCompartir() {
    document.getElementById('resultados')?.addEventListener('compartir-med', async (e) => {
        const { hash } = e.detail;
        const med = getTodos().find(m => hashMedicamento(m) === hash);
        if (med) await compartirMedicamento(med);
    });

    // Delegación directa como fallback (click en btn-compartir)
    document.getElementById('resultados')?.addEventListener('click', async (e) => {
        const btn = e.target.closest('.btn-compartir');
        if (!btn) return;
        const article = btn.closest('article[data-hash]');
        if (!article) return;
        const med = getTodos().find(m => hashMedicamento(m) === article.dataset.hash);
        if (med) await compartirMedicamento(med);
    });
}

// ── Info adicional: escuchar click delegado ─────────────────────────────
function _initInfoModal() {
    document.getElementById('resultados')?.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-info-adicional');
        if (!btn) return;
        abrirModalInfo(btn.dataset.hash);
    });
}

// ── Persistencia URL ──────────────────────────────────────────────────
function _actualizarURL(q) {
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q);
    else   url.searchParams.delete('q');
    history.replaceState(null, '', url.toString());
}

// ── Hash en URL: medicamento compartido ──────────────────────────────
function _resolverHash() {
    const hash = location.hash.slice(1); // quitar el #
    if (!hash || !hash.includes('--')) return null;
    return buscarPorHash(getTodos(), hash);
}

// ── Botón scroll-to-top ───────────────────────────────────────────────
function _initScrollTop() {
    let btn = document.getElementById('btnTop');
    if (!btn) {
        btn = document.createElement('button');
        btn.id        = 'btnTop';
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><polyline points="18 15 12 9 6 15"/></svg>`;
        btn.setAttribute('aria-label', 'Volver arriba');
        document.body.appendChild(btn);
    }
    window.addEventListener('scroll', () => {
        btn.classList.toggle('visible', window.scrollY > 300);
    }, { passive: true });
    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ── Init ──────────────────────────────────────────────────────────────
async function init() {
    mostrarSkeleton();
    setLoading(true);
    _initScrollTop();

    try {
        const data = await cargarDatos();
        const medicamentos = data.medicamentos || [];
        construirIndice(medicamentos);
        initStore(medicamentos);
        cargarOpcionesFiltros(medicamentos);
        actualizarFechaEnFooter(data.fecha);

        // Resolver hash (medicamento compartido) primero
        medDestacada = _resolverHash();

        if (medDestacada) {
            // Buscar productos similares por droga
            setFiltroTexto(medDestacada.droga);
            document.getElementById('buscador').value = medDestacada.droga;
        } else {
            // Restaurar búsqueda desde URL
            const q = new URLSearchParams(window.location.search).get('q');
            if (q && q.length >= 2) {
                document.getElementById('buscador').value = q;
                setFiltroTexto(q);
            } else {
                mostrarMensajeInicial();
            }
        }

        setLoading(false);

        // Info complementaria: se carga en segundo plano (no
        // bloquea el render principal). Cuando esté lista, se re-renderiza
        // para que aparezcan los botones "+ Info" en las tarjetas visibles.
        cargarInfoAdicional().then(mapa => {
            setInfoAdicionalMap(mapa);
            _render(getState());
        });
    } catch (err) {
        console.error(err);
        const msg = 'No se pudieron cargar los datos. Intentá recargar la página.';
        setError(msg);
        mostrarError(msg);
        document.getElementById('btnReintentar')?.addEventListener('click', () => {
            location.reload();
        });
        return;
    }

    // Event listeners
    document.getElementById('buscador')?.addEventListener('input', onInput);
    document.getElementById('buscador')?.addEventListener('keydown', e => {
        if (e.key === 'Enter') onBuscar();
    });
    document.getElementById('btnBuscar')?.addEventListener('click', onBuscar);
    document.getElementById('btnLimpiar')?.addEventListener('click', onLimpiar);
    document.getElementById('filtroPresentacion')?.addEventListener('change', onFiltroPresentacionChange);
    document.getElementById('filtroLaboratorio')?.addEventListener('change', onFiltroLaboratorioChange);
    document.getElementById('ordenPrecio')?.addEventListener('change', onOrdenChange);
    document.getElementById('togglePami')?.addEventListener('change', e => setSoloPami(e.target.checked));

    _initCompartir();
    _initInfoModal();
}

init();

// PWA install prompt
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    document.getElementById('btnInstalarApp').style.display = 'inline-flex';
});

document.getElementById('btnInstalarApp')?.addEventListener('click', async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    deferredPrompt = null;
    document.getElementById('btnInstalarApp').style.display = 'none';
});

window.addEventListener('appinstalled', () => {
    document.getElementById('btnInstalarApp').style.display = 'none';
    deferredPrompt = null;
});

// PWA install — instrucciones manuales para iOS (Safari no dispara beforeinstallprompt)
(function initInstalarIOS() {
    const esIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const yaInstalada = window.navigator.standalone === true
        || window.matchMedia('(display-mode: standalone)').matches;
    const descartado = localStorage.getItem('ios_install_tip_descartado') === '1';

    if (!esIOS || yaInstalada || descartado) return;

    const wrap = document.getElementById('iosInstalarWrap');
    const btn = document.getElementById('btnInstalarIOS');
    const tip = document.getElementById('iosInstalarTip');
    const btnCerrar = document.getElementById('btnCerrarIosTip');
    if (!wrap || !btn || !tip) return;

    wrap.classList.remove('hidden');

    btn.addEventListener('click', () => {
        const abierto = !tip.classList.contains('hidden');
        tip.classList.toggle('hidden', abierto);
        btn.setAttribute('aria-expanded', String(!abierto));
    });

    btnCerrar?.addEventListener('click', (e) => {
        e.stopPropagation();
        tip.classList.add('hidden');
        btn.setAttribute('aria-expanded', 'false');
        localStorage.setItem('ios_install_tip_descartado', '1');
        wrap.classList.add('hidden');
    });

    document.addEventListener('click', (e) => {
        if (!wrap.contains(e.target)) {
            tip.classList.add('hidden');
            btn.setAttribute('aria-expanded', 'false');
        }
    });
})();

window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
        const cache = sessionStorage.getItem('remedios_data_v2');
        if (cache) {
            const { ts } = JSON.parse(cache);
            const edad = Date.now() - ts;
            if (edad > 2 * 60 * 60 * 1000) {
                sessionStorage.removeItem('remedios_data_v2');
            }
        }
    }
});
async function cargarVersionFooter() {
    const el = document.getElementById('footer-version');
    if (!el) return;
    try {
        const res = await fetch('package.json', { cache: 'no-cache' });
        if (!res.ok) throw new Error('no ok');
        const pkg = await res.json();
        el.textContent = 'v' + pkg.version;
    } catch {
        el.remove();
    }
}

cargarVersionFooter();

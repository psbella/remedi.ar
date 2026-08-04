// admin.js — panel de administración de outliers
// Movido fuera de admin.html porque la CSP (script-src 'self' + hashes fijos
// de index.html) bloqueaba tanto el <script> inline como los onclick="".
// Como archivo externo queda cubierto por 'self', sin agregar hashes nuevos
// (mismo criterio que js/landing.js, ver _headers).

// ── Config ────────────────────────────────────────────────────────────────
const REPO   = 'psbella/remediar';
const REPORT = 'data/outlier_report.json';
const BL_PATH = 'data/blacklist.json';

let TOKEN  = '';
let BRANCH = 'main';
let allOutliers   = [];
let blacklist     = {};   // key → {droga, marca, presentacion, laboratorio, motivo, fecha}
let blacklistSha  = null;
let filtroActual  = 'todos';
let seleccionados = new Set();
let sortCol = null;   // null = orden original del reporte
let sortDir = 1;      // 1 = ascendente, -1 = descendente

// ── Helpers ───────────────────────────────────────────────────────────────
function makeKey(m) {
  return [m.droga, m.marca, m.presentacion, m.laboratorio]
    .map(s => (s || '').trim().toLowerCase()).join('|');
}

function formatPrecio(p) {
  if (!p && p !== 0) return '—';
  return '$' + Number(p).toLocaleString('es-AR', {minimumFractionDigits:2, maximumFractionDigits:2});
}

function toast(msg, tipo = 'success') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'show ' + tipo;
  setTimeout(() => el.className = '', 3000);
}

function setStatus(ok, txt) {
  document.getElementById('status-dot').className = 'dot ' + (ok ? 'ok' : 'err');
  document.getElementById('status-text').textContent = txt;
}

// ── Auth ──────────────────────────────────────────────────────────────────
async function conectar() {
  TOKEN  = document.getElementById('token-input').value.trim();
  BRANCH = document.getElementById('branch-input').value.trim() || 'main';
  if (!TOKEN) { toast('Ingresá un token', 'error'); return; }

  setStatus(false, 'conectando…');
  try {
    await cargarDatos();
    document.getElementById('auth-gate').style.display   = 'none';
    document.getElementById('main-panel').style.display  = 'block';
    setStatus(true, 'conectado · ' + REPO);
  } catch(e) {
    setStatus(false, 'error de conexión');
    toast('No se pudo conectar: ' + e.message, 'error');
  }
}

// ── GitHub API ────────────────────────────────────────────────────────────
async function ghGet(path) {
  const r = await fetch(`https://api.github.com/repos/${REPO}/contents/${path}?ref=${BRANCH}`, {
    headers: { Authorization: `Bearer ${TOKEN}`, Accept: 'application/vnd.github.v3+json' }
  });
  if (!r.ok) throw new Error(`GitHub ${r.status}: ${path}`);
  const data = await r.json();
  const content = JSON.parse(atob(data.content.replace(/\n/g, '')));
  return { content, sha: data.sha };
}

async function ghPut(path, content, sha, message) {
  const body = {
    message,
    content: btoa(unescape(encodeURIComponent(JSON.stringify(content, null, 2)))),
    branch: BRANCH,
  };
  if (sha) body.sha = sha;
  const r = await fetch(`https://api.github.com/repos/${REPO}/contents/${path}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      Accept: 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = await r.json();
    const e = new Error(err.message || `GitHub ${r.status}`);
    e.status = r.status;
    e.isShaConflict = r.status === 409;
    throw e;
  }
  return await r.json();
}

// ── Cargar datos ──────────────────────────────────────────────────────────
async function cargarDatos() {
  document.getElementById('tabla-body').innerHTML =
    '<tr><td colspan="8"><div class="empty"><div class="spinner"></div><br>Cargando…</div></td></tr>';

  // outlier_report.json
  const { content: report } = await ghGet(REPORT);
  allOutliers = report.outliers || [];

  // stats
  document.getElementById('stat-total').textContent  = allOutliers.length;
  document.getElementById('stat-criticos').textContent =
    allOutliers.filter(o => o.precio_outlier_tipo === 'bajo_critico').length;
  document.getElementById('stat-fecha').textContent =
    (report.timestamp || '—').slice(0, 16).replace('T', ' ');

  // blacklist.json (puede no existir aún)
  try {
    const bl = await ghGet(BL_PATH);
    blacklist    = bl.content;
    blacklistSha = bl.sha;
  } catch(e) {
    blacklist    = {};
    blacklistSha = null;
  }

  document.getElementById('stat-blacklist').textContent = Object.keys(blacklist).length;

  seleccionados.clear();
  actualizarBtnBlacklist();
  renderTabla();
}

// ── Render ────────────────────────────────────────────────────────────────
function getOutliersFiltrados() {
  if (filtroActual === 'criticos')
    return allOutliers.filter(o => o.precio_outlier_tipo === 'bajo_critico');
  if (filtroActual === 'sospechosos')
    return allOutliers.filter(o => ['bajo_relativo','bajo_iqr','bajo_absoluto'].includes(o.precio_outlier_tipo));
  if (filtroActual === 'blacklisted')
    return allOutliers.filter(o => makeKey(o) in blacklist);
  return allOutliers;
}

function valorOrdenable(o, col) {
  if (col === 'ratio') {
    return (o.precio && o.mediana_droga) ? o.precio / o.mediana_droga : null;
  }
  return o[col];
}

function ordenarLista(lista) {
  if (!sortCol) return lista;
  // copia: no mutar allOutliers
  return [...lista].sort((a, b) => {
    const va = valorOrdenable(a, sortCol);
    const vb = valorOrdenable(b, sortCol);
    // los valores faltantes van siempre al final, sea cual sea la dirección
    if (va == null && vb == null) return 0;
    if (va == null) return 1;
    if (vb == null) return -1;
    if (typeof va === 'number' && typeof vb === 'number') {
      return (va - vb) * sortDir;
    }
    return String(va).localeCompare(String(vb), 'es', { sensitivity: 'base' }) * sortDir;
  });
}

function renderTabla() {
  const lista = ordenarLista(getOutliersFiltrados());
  document.getElementById('toolbar-label').textContent =
    `${lista.length} registros · filtro: ${filtroActual}`;

  actualizarFlechasOrden();

  if (!lista.length) {
    document.getElementById('tabla-body').innerHTML =
      '<tr><td colspan="8"><div class="empty">Sin registros para este filtro</div></td></tr>';
    return;
  }

  document.getElementById('tabla-body').innerHTML = lista.map(o => {
    const key   = makeKey(o);
    const enBL  = key in blacklist;
    const sel   = seleccionados.has(key);
    const ratio = o.precio && o.mediana_droga
      ? (o.precio / o.mediana_droga * 100).toFixed(1) + '%'
      : '—';
    const ratioCls = !o.precio || !o.mediana_droga ? 'ok'
      : (o.precio / o.mediana_droga < 0.10) ? 'critico' : 'sospecho';

    return `
    <tr class="${enBL ? 'blacklisted' : ''}" data-key="${key}">
      <td><input type="checkbox" class="row-check" data-key="${key}" ${sel ? 'checked' : ''} ${enBL ? 'disabled' : ''}></td>
      <td>
        <div class="marca">${o.marca || '—'}</div>
        <div class="droga">${o.droga || '—'}</div>
        <div class="lab">${o.laboratorio || '—'}</div>
      </td>
      <td class="td-presentacion">${o.presentacion || '—'}</td>
      <td>
        <div class="precio">${formatPrecio(o.precio)}</div>
      </td>
      <td>
        <div class="precio-mediana">${formatPrecio(o.mediana_droga)}</div>
        <div class="n-droga-count">${o.n_droga || '?'} registros</div>
      </td>
      <td><span class="ratio ${ratioCls}">${ratio}</span></td>
      <td><span class="tipo-badge tipo-${o.precio_outlier_tipo || ''}">${o.precio_outlier_tipo || '—'}</span></td>
      <td>
        ${enBL
          ? `<span class="blacklist-badge">bloqueado</span>
             <button class="btn btn-ghost btn-sm mt-sm" data-action="desbloquear" data-key="${key}">desbloquear</button>`
          : `<button class="btn btn-danger btn-sm" data-action="bloquear" data-key="${key}" data-marca="${(o.marca||'').replace(/"/g,'&quot;')}">⛔ bloquear</button>`
        }
      </td>
    </tr>`;
  }).join('');
}

function actualizarFlechasOrden() {
  document.querySelectorAll('th.sortable').forEach(th => {
    const arrow = th.querySelector('.sort-arrow');
    if (th.dataset.sort === sortCol) {
      th.classList.add('sorted');
      arrow.textContent = sortDir === 1 ? '▲' : '▼';
    } else {
      th.classList.remove('sorted');
      arrow.textContent = '';
    }
  });
}

// ── Selección ─────────────────────────────────────────────────────────────
function toggleSel(key, cb) {
  cb.checked ? seleccionados.add(key) : seleccionados.delete(key);
  actualizarBtnBlacklist();
}

function toggleAll(masterCb) {
  const lista = getOutliersFiltrados();
  lista.forEach(o => {
    const key = makeKey(o);
    if (key in blacklist) return;
    masterCb.checked ? seleccionados.add(key) : seleccionados.delete(key);
  });
  renderTabla();
  actualizarBtnBlacklist();
}

function seleccionarTodos() {
  document.getElementById('check-all').checked = true;
  toggleAll(document.getElementById('check-all'));
}

function actualizarBtnBlacklist() {
  const btn = document.getElementById('btn-blacklist');
  btn.disabled = seleccionados.size === 0;
  btn.textContent = seleccionados.size > 0
    ? `⛔ Bloquear ${seleccionados.size} seleccionado${seleccionados.size > 1 ? 's' : ''}`
    : '⛔ Bloquear seleccionados';
}

// ── Blacklist ─────────────────────────────────────────────────────────────
function construirEntrada(o) {
  return {
    droga:        o.droga,
    marca:        o.marca,
    presentacion: o.presentacion,
    laboratorio:  o.laboratorio,
    precio_detectado: o.precio,
    tipo:         o.precio_outlier_tipo,
    motivo:       (o.razones || []).join(' | '),
    bloqueado_en: new Date().toISOString().slice(0, 16),
  };
}

// Aplica `mutator` sobre el estado REMOTO más reciente de blacklist.json
// (no sobre el `blacklist` local, que puede estar desactualizado si hay
// otra pestaña u otro click en curso) y reintenta una vez si GitHub
// responde 409 por sha desincronizado.
async function actualizarBlacklist(mutator, mensaje) {
  for (let intento = 0; intento < 2; intento++) {
    // Releer siempre antes de escribir: minimiza la ventana de conflicto
    // y, si igual hay condición de carrera, el reintento la resuelve.
    let fresco, freshSha;
    try {
      const r = await ghGet(BL_PATH);
      fresco = r.content;
      freshSha = r.sha;
    } catch (e) {
      fresco = {};       // blacklist.json puede no existir aún
      freshSha = null;
    }

    mutator(fresco);

    try {
      const result = await ghPut(BL_PATH, fresco, freshSha, mensaje);
      blacklist    = fresco;
      blacklistSha = result.content.sha;
      document.getElementById('stat-blacklist').textContent = Object.keys(blacklist).length;
      return;
    } catch (e) {
      if (e.isShaConflict && intento === 0) continue;  // reintentar con sha fresco
      throw e;
    }
  }
}

async function bloquearUno(key, marca) {
  const outlier = allOutliers.find(o => makeKey(o) === key);
  if (!outlier) return;
  try {
    await actualizarBlacklist(bl => { bl[key] = construirEntrada(outlier); }, `admin: bloquear ${marca}`);
    toast(`${marca} agregado a lista negra`);
    renderTabla();
  } catch(e) {
    toast('Error al guardar: ' + e.message, 'error');
  }
}

async function agregarSeleccionados() {
  if (!seleccionados.size) return;
  const btn = document.getElementById('btn-blacklist');
  btn.disabled = true;
  btn.textContent = 'guardando…';

  const pendientes = [...seleccionados]
    .map(key => allOutliers.find(o => makeKey(o) === key))
    .filter(Boolean);

  try {
    await actualizarBlacklist(bl => {
      pendientes.forEach(o => { bl[makeKey(o)] = construirEntrada(o); });
    }, `admin: bloquear ${pendientes.length} outliers`);
    toast(`${pendientes.length} medicamento${pendientes.length > 1 ? 's' : ''} bloqueado${pendientes.length > 1 ? 's' : ''}`);
    seleccionados.clear();
    renderTabla();
  } catch(e) {
    toast('Error al guardar: ' + e.message, 'error');
  }
  actualizarBtnBlacklist();
}

async function quitarDeBlacklist(key) {
  const entrada = blacklist[key];
  if (!entrada) return;
  const marca = entrada.marca || key;
  try {
    await actualizarBlacklist(bl => { delete bl[key]; }, `admin: desbloquear ${marca}`);
    toast(`${marca} removido de lista negra`);
    renderTabla();
  } catch(e) {
    toast('Error al guardar: ' + e.message, 'error');
  }
}

// ── Filtros ───────────────────────────────────────────────────────────────
function setFiltro(f, btn) {
  filtroActual = f;
  document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  seleccionados.clear();
  document.getElementById('check-all').checked = false;
  actualizarBtnBlacklist();
  renderTabla();
}

// ── Bindings (reemplaza los onclick="" bloqueados por CSP) ─────────────────
document.getElementById('btn-conectar').addEventListener('click', conectar);

// Enter en el input de token también conecta (mejora de UX, no forma parte del fix de CSP)
document.getElementById('token-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') conectar();
});

document.querySelector('.filter-tabs').addEventListener('click', e => {
  const btn = e.target.closest('.filter-tab');
  if (btn) setFiltro(btn.dataset.filtro, btn);
});

document.getElementById('btn-sel-todos').addEventListener('click', seleccionarTodos);
document.getElementById('btn-blacklist').addEventListener('click', agregarSeleccionados);
document.getElementById('btn-reload').addEventListener('click', cargarDatos);
document.getElementById('check-all').addEventListener('change', function () { toggleAll(this); });

document.querySelector('thead').addEventListener('click', e => {
  const th = e.target.closest('th.sortable');
  if (!th) return;
  const col = th.dataset.sort;
  if (sortCol === col) {
    sortDir *= -1;
  } else {
    sortCol = col;
    sortDir = 1;
  }
  renderTabla();
});

document.getElementById('tabla-body').addEventListener('change', e => {
  if (e.target.matches('.row-check')) toggleSel(e.target.dataset.key, e.target);
});

document.getElementById('tabla-body').addEventListener('click', e => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;
  if (btn.dataset.action === 'bloquear')   bloquearUno(btn.dataset.key, btn.dataset.marca);
  if (btn.dataset.action === 'desbloquear') quitarDeBlacklist(btn.dataset.key);
});

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

// Misma heuristica que scripts/etl/blacklist.py::_parece_corrupta. No repara
// nada -- solo evita guardar un bloqueo cuya clave nunca va a poder matchear
// contra un medicamento real (ver commit 8358b29).
function pareceCorrupta(texto) {
  return texto.includes('Ã') || texto.includes('â€')
    || [...texto].some(c => c.charCodeAt(0) >= 0x80 && c.charCodeAt(0) <= 0x9f);
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
  if (!r.ok) {
    const e = new Error(`GitHub ${r.status}: ${path}`);
    e.status = r.status;
    throw e;
  }
  const data = await r.json();
  let base64 = data.content;

  // La Contents API no incluye `content` para archivos > 1MB (blacklist.json
  // ya cruzó ese límite). En ese caso hay que pedirlo aparte con la Git Data
  // API (blobs), que soporta hasta 100MB, usando el mismo sha que ya tenemos.
  if (!base64) {
    const blobR = await fetch(`https://api.github.com/repos/${REPO}/git/blobs/${data.sha}`, {
      headers: { Authorization: `Bearer ${TOKEN}`, Accept: 'application/vnd.github.v3+json' }
    });
    if (!blobR.ok) {
      const e = new Error(`GitHub ${blobR.status} (blob): ${path}`);
      e.status = blobR.status;
      throw e;
    }
    base64 = (await blobR.json()).content;
  }

  // Inversa exacta de btoa(unescape(encodeURIComponent(...))) en ghPut.
  // atob() sola interpreta cada byte UTF-8 como un carácter Latin-1 (mojibake
  // con tildes/ñ). escape()+decodeURIComponent() revierte eso correctamente.
  const content = JSON.parse(decodeURIComponent(escape(atob(base64.replace(/\n/g, '')))));
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

  // blacklist.json (puede no existir aún -- eso sí es un 404 legítimo)
  try {
    const bl = await ghGet(BL_PATH);
    blacklist    = bl.content;
    blacklistSha = bl.sha;
  } catch(e) {
    if (e.status === 404) {
      blacklist    = {};
      blacklistSha = null;
    } else {
      // Cualquier otro fallo (401, 403, rate limit, red) NO se trata como
      // "vacío" -- eso mostraría todo como "no bloqueado" sin avisar,
      // aunque blacklist.json siga íntegro en GitHub. Se corta la carga
      // y se avisa explícitamente en vez de mentir con datos vacíos.
      throw new Error(`No se pudo leer blacklist.json (${e.message}). Los bloqueos existentes NO se perdieron, pero no se pueden mostrar ahora.`);
    }
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
// otra pestaña u otro click en curso) y reintenta ante 409 con backoff,
// porque la Contents API de GitHub puede tardar un instante en propagar
// la última escritura antes de que un GET inmediato la refleje.
async function actualizarBlacklist(mutator, mensaje) {
  const maxIntentos = 4;
  for (let intento = 0; intento < maxIntentos; intento++) {
    if (intento > 0) await new Promise(r => setTimeout(r, 700 * intento));

    let fresco, freshSha;
    try {
      const r = await ghGet(BL_PATH);
      fresco = r.content;
      freshSha = r.sha;
    } catch (e) {
      if (e.status === 404) {
        fresco = {};       // blacklist.json legítimamente no existe aún
        freshSha = null;
      } else {
        // Cualquier otro fallo de lectura: abortar sin escribir. Tratar esto
        // como "vacío" pisaría las entradas existentes con un objeto casi
        // vacío -- perder datos en silencio es peor que fallar visiblemente.
        throw new Error(`No se pudo leer blacklist.json antes de guardar (${e.message}). No se escribió nada, tus bloqueos existentes están a salvo.`);
      }
    }

    mutator(fresco);

    try {
      const result = await ghPut(BL_PATH, fresco, freshSha, mensaje);
      blacklist    = fresco;
      blacklistSha = result.content.sha;
      document.getElementById('stat-blacklist').textContent = Object.keys(blacklist).length;
      return;
    } catch (e) {
      if (e.isShaConflict && intento < maxIntentos - 1) continue;  // reintentar con sha fresco
      throw e;
    }
  }
}

// Serializa todas las escrituras a blacklist.json DENTRO de esta pestaña.
// Sin esto, clickear "bloquear" en dos filas distintas rápido dispara dos
// actualizarBlacklist() en paralelo, cada una con su propio ciclo de
// lectura+escritura, compitiendo entre sí por el mismo archivo -- eso
// aumenta las chances de agotar los reintentos por conflicto de sha.
// (No resuelve conflictos entre pestañas distintas -- para eso siguen
// estando los reintentos con backoff de actualizarBlacklist.)
let colaEscrituraBlacklist = Promise.resolve();
function encolarEscrituraBlacklist(mutator, mensaje) {
  const resultado = colaEscrituraBlacklist.then(
    () => actualizarBlacklist(mutator, mensaje)
  );
  // Si esta escritura falla, no debe trabar las siguientes en la cola.
  colaEscrituraBlacklist = resultado.catch(() => {});
  return resultado;
}

async function bloquearUno(key, marca) {
  const outlier = allOutliers.find(o => makeKey(o) === key);
  if (!outlier) return;
  if (pareceCorrupta(key)) {
    toast(`${marca}: encoding corrupto, no se puede bloquear con confianza (revisar el PDF a mano)`, 'error');
    return;
  }
  try {
    await encolarEscrituraBlacklist(bl => { bl[key] = construirEntrada(outlier); }, `admin: bloquear ${marca}`);
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

  const corruptos = pendientes.filter(o => pareceCorrupta(makeKey(o)));
  const validos   = pendientes.filter(o => !pareceCorrupta(makeKey(o)));

  if (corruptos.length) {
    toast(`${corruptos.length} omitido(s) por encoding corrupto (no se pueden bloquear con confianza)`, 'error');
  }

  if (validos.length) {
    try {
      await encolarEscrituraBlacklist(bl => {
        validos.forEach(o => { bl[makeKey(o)] = construirEntrada(o); });
      }, `admin: bloquear ${validos.length} outliers`);
      toast(`${validos.length} medicamento${validos.length > 1 ? 's' : ''} bloqueado${validos.length > 1 ? 's' : ''}`);
    } catch(e) {
      toast('Error al guardar: ' + e.message, 'error');
    }
  }
  seleccionados.clear();
  renderTabla();
  actualizarBtnBlacklist();
}

async function quitarDeBlacklist(key) {
  const entrada = blacklist[key];
  if (!entrada) return;
  const marca = entrada.marca || key;
  try {
    await encolarEscrituraBlacklist(bl => { delete bl[key]; }, `admin: desbloquear ${marca}`);
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
document.getElementById('auth-form').addEventListener('submit', e => {
  e.preventDefault();  // no recargar la página -- conectar() maneja todo por fetch
  conectar();
});

document.querySelector('.filter-tabs').addEventListener('click', e => {
  const btn = e.target.closest('.filter-tab');
  if (btn) setFiltro(btn.dataset.filtro, btn);
});

document.getElementById('btn-sel-todos').addEventListener('click', seleccionarTodos);
document.getElementById('btn-blacklist').addEventListener('click', agregarSeleccionados);
document.getElementById('btn-reload').addEventListener('click', async () => {
  try {
    await cargarDatos();
  } catch (e) {
    toast(e.message, 'error');
  }
});
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
  if (!btn || btn.disabled) return;
  const textoOriginal = btn.textContent;
  btn.disabled = true;
  btn.textContent = '…';
  const terminar = () => { btn.disabled = false; btn.textContent = textoOriginal; };
  if (btn.dataset.action === 'bloquear') {
    bloquearUno(btn.dataset.key, btn.dataset.marca).finally(terminar);
  } else if (btn.dataset.action === 'desbloquear') {
    quitarDeBlacklist(btn.dataset.key).finally(terminar);
  } else {
    terminar();
  }
});

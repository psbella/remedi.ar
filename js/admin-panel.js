// admin-panel.js — Panel de administración de outliers
// Reescrito 2026-08-14: limpio, modular, sin dependencias

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// CONFIG
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const CONFIG = {
  repo: 'psbella/remediar',
  reportPath: 'data/outlier_report.json',
  blacklistPath: 'data/blacklist.json',
  debug: true,
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// STATE
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

let state = {
  token: '',
  branch: 'main',
  outliers: [],
  blacklist: {},
  blacklistSha: null,
  filter: 'all',
  selected: new Set(),
  sort: { column: null, direction: 1 },
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// LOGGING
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const log = {
  info: (...args) => CONFIG.debug && console.log('[admin]', ...args),
  warn: (...args) => console.warn('[admin]', ...args),
  error: (...args) => console.error('[admin]', ...args),
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// UTILITIES
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function makeKey(item) {
  return [item.droga, item.marca, item.presentacion, item.laboratorio]
    .map(s => (s || '').trim().toLowerCase())
    .join('|');
}

function isCorrupted(text) {
  if (!text || typeof text !== 'string') return false;
  return text.includes('Ã') || text.includes('â€') ||
         [...text].some(c => c.charCodeAt(0) >= 0x80 && c.charCodeAt(0) <= 0x9f);
}

function formatPrice(price) {
  if (!price && price !== 0) return '—';
  return '$' + Number(price).toLocaleString('es-AR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function toast(message, type = 'success') {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.className = `toast ${type}`;
  setTimeout(() => el.className = 'toast hidden', 3000);
}

function setStatus(ok, text) {
  const dot = document.getElementById('status-dot');
  const txt = document.getElementById('status-text');
  dot.className = `dot ${ok ? 'ok' : 'err'}`;
  txt.textContent = text;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// GITHUB API
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function githubGet(path) {
  log.info(`GET ${path}`);
  const url = `https://api.github.com/repos/${CONFIG.repo}/contents/${path}?ref=${state.branch}`;
  const r = await fetch(url, {
    headers: {
      Authorization: `Bearer ${state.token}`,
      Accept: 'application/vnd.github.v3+json',
    },
  });

  if (!r.ok) {
    const err = new Error(`GitHub ${r.status}: ${path}`);
    err.status = r.status;
    throw err;
  }

  const data = await r.json();
  let base64 = data.content;

  // Si archivo > 1MB, usar Blob API
  if (!base64) {
    log.info(`${path} > 1MB, usando Blob API`);
    const blobR = await fetch(
      `https://api.github.com/repos/${CONFIG.repo}/git/blobs/${data.sha}`,
      {
        headers: {
          Authorization: `Bearer ${state.token}`,
          Accept: 'application/vnd.github.v3+json',
        },
      }
    );
    if (!blobR.ok) throw new Error(`GitHub ${blobR.status} (blob): ${path}`);
    base64 = (await blobR.json()).content;
  }

  // Decodificar UTF-8. Dos formatos posibles según cómo se guardó el archivo:
  //   - blacklist.json (escrito por este panel vía githubPut): pasó por
  //     encodeURIComponent()+unescape() antes de btoa(), así que hace falta
  //     decodeURIComponent() para revertirlo.
  //   - outlier_report.json (escrito por el ETL en Python): es UTF-8 plano
  //     en base64, sin ese paso extra — decodeURIComponent() encuentra
  //     bytes que no son secuencias %XX válidas y tira "URI malformed".
  // Se prueba decodeURIComponent() primero y, si falla puntualmente esa
  // llamada, se cae a interpretar el string de atob() como UTF-8 directo
  // (no como Latin-1 vía escape(), que fue el bug original).
  let content;
  const decoded = atob(base64.replace(/\n/g, ''));
  try {
    content = JSON.parse(decodeURIComponent(decoded));
  } catch (e1) {
    try {
      const bytes = Uint8Array.from(decoded, c => c.charCodeAt(0));
      content = JSON.parse(new TextDecoder('utf-8').decode(bytes));
    } catch (e2) {
      log.error(`Error decodificando ${path}:`, e2.message);
      log.error(`base64 length: ${base64.length}`);
      throw new Error(`Fallo decodificando ${path}: ${e2.message}`);
    }
  }

  // Detectar mojibake residual (datos históricos)
  if (Object.values(content).some(v =>
    typeof v === 'string' && (v.includes('Ã') || v.includes('â€'))
  )) {
    log.warn(`Mojibake detectado en ${path}`);
  }

  return { content, sha: data.sha };
}

async function githubPut(path, content, sha, message) {
  log.info(`PUT ${path} (${Object.keys(content).length} keys)`);
  const body = {
    message,
    content: btoa(unescape(encodeURIComponent(JSON.stringify(content, null, 2)))),
    branch: state.branch,
  };
  if (sha) body.sha = sha;

  const r = await fetch(`https://api.github.com/repos/${CONFIG.repo}/contents/${path}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${state.token}`,
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

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// DATA LOADING
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function loadData() {
  log.info('Cargando datos…');
  
  // Outliers
  const { content: report } = await githubGet(CONFIG.reportPath);
  state.outliers = report.outliers || [];
  log.info(`Cargados ${state.outliers.length} outliers`);

  // Blacklist (puede no existir)
  try {
    const bl = await githubGet(CONFIG.blacklistPath);
    state.blacklist = bl.content;
    state.blacklistSha = bl.sha;
    log.info(`Blacklist: ${Object.keys(state.blacklist).length} entries`);
  } catch (e) {
    if (e.status === 404) {
      log.info('blacklist.json no existe (será creado)');
      state.blacklist = {};
      state.blacklistSha = null;
    } else {
      throw e;
    }
  }

  // Actualizar stats
  updateStats(report);
  
  // Clear selection
  state.selected.clear();
  
  // Renderizar
  render();
}

function updateStats(report) {
  document.getElementById('stat-total').textContent = state.outliers.length;
  
  const critical = state.outliers.filter(o => o.precio_outlier_tipo === 'bajo_critico').length;
  document.getElementById('stat-critical').textContent = critical;
  
  document.getElementById('stat-blocked').textContent = Object.keys(state.blacklist).length;
  
  const timestamp = (report.timestamp || '').slice(0, 16).replace('T', ' ');
  document.getElementById('stat-updated').textContent = timestamp || '—';
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// FILTERING & SORTING
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function getFilteredOutliers() {
  let list = [...state.outliers];
  
  switch (state.filter) {
    case 'critical':
      return list.filter(o => o.precio_outlier_tipo === 'bajo_critico');
    case 'suspicious':
      return list.filter(o => 
        ['bajo_relativo', 'bajo_iqr', 'bajo_absoluto'].includes(o.precio_outlier_tipo)
      );
    case 'blocked':
      return list.filter(o => makeKey(o) in state.blacklist);
    default:
      return list;
  }
}

function sortList(list) {
  if (!state.sort.column) return list;
  
  return [...list].sort((a, b) => {
    let va = state.sort.column === 'ratio'
      ? (a.precio && a.mediana_droga ? a.precio / a.mediana_droga : null)
      : a[state.sort.column];
    let vb = state.sort.column === 'ratio'
      ? (b.precio && b.mediana_droga ? b.precio / b.mediana_droga : null)
      : b[state.sort.column];
    
    if (va == null && vb == null) return 0;
    if (va == null) return 1;
    if (vb == null) return -1;
    
    if (typeof va === 'number' && typeof vb === 'number') {
      return (va - vb) * state.sort.direction;
    }
    
    return String(va).localeCompare(String(vb), 'es', { sensitivity: 'base' }) * state.sort.direction;
  });
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// RENDERING
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function render() {
  const list = sortList(getFilteredOutliers());
  renderToolbarInfo(list);
  renderSortArrows();
  renderTable(list);
  updateBlockBtn();
}

function renderToolbarInfo(list) {
  const info = document.getElementById('toolbar-info');
  info.textContent = `${list.length} registros · filtro: ${state.filter}`;
}

function renderSortArrows() {
  document.querySelectorAll('th.sortable').forEach(th => {
    const arrow = th.querySelector('.arrow');
    if (th.dataset.sort === state.sort.column) {
      th.classList.add('sorted');
      arrow.textContent = state.sort.direction === 1 ? '▲' : '▼';
    } else {
      th.classList.remove('sorted');
      arrow.textContent = '';
    }
  });
}

function renderTable(list) {
  const tbody = document.getElementById('table-body');
  
  if (!list.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="empty-state">Sin registros</td></tr>';
    return;
  }
  
  tbody.innerHTML = list.map(o => {
    const key = makeKey(o);
    const isBlocked = key in state.blacklist;
    const isSelected = state.selected.has(key);
    const ratio = o.precio && o.mediana_droga
      ? (o.precio / o.mediana_droga * 100).toFixed(1) + '%'
      : '—';
    const ratioCls = !o.precio || !o.mediana_droga ? ''
      : o.precio / o.mediana_droga < 0.10 ? 'critical' : 'suspicious';
    
    const typeClass = o.precio_outlier_tipo === 'bajo_critico' ? 'critical' : 'suspicious';
    
    let rowClass = '';
    if (isBlocked) rowClass = 'blocked';
    else if (o.precio_outlier_tipo === 'bajo_critico') rowClass = 'critical';
    
    return `
      <tr class="${rowClass}" data-key="${key}">
        <td class="col-check">
          <input type="checkbox" class="row-check" data-key="${key}" 
            ${isSelected ? 'checked' : ''} ${isBlocked ? 'disabled' : ''}>
        </td>
        <td class="col-med">
          <div class="med-info">
            <div class="med-name">${o.marca || '—'}</div>
            <div class="med-brand">${o.droga || '—'}</div>
            <div class="med-lab">${o.laboratorio || '—'}</div>
          </div>
        </td>
        <td class="col-pres">${o.presentacion || '—'}</td>
        <td class="col-precio">${formatPrice(o.precio)}</td>
        <td class="col-mediana">${formatPrice(o.mediana_droga)}</td>
        <td class="col-ratio"><span class="${ratioCls}">${ratio}</span></td>
        <td class="col-tipo">
          <span class="tipo-badge ${typeClass}">${o.precio_outlier_tipo || '—'}</span>
        </td>
        <td class="col-action">
          ${isBlocked
            ? `<button class="btn btn-sm" data-action="unblock" data-key="${key}">🔓</button>`
            : `<button class="btn btn-sm btn-danger" data-action="block" data-key="${key}">⛔</button>`
          }
        </td>
      </tr>
    `;
  }).join('');
}

function updateBlockBtn() {
  const btn = document.getElementById('btn-block');
  btn.disabled = state.selected.size === 0;
  btn.textContent = state.selected.size > 0
    ? `⛔ Bloquear ${state.selected.size}`
    : '⛔ Bloquear seleccionados';
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// BLACKLIST OPERATIONS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

let writeQueue = Promise.resolve();

async function updateBlacklist(mutator, message) {
  const maxRetries = 4;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    if (attempt > 0) await new Promise(r => setTimeout(r, 700 * attempt));
    
    // Leer versión remota más reciente
    let fresh, freshSha;
    try {
      const r = await githubGet(CONFIG.blacklistPath);
      fresh = r.content;
      freshSha = r.sha;
    } catch (e) {
      if (e.status === 404) {
        fresh = {};
        freshSha = null;
      } else {
        throw new Error(`No se pudo leer blacklist: ${e.message}`);
      }
    }
    
    // Aplicar mutación
    mutator(fresh);
    
    // Intentar escribir
    try {
      const result = await githubPut(CONFIG.blacklistPath, fresh, freshSha, message);
      state.blacklist = fresh;
      state.blacklistSha = result.content.sha;
      
      // Actualizar stats
      document.getElementById('stat-blocked').textContent = Object.keys(state.blacklist).length;
      return;
    } catch (e) {
      if (e.isShaConflict && attempt < maxRetries - 1) {
        log.warn(`SHA conflict, reintentando (${attempt + 1}/${maxRetries})`);
        continue;
      }
      throw e;
    }
  }
}

function enqueueWrite(mutator, message) {
  const result = writeQueue.then(() => updateBlacklist(mutator, message));
  writeQueue = result.catch(() => {});
  return result;
}

async function blockOne(key, marca) {
  const o = state.outliers.find(x => makeKey(x) === key);
  if (!o) return;
  if (isCorrupted(key)) {
    toast(`${marca}: encoding corrupto, revisar a mano`, 'error');
    return;
  }
  
  try {
    await enqueueWrite(bl => {
      bl[key] = {
        droga: o.droga,
        marca: o.marca,
        presentacion: o.presentacion,
        laboratorio: o.laboratorio,
        precio_detectado: o.precio,
        tipo: o.precio_outlier_tipo,
        motivo: (o.razones || []).join(' | '),
        bloqueado_en: new Date().toISOString().slice(0, 16),
      };
    }, `admin: bloquear ${marca}`);
    
    toast(`${marca} bloqueado`);
    render();
  } catch (e) {
    toast(`Error: ${e.message}`, 'error');
    log.error(e);
  }
}

async function blockSelected() {
  if (!state.selected.size) return;
  
  const btn = document.getElementById('btn-block');
  btn.disabled = true;
  btn.textContent = 'guardando…';
  
  const pending = [...state.selected]
    .map(key => state.outliers.find(o => makeKey(o) === key))
    .filter(Boolean);
  
  const corrupted = pending.filter(o => isCorrupted(makeKey(o)));
  const valid = pending.filter(o => !isCorrupted(makeKey(o)));
  
  if (corrupted.length) {
    toast(`${corrupted.length} omitido(s) por encoding corrupto`, 'error');
  }
  
  if (valid.length) {
    try {
      await enqueueWrite(bl => {
        valid.forEach(o => {
          bl[makeKey(o)] = {
            droga: o.droga,
            marca: o.marca,
            presentacion: o.presentacion,
            laboratorio: o.laboratorio,
            precio_detectado: o.precio,
            tipo: o.precio_outlier_tipo,
            motivo: (o.razones || []).join(' | '),
            bloqueado_en: new Date().toISOString().slice(0, 16),
          };
        });
      }, `admin: bloquear ${valid.length}`);
      
      toast(`${valid.length} bloqueado(s)`);
    } catch (e) {
      toast(`Error: ${e.message}`, 'error');
      log.error(e);
    }
  }
  
  state.selected.clear();
  render();
}

async function unblockOne(key) {
  const entry = state.blacklist[key];
  if (!entry) return;
  
  const marca = entry.marca || key;
  try {
    await enqueueWrite(bl => { delete bl[key]; }, `admin: desbloquear ${marca}`);
    toast(`${marca} desbloqueado`);
    render();
  } catch (e) {
    toast(`Error: ${e.message}`, 'error');
    log.error(e);
  }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// EVENT HANDLERS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

document.getElementById('form-auth').addEventListener('submit', async e => {
  e.preventDefault();
  
  state.token = document.getElementById('input-token').value.trim();
  state.branch = document.getElementById('input-branch').value.trim() || 'main';
  
  if (!state.token) {
    toast('Token requerido', 'error');
    return;
  }
  
  setStatus(false, 'conectando…');
  try {
    log.info(`Conectando a ${CONFIG.repo}/${state.branch}`);
    await loadData();
    
    document.getElementById('screen-auth').classList.remove('active');
    document.getElementById('screen-main').classList.add('active');
    
    setStatus(true, 'conectado');
    log.info('✅ Conectado');
  } catch (e) {
    log.error(e);
    setStatus(false, e.message);
    toast(e.message, 'error');
  }
});

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.filter = btn.dataset.filter;
    state.selected.clear();
    document.getElementById('check-all').checked = false;
    render();
  });
});

document.getElementById('check-all').addEventListener('change', e => {
  const list = getFilteredOutliers();
  list.forEach(o => {
    const key = makeKey(o);
    if (key in state.blacklist) return;
    e.target.checked ? state.selected.add(key) : state.selected.delete(key);
  });
  render();
});

document.getElementById('btn-select-all').addEventListener('click', () => {
  document.getElementById('check-all').checked = true;
  document.getElementById('check-all').dispatchEvent(new Event('change'));
});

document.getElementById('btn-block').addEventListener('click', blockSelected);

document.getElementById('btn-refresh').addEventListener('click', async () => {
  try {
    await loadData();
    toast('Datos recargados');
  } catch (e) {
    toast(e.message, 'error');
    log.error(e);
  }
});

document.querySelector('thead').addEventListener('click', e => {
  const th = e.target.closest('th.sortable');
  if (!th) return;
  
  const col = th.dataset.sort;
  if (state.sort.column === col) {
    state.sort.direction *= -1;
  } else {
    state.sort.column = col;
    state.sort.direction = 1;
  }
  render();
});

document.getElementById('table-body').addEventListener('change', e => {
  if (e.target.matches('.row-check')) {
    const key = e.target.dataset.key;
    e.target.checked ? state.selected.add(key) : state.selected.delete(key);
    updateBlockBtn();
  }
});

document.getElementById('table-body').addEventListener('click', e => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;
  
  const key = btn.dataset.key;
  const action = btn.dataset.action;
  const origText = btn.textContent;
  
  btn.disabled = true;
  btn.textContent = '…';
  
  const done = () => {
    btn.disabled = false;
    btn.textContent = origText;
  };
  
  if (action === 'block') {
    const o = state.outliers.find(x => makeKey(x) === key);
    blockOne(key, o?.marca || key).finally(done);
  } else if (action === 'unblock') {
    unblockOne(key).finally(done);
  }
});

log.info('✅ admin-panel.js cargado');
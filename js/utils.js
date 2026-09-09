// js/utils.js — Utilidades y normalización

/**
 * Normaliza texto para comparación/búsqueda: minúsculas y sin acentos.
 */
export function normalizar(texto) {
    if (!texto) return '';
    return texto.toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .trim();
}

/**
 * Formatea un precio como moneda argentina (es-AR, ARS). Devuelve 'N/D'
 * si el valor es nulo o no numérico.
 */
export function formatearPrecio(precio) {
    if (precio == null || isNaN(precio)) return 'N/D';
    return precio.toLocaleString('es-AR', {
        style: 'currency', currency: 'ARS',
        minimumFractionDigits: 2, maximumFractionDigits: 2
    });
}

/**
 * Escapa caracteres especiales de HTML para insertar texto de forma
 * segura en el DOM (previene inyección de markup).
 */
export function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
		.replace(/'/g, '&#039;');
}

// ── Normalización de laboratorios truncados ───────────────────────────
const LAB_CORRECCIONES = {
    "abbvie (ex alle": "Abbvie / Recalcine",
    "alef medical ar": "Alef Medical Argentina",
    "bausch & lomb a": "Bausch & Lomb Argentina",
    "baxter argentin": "Baxter Argentina",
    "biopas argentin": "Biopas Argentina",
    "boehringer inge": "Boehringer Ingelheim",
    "bristol": "Bristol-Myers Squibb",
    "celnova argenti": "Celnova Argentina",
    "johnson & johns": "Johnson & Johnson",
    "lab internacion": "Laboratorio Internacional",
    "laboratorio gra": "Laboratorio Grafo",
    "laboratorio mer": "Laboratorio Merck",
    "laboratorio val": "Laboratorio Valent",
    "laboratorios be": "Laboratorios Beta",
    "laboratorios fe": "Laboratorios Ferrer",
    "laboratorios ta": "Laboratorios Tuteur",
    "lancaster pharm": "Lancaster Pharma",
    "microsules arg.": "Microsules Argentina",
    "msd argentina s": "MSD Argentina",
    "opella healthca": "Opella Healthcare",
    "organon arg.": "Organon Argentina",
    "pharmalep s.a": "Pharmalep S.A.",
    "pierre fabre me": "Pierre Fabre Médicament",
    "pierre fabre on": "Pierre Fabre Oncologie",
    "procter & gambl": "Procter & Gamble",
    "reckitt benckis": "Reckitt Benckiser",
    "sanofi pasteur": "Sanofi Pasteur Argentina",
    "takeda argentin": "Takeda Argentina",
    "vannier - grune": "Vannier - Grünenthal"
};

/**
 * Reemplaza nombres de laboratorio truncados por el PDF de origen (ej.
 * "abbvie (ex alle" -> "Abbvie / Recalcine") usando el mapa de correcciones
 * conocidas. Si no hay corrección registrada, devuelve el valor original.
 */
export function normalizarLaboratorio(lab) {
    if (!lab) return "Desconocido";
    const clave = lab.toLowerCase().trim().replace(/\.$/, '');
    return LAB_CORRECCIONES[clave] || lab;
}

/**
 * Detecta laboratorios corruptos por mal parseo (precios o dosis que
 * terminaron en el campo laboratorio), vía blacklist de valores conocidos
 * más heurísticas de dígitos/unidades.
 */
export function esLaboratorioCorrupto(valor) {
    if (!valor) return true;
    const limpio = valor.toString().trim();
    const blacklist = [
        "20/134mg compx30+capsx30Teva argentina",
        "200/10mg comp.x60(30+30) Craveri",
        "35.486,17", "37.532,00", "41.931,16", "42.601,18", "9.938,36"
    ];
    if (blacklist.includes(limpio)) return true;
    if (/^\d/.test(limpio) && /mg|ml|g|ui|comp|tableta|capsula/i.test(limpio)) return true;
    const numeros = (limpio.match(/\d+/g) || []).length;
    if (numeros >= 2) return true;
    return false;
}

/**
 * Extrae los valores únicos de presentación y laboratorio (normalizado, sin
 * corruptos) presentes en la lista, para poblar los dropdowns de filtro.
 */
export function extraerFiltros(medicamentos) {
    const pres = new Set();
    const labs = new Set();
    for (const m of medicamentos) {
        if (m.presentacion) pres.add(m.presentacion);
        if (m.laboratorio && m.laboratorio !== "Desconocido" && !esLaboratorioCorrupto(m.laboratorio)) {
            labs.add(normalizarLaboratorio(m.laboratorio));
        }
    }
    return {
        presentaciones: [...pres].sort(),
        laboratorios: [...labs].sort()
    };
}

// ── Parseo de presentación en componentes ─────────────────────────────
const FORMAS_MAP = {
    // Comprimidos
    'comp':              'Comprimidos',
    'comp.rec':          'Comprimidos recubiertos',
    'comp. rec':         'Comprimidos recubiertos',
    'comp.ran':          'Comprimidos ranurados',
    'comp.rec.ran':      'Comprimidos recubiertos ranurados',
    'comp.birran':       'Comprimidos biranurados',
    'comp.mast':         'Comprimidos masticables',
    'comp.subl':         'Comprimidos sublinguales',
    'comp.efer':         'Comprimidos efervescentes',
    'comp.dispers':      'Comprimidos dispersables',
    'comp.lib.prol':     'Comprimidos liberación prolongada',
    'comp.rec.ap':       'Comprimidos recubiertos acción prolongada',
    'comp.disper':       'Comprimidos dispersables',
    'pcomp':             'Comprimidos',
    'pcomp.rec':         'Comprimidos recubiertos',
    'grag':              'Grageas',
    // Cápsulas
    'caps':              'Cápsulas',
    'cáps':              'Cápsulas',
    'caps.blandas':      'Cápsulas blandas',
    'cáps.bl':           'Cápsulas blandas',
    'caps.lib.prol':     'Cápsulas liberación prolongada',
    // Inyectables
    'a':                 'Ampolla',
    'f.a':               'Frasco ampolla',
    'iny':               'Inyectable',
    'iny.a':             'Ampolla inyectable',
    'iny.f.a':           'Frasco ampolla inyectable',
    'iny.liof.f.a':      'Frasco ampolla liofilizado inyectable',
    'liof.f.a':          'Frasco ampolla liofilizado',
    'f.a.liof':          'Frasco ampolla liofilizado',
    'vial':              'Vial',
    'iny.vial':          'Vial inyectable',
    'jga.prell':         'Jeringa prellenada',
    'lap.prell':         'Lapicera prellenada',
    // Tópicos
    'cr':                'Crema',
    'ung':               'Ungüento',
    'gel':               'Gel',
    'loc':               'Loción',
    'pomo':              'Pomo',
    'sol.oft':           'Solución oftálmica',
    'gts.oft':           'Gotas oftálmicas',
    'gts.óticas':        'Gotas óticas',
    'colirio':           'Colirio',
    'pda':               'Parche',
    // Orales líquidos
    'jbe':               'Jarabe',
    'sol':               'Solución',
    'sol.oral':          'Solución oral',
    'susp':              'Suspensión',
    'susp.oral':         'Suspensión oral',
    'susp.oft':          'Suspensión oftálmica',
    'gts':               'Gotas',
    'liq':               'Líquido',
    // Aerosoles / sprays
    'aer':               'Aerosol',
    'spray':             'Spray',
    'spray nasal':       'Spray nasal',
    // Otros sólidos
    'sob':               'Sobres',
    'sobres':            'Sobres',
    'ov':                'Óvulos',
    'env':               'Envase',
    'pvo':               'Polvo',
    'emuls':             'Emulsión',
    'fco':               'Frasco',
    'fco.a':             'Frasco ampolla',
    'fco.gotero':        'Frasco gotero',
    'bolsa':             'Bolsa',
    'laca':              'Laca',
    'espuma':            'Espuma',
    'espuma rectal':     'Espuma rectal',
    'jalea':             'Jalea',
    'pote':              'Pote',
    'gtas':              'Gotas',
    'gotas':             'Gotas',
    'past':              'Pastillas',
    'pastillas':         'Pastillas',
    'colut':             'Colutorio',
    'soluc':             'Solución',
    'parches':           'Parches',
    'caramelos':         'Caramelos',
    'pasta dérm':        'Pasta dérmica',
    'unidosis':          'Unidosis',
    'toallitas':         'Toallitas',
    'sistemas':          'Sistemas',
    'estuche':           'Estuche',
    'sachets':           'Sobres',
    'implante':          'Implante',
    'pomada':            'Pomada',
    'polvo':             'Polvo',
    'talquera':          'Talquera',
    'champu':            'Champú',
    'crema':             'Crema',
};

/**
 * Descompone una presentación en sus componentes: dosis, forma farmacéutica
 * y cantidad (ej. "500mg comp.rec.x30" -> dosis "500mg", forma
 * "Comprimidos recubiertos", cantidad "30"). Devuelve null si no matchea
 * ninguno de los tres.
 */
export function parsearPresentacion(texto) {
    if (!texto) return null;
    const t = texto.trim().toLowerCase();

    // Extraer dosis: "300 mg", "40mg/0.4ml", "0.1%", "15% ", etc.
    const reDosis = /^([\d.,/]+\s*(?:mg|mcg|g(?!\w)|ml|ui|%|u(?!\w))(?:\/[\d.,]*\s*(?:mg|mcg|g|ml|ui|%))?)\s*/i;
    const mDosis = t.match(reDosis);
    const dosis = mDosis ? mDosis[1].trim() : null;
    const resto = mDosis ? t.slice(mDosis[0].length) : t;

    // Extraer cantidad: "x 30", "x 100 ml", "x 1 x 2ml"
    const reCant = /\.?x\s*([\d.,]+(?:\s*x\s*[\d.,]+(?:\s*(?:ml|g|l))?)?(?:\s*(?:ml|g|l))?)\s*$/i;
    const mCant = resto.match(reCant);
    const cantidad = mCant ? mCant[1].trim() : null;
    const formaRaw = mCant ? resto.slice(0, resto.length - mCant[0].length).trim() : resto.trim();

    // Normalizar forma: quitar puntos finales, buscar en mapa
    const formaKey = formaRaw.replace(/\.+$/, '').toLowerCase();
    const forma = FORMAS_MAP[formaKey] || (formaRaw ? formaRaw.charAt(0).toUpperCase() + formaRaw.slice(1) : null);

    if (!dosis && !forma && !cantidad) return null;
    return { dosis, forma, cantidad };
}

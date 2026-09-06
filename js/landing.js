// js/landing.js — Comportamiento compartido por las landing pages de drogas
// (botón volver arriba, aviso de scroll en la tabla, buscador del footer,
// versión dinámica). Antes vivía inline en cada una de las 100 páginas
// generadas por scripts/generar_landings.py; se movió a un archivo externo
// para que quede cubierto por script-src 'self' en la CSP y no dependa de
// mantener un hash SHA-256 sincronizado cada vez que se edita.
(function() {
    const btn = document.getElementById('btnTop');
    if (!btn) return;
    window.addEventListener('scroll', function() {
        btn.classList.toggle('visible', window.scrollY > 300);
    }, { passive: true });
    btn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}());
(function() {
    const wrapper = document.getElementById('tablaWrapper');
    const scroll  = document.getElementById('tablaScroll');
    if (!wrapper || !scroll) return;
    function check() {
        wrapper.classList.toggle('no-overflow', scroll.scrollWidth <= scroll.clientWidth);
    }
    check();
    window.addEventListener('resize', check);
}());
(function() {
    const inp = document.getElementById('buscador');
    const btn = document.getElementById('btnBuscar');
    function ir() {
        const q = inp ? inp.value.trim() : '';
        if (q.length >= 2) window.location.href = 'index.html?q=' + encodeURIComponent(q);
    }
    if (btn) btn.addEventListener('click', ir);
    if (inp) inp.addEventListener('keydown', function(e) { if (e.key === 'Enter') ir(); });
}());
(function() {
    const el = document.getElementById('footer-version');
    if (!el) return;
    fetch('package.json', { cache: 'no-cache' })
        .then(function(res) { if (!res.ok) throw new Error('no ok'); return res.json(); })
        .then(function(pkg) { el.textContent = 'v' + pkg.version; })
        .catch(function() { el.remove(); });
}());

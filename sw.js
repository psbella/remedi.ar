// sw.js — Service Worker remedi.ar
const CACHE_NAME   = 'remediar-v14';
const CACHE_STATIC = [
    '/',
    '/index.html',
    '/about.html',
    '/css/style.css',
    '/manifest.json',
    '/img/favicon.svg',
    '/img/logo_banner.svg',
    '/img/icon-192.png',
    '/img/icon-512.png',
    '/img/og-image.png',
    '/js/main.js',
    '/js/about.js',
    '/js/store.js',
    '/js/dataLoader.js',
    '/js/filters.js',
    '/js/searchEngine.js',
    '/js/uiRenderer.js',
    '/js/infoAdicional.js',
    '/js/utils.js',
    '/js/landing.js',
];

// Instalación: cachear assets estáticos
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(CACHE_STATIC))
            .then(() => self.skipWaiting())
    );
});

// Activación: limpiar caches viejas
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

// Fetch: estrategia según tipo de recurso
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // medicamentos.json → network-first (datos frescos siempre)
    if (url.pathname.includes('medicamentos.json')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Assets estáticos → cache-first
    event.respondWith(
        caches.match(event.request)
            .then(cached => cached || fetch(event.request))
    );
});

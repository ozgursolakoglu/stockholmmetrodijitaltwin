// Stockholm Metrosu canlı dijital gölge - Cloudflare Worker aracı sunucusu
// SL Transport API'ye gelen istekleri iletir, CORS izni ekler ve yanıtları önbelleğe alır.
// Kurulum: Cloudflare hesabı > Workers & Pages > Create > Worker > bu kodu yapıştırın > Deploy.
// Çıkan adresi (ör. https://sl-metro.kullaniciadi.workers.dev) sayfadaki "Veri kaynağı ayarı" alanına yazın.

const UPSTREAM = 'https://transport.integration.sl.se';
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Accept, Content-Type',
};
const ALLOWED = /^\/v1\/(sites|lines|sites\/\d+\/departures|stop-points|transport-authorities)$/;

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') return new Response(null, { headers: CORS });
    if (request.method !== 'GET') return new Response('Yalnızca GET', { status: 405, headers: CORS });

    const url = new URL(request.url);
    if (!ALLOWED.test(url.pathname)) return new Response('Bu adres desteklenmiyor', { status: 404, headers: CORS });

    const target = UPSTREAM + url.pathname + url.search;
    const ttl = url.pathname.endsWith('/departures') ? 20 : 86400;
    const cache = caches.default;
    const key = new Request(target);

    let res = await cache.match(key);
    if (!res) {
      const up = await fetch(target, { headers: { Accept: 'application/json' } });
      res = new Response(up.body, up);
      res.headers.set('Cache-Control', `public, max-age=${ttl}`);
      if (up.ok) ctx.waitUntil(cache.put(key, res.clone()));
    }
    res = new Response(res.body, res);
    for (const [k, v] of Object.entries(CORS)) res.headers.set(k, v);
    return res;
  },
};

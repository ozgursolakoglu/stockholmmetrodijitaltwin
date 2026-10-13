#!/usr/bin/env python3
"""
Stockholm Metrosu canlı dijital gölge - yerel sunucu ve aracı (proxy)

Kullanım:
    python3 sl_proxy.py          (Windows'ta: python sl_proxy.py)
Ardından tarayıcıda açın:  http://localhost:8000

- index.html dosyasını sunar.
- /v1/... isteklerini SL Transport API'ye (https://transport.integration.sl.se) iletir.
- Yanıtları önbelleğe alır: istasyon listesi 1 gün, kalkışlar 20 saniye.
  Böylece sınıftaki 30 öğrenci aynı sunucuyu kullansa bile SL'ye giden istek sayısı artmaz.
Ek kurulum gerektirmez; yalnızca Python 3 yeterlidir.
"""
import json, os, re, socket, ssl, sys, threading, time, urllib.request, urllib.error, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

UPSTREAM = "https://transport.integration.sl.se"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", "8000"))
ALLOWED = re.compile(r"^/v1/(sites|lines(\?transport_authority_id=\d+)?|sites/\d+/departures|stop-points|transport-authorities)(\?.*)?$")
CACHE, LOCK = {}, threading.Lock()

def ttl_for(path):
    return 20 if "/departures" in path else 86400

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=os.path.dirname(os.path.abspath(__file__)), **kw)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/v1/"):
            return self.proxy()
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_GET()

    def proxy(self):
        if not ALLOWED.match(self.path):
            self.send_error(404, "Bu adres desteklenmiyor")
            return
        now = time.time()
        with LOCK:
            hit = CACHE.get(self.path)
        if hit and now - hit[0] < ttl_for(self.path):
            body, status = hit[1], 200
        else:
            try:
                req = urllib.request.Request(UPSTREAM + self.path, headers={"Accept": "application/json", "User-Agent": "okul-dijital-ikiz/1.0"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    body, status = r.read(), r.status
                with LOCK:
                    CACHE[self.path] = (now, body)
            except urllib.error.HTTPError as e:
                body, status = json.dumps({"error": "SL HTTP %d" % e.code}).encode(), e.code
            except Exception as e:
                if hit:
                    body, status = hit[1], 200          # bağlantı koparsa eski veriyi ver
                else:
                    body, status = json.dumps({"error": str(e)}).encode(), 502
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        line = fmt % args
        if "/departures" not in line:
            sys.stderr.write(line + "\n")

def check_sl():
    print("SL sunucusu deneniyor...", end=" ", flush=True)
    try:
        req = urllib.request.Request(UPSTREAM + "/v1/sites/9001/departures", headers={"Accept": "application/json", "User-Agent": "okul-dijital-ikiz/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read()
        print("TAMAM, canlı veri alınabiliyor.")
    except Exception as e:
        print("BAŞARISIZ.")
        print("  Hata:", e)
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            print("  Mac'te çözüm: Uygulamalar > Python 3.x klasöründeki 'Install Certificates.command' dosyasına çift tıklayın.")
        else:
            print("  İnternet bağlantısını veya okul ağının güvenlik duvarını kontrol edin. Sayfa yine açılır ama simüle veri gösterir.")

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(here, "index.html")):
        print("HATA: index.html bu dosyayla aynı klasörde değil:", here)
        sys.exit(1)
    server = None
    for port in range(PORT, PORT + 10):
        try:
            server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
            break
        except OSError:
            print("Port %d kullanımda, %d deneniyor..." % (port, port + 1))
    if not server:
        print("HATA: Boş port bulunamadı.")
        sys.exit(1)
    url = "http://127.0.0.1:%d" % port
    check_sl()
    print()
    print("Sunucu çalışıyor:  %s   (bu pencereyi KAPATMAYIN; durdurmak için Ctrl+C)" % url)
    try:
        ip = socket.gethostbyname(socket.gethostname())
        print("Aynı ağdaki öğrenciler için:  http://%s:%d" % (ip, port))
    except Exception:
        pass
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu durduruldu.")

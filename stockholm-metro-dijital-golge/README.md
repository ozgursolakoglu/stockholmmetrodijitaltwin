# Stockholm Metrosu – Canlı Dijital Gölge

Stockholm metrosunun (Tunnelbana) gerçek zamanlı verilerle çalışan şematik haritası. Yapay zekâ ve dijital ikiz derslerinde kullanılmak üzere hazırlanmıştır.

- 7 hat (10, 11, 13, 14, 17, 18, 19) ve yaklaşık 100 istasyon
- Trenlerin tahmini anlık konumu ve gecikmeleri
- İstasyona dokununca o istasyondan kalkacak trenler
- "Gerçek konumlar" görünümü: şematik harita ile gerçek coğrafya arasında geçiş
- Bağlantı yoksa otomatik simüle veri (demo) modu

Veri kaynağı: [SL Transport API](https://www.trafiklab.se/api/other-apis/sl/transport/) (API anahtarı gerektirmez). Verilerin kullanımı için SL/Trafiklab lisans koşullarına bakın.

> Trenlerin konumu GPS değildir; her istasyonun "sonraki tren X dakika sonra" bilgisinden hesaplanan bir tahmindir. Sistem trenleri yalnızca izler, yönetmez: bu yüzden tam bir dijital ikiz değil, bir **dijital gölgedir**.

## Dosyalar

| Dosya | Görevi |
|---|---|
| `index.html` | Harita ve arayüz |
| `config.js` | Veri kaynağı adresi (isteğe bağlı) |
| `sl_proxy.py` | Yerel sunucu ve aracı; sınıfta tek bilgisayardan çalıştırmak için |
| `cloudflare-worker.js` | İnternette çalışan aracı sunucu; GitHub Pages ile birlikte kullanmak için |

## 1. GitHub Pages ile yayınlama

1. Repoda **Settings > Pages** bölümüne gidin.
2. *Source* olarak **Deploy from a branch**, dal olarak **main**, klasör olarak **/(root)** seçip kaydedin.
3. Birkaç dakika içinde sayfa `https://KULLANICI-ADI.github.io/REPO-ADI/` adresinde yayına girer.

GitHub Pages yalnızca statik dosya sunar, Python sunucusunu çalıştıramaz. Sayfa önce SL'ye doğrudan bağlanmayı dener. Sağ üstte "Simüle veri" görürseniz tarayıcı doğrudan bağlantıya izin vermiyor demektir; bu durumda 2. adımdaki aracı sunucuyu kurun.

## 2. Cloudflare Worker (GitHub Pages için aracı sunucu)

1. [Cloudflare](https://dash.cloudflare.com) hesabı açın (ücretsiz).
2. **Workers & Pages > Create > Worker** adımlarını izleyin, `cloudflare-worker.js` içeriğini yapıştırıp **Deploy**'a basın.
3. Size verilen `https://....workers.dev` adresini kopyalayın.
4. Bu repoda `config.js` dosyasını açın, kalem simgesiyle düzenleyin ve adresi yazın:
   ```js
   window.SL_API_BASE = "https://sl-metro.kullaniciadi.workers.dev";
   ```
5. Değişikliği kaydedin (Commit). Birkaç dakika sonra GitHub Pages sayfası canlı veriyle açılır.

Worker yanıtları 20 saniye önbellekte tuttuğu için sayfayı aynı anda açan öğrenci sayısı SL'ye giden istekleri artırmaz.

Alternatif olarak adres bağlantıya da eklenebilir: `https://KULLANICI-ADI.github.io/REPO-ADI/?api=https://sl-metro.kullaniciadi.workers.dev`

## 3. Sınıfta yerel olarak çalıştırma

Python 3 yeterlidir, başka kurulum gerekmez.

```bash
python sl_proxy.py        # Windows'ta gerekirse: py sl_proxy.py
python3 sl_proxy.py       # Mac / Linux
```

Tarayıcı kendiliğinden `http://127.0.0.1:8000` adresini açar. Aynı ağdaki öğrenciler, pencerede yazan IP adresiyle bağlanabilir. Port doluysa sunucu sıradaki portu dener; isterseniz port numarası verebilirsiniz: `python sl_proxy.py 8080`.

Sorun giderme:
- **Mac'te `CERTIFICATE_VERIFY_FAILED`**: Uygulamalar > Python 3.x klasöründeki *Install Certificates.command* dosyasını çalıştırın.
- **Sayfa açılıyor ama simüle veri görünüyor**: Okul ağı dış bağlantıları engelliyor olabilir. Sunucu açılışta SL bağlantısını test eder ve sonucu pencereye yazar.

## Derste kullanım önerileri

- Sarı yanan istasyon o an sorgulanan istasyondur: veri akışını gözle göstermek için kullanın.
- Kırmızı çerçeveli trenler 2 dakika veya daha fazla gecikmelidir.
- "Gerçek konumlar" düğmesiyle modelin gerçeği nasıl sadeleştirdiğini tartışın.
- Dijital model, dijital gölge ve dijital ikiz ayrımını bu örnek üzerinden anlatın.

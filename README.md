## Scripts

Kendi kullandığım fish fonksiyonları ve küçük araçlar (CachyOS / Arch + KDE).

## Kurulum

```fish
git clone https://github.com/thebanri/scripts.git ~/scripts
```

`~/.config/fish/config.fish` dosyasına şunu ekleyin, fish her `.fish` dosyasını komut olarak tanır:

```fish
set -p fish_function_path ~/scripts
```

## Komutlar

| Komut | Ne yapar |
|---|---|
| `last-pkgs [n]` | pacman log'undan son `n` işlemde (varsayılan 3) kurulan/güncellenen paketleri renkli listeler |
| `last-pkgs -d` | Sadece bugün kurulan/güncellenen paketler |
| `cache` | İndirme yarım kalan pacman dosyalarını siler ve `yay -Scc` ile paket önbelleğini temizler |
| `gitadd` | `git add .`, [opencommit](https://github.com/di-sukharev/opencommit) (`oco`) ile commit mesajı yazar ve pushlar |
| `open [yol]` | Dosya/klasörü varsayılan uygulamayla açar, yol verilmezse bulunulan klasörü. Terminal kapansa da açık kalır |
| `win-next` | Sadece bir sonraki açılış için Windows'u seçer ve yeniden başlatır (`efibootmgr --bootnext`, sudo ister) |
| `shu`, `shutdown` | `systemctl poweroff` |
| `conv <format> <dosya>...` | ffmpeg ile dönüştürür, çıktı aynı adla yeni uzantıda: `conv mp3 *.mp4`, `conv gif klip.mkv`, `conv mp4 kayit.mkv`. mp3/m4a/opus/flac/wav/wma/aiff/ac3/amr'da görüntüyü atar, mp4/mov/m4v/3gp/webm her yerde oynasın diye yuv420p (ve çift boyut) kullanır, gif'i palet ile üretir, png/jpg/bmp/tiff/jxl'de videonun ilk karesini alır. mkv/avi/wmv/flv/ts/webp/avif vb. için ffmpeg kodeği kendi seçer. `conv pdf` resimleri ImageMagick, belgeleri (docx/odt/pptx/xlsx/txt) LibreOffice ile pdf yapar; `conv png belge.pdf` her sayfayı ayrı resim yapar (`belge-0.png`, `belge-1.png`...) |
| `r-dlp <link> [yt-dlp seçenekleri]` | Reddit gönderisindeki videoyu bulup gönderi başlığıyla indirir. Reddit curl'ü engellediği için linki [vxreddit](https://vxreddit.com) üzerinden bulur, v.redd.it videolarını en iyi kalitede sesle birlikte alır. `reddit.com`, `old.reddit.com`, `redd.it` kısa linki ve doğrudan `v.redd.it` linki kabul eder (`v.redd.it`de dosya adı `reddit-<id>` olur) |
| `zapret-add <site>...` | Siteyi [zapret](https://github.com/bol-van/zapret) listesine (`/opt/zapret/ipset/zapret-hosts-user.txt`) ekler, alt alan adları da kapsanır. Link de kabul eder (`https://www.x.com/yol` → `x.com`). Listeyi `~/Downloads/Config/Zapret/`'e de kopyalar, commit/push elle. sudo ister |
| `kivo` | Kivo'yu `WEBKIT_DISABLE_DMABUF_RENDERER=1` ile açar (WebKitGTK'nın NVIDIA'daki boş/siyah pencere sorununa karşı) |

## find_turkish.py

Bir projedeki Türkçe kelimeleri ve karakterleri bulur (kod, yorum, doküman). İngilizce kelimeleri, anahtar kelimeleri, hex ve URL'leri ayıklayarak yanlış pozitifleri azaltır. Pre-commit hook veya CI'da kullanılabilir.

```fish
./find_turkish.py                     # bulunulan klasörü tara
./find_turkish.py src -c              # sadece yorum satırları
./find_turkish.py -e .go,.py -i vendor,node_modules
./find_turkish.py -s                  # dosya başına özet
./find_turkish.py --json              # JSON çıktı
```

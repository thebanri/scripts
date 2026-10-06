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

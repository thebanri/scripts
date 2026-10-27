function conv --description 'ffmpeg ile dönüştürür: conv <format> <dosya>...'
    if test (count $argv) -lt 2
        echo "Kullanım: conv <format> <dosya>...   örn: conv mp3 *.mp4, conv gif klip.mkv, conv pdf belge.docx" >&2
        return 1
    end

    set -l fmt (string lower -- $argv[1])
    set -l opts
    switch $fmt
        case mp3
            set opts -vn -q:a 2
        case m4a aac opus ogg flac wav wma aiff ac3 mka
            set opts -vn
        case amr
            # AMR-NB yalnızca 8 kHz mono kabul ediyor
            set opts -vn -ar 8000 -ac 1
        case 3gp
            # varsayılan h263 yalnızca sabit boyutları (176x144 vb.) kabul ediyor
            set opts -c:v libx264 -pix_fmt yuv420p -c:a aac -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2'
        case mp4 mov m4v
            # yuv420p: 10-bit/444 kaynaklar telefon ve tarayıcıda oynamıyor; x264 tek sayılı boyut kabul etmiyor (gif'lerde sık)
            set opts -pix_fmt yuv420p -movflags +faststart -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2'
        case webm
            # ffmpeg'in varsayılan VP9 bitrate'i çok düşük, kaliteyi CRF ile sabitle
            set opts -pix_fmt yuv420p -c:v libvpx-vp9 -crf 32 -b:v 0 -c:a libopus
        case gif
            set opts -vf 'fps=15,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse'
        case png jpg jpeg bmp tiff jxl
            # videodan tek kare (ilk kare) alır; webp/avif hareketli kalır
            set opts -frames:v 1
    end
    # diğer formatlarda (mkv avi wmv flv ts webp avif...) ffmpeg uzantıya göre kodeği kendi seçer

    for f in $argv[2..]
        set -l out (path change-extension $fmt $f)
        if test "$out" = "$f"
            echo "Atlandı, zaten $fmt: $f" >&2
            continue
        end
        set -l in_ext (path extension $f | string lower)
        if test $fmt = pdf
            # ffmpeg pdf yazamıyor: resimler ImageMagick, belgeler (docx odt pptx xlsx txt...) LibreOffice ile
            if contains -- $in_ext .png .jpg .jpeg .webp .avif .bmp .tiff .gif
                magick $f $out
            else
                soffice --headless --convert-to pdf --outdir (path dirname $f) $f
            end
        else if test "$in_ext" = .pdf
            # ffmpeg pdf okuyamıyor; çok sayfalıda her sayfa ayrı dosya olur: belge-0.png, belge-1.png...
            magick -density 150 $f $out
        else
            ffmpeg -hide_banner -i $f $opts $out
        end
        or return
    end
end

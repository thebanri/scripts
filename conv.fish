function conv --description 'ffmpeg ile dönüştürür: conv <format> <dosya>...'
    if test (count $argv) -lt 2
        echo "Kullanım: conv <format> <dosya>...   örn: conv mp3 *.mp4, conv gif klip.mkv" >&2
        return 1
    end

    set -l fmt (string lower -- $argv[1])
    set -l opts
    switch $fmt
        case mp3
            set opts -vn -q:a 2
        case m4a aac opus ogg flac wav
            set opts -vn
        case mp4 mov
            # yuv420p: 10-bit/444 kaynaklar telefon ve tarayıcıda oynamıyor
            set opts -pix_fmt yuv420p -movflags +faststart
        case webm
            # ffmpeg'in varsayılan VP9 bitrate'i çok düşük, kaliteyi CRF ile sabitle
            set opts -pix_fmt yuv420p -c:v libvpx-vp9 -crf 32 -b:v 0 -c:a libopus
        case gif
            set opts -vf 'fps=15,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse'
    end
    # diğer formatlarda ffmpeg uzantıya göre kodeği kendi seçer

    for f in $argv[2..]
        set -l out (path change-extension $fmt $f)
        if test "$out" = "$f"
            echo "Atlandı, zaten $fmt: $f" >&2
            continue
        end
        ffmpeg -hide_banner -i $f $opts $out
        or return
    end
end

function r-dlp --description 'Reddit gönderisindeki videoyu bulup yt-dlp ile indirir: r-dlp <link> [yt-dlp seçenekleri]'
    if test (count $argv) -lt 1
        echo "Kullanım: r-dlp <reddit linki> [yt-dlp seçenekleri]" >&2
        return 1
    end

    # v.redd.it linki doğrudan videodur, gönderiye gitmeye gerek yok (başlık da yok)
    set -l id (string match -rg '^(?:https?://)?v\.redd\.it/([a-z0-9]+)' -- $argv[1])
    set -l title
    set -l video

    if test -z "$id"
        # Reddit curl'ü engelliyor; vxreddit bot user-agent'ına gönderinin meta etiketlerini veriyor
        set -l vx (string replace -r '^(https?://)?([a-z]+\.)?reddit\.com' https://vxreddit.com -- $argv[1] \
            | string replace -r '^(https?://)?redd\.it/' https://vxreddit.com/comments/)
        set -l page (curl -sL -A 'TelegramBot (like TwitterBot)' $vx | string match -r '<meta [^>]*>')
        set title (string match -rg 'og:title" content="([^"]*)"' -- $page)[1]
        set video (string match -rg 'og:video" content="([^"]*)"' -- $page)[1]

        if test -z "$video"
            echo "Video bulunamadı: $argv[1]" >&2
            return 1
        end
        set id (string match -rg 'v\.redd\.it%2F([a-z0-9]+)' -- $video)
    end

    # vxreddit 480p veriyor; v.redd.it ise HLS listesinden en iyi kaliteyi sesle birlikte al
    test -n "$id"; and set video https://v.redd.it/$id/HLSPlaylist.m3u8

    # dosya adında / olamaz, çok uzun başlıkları kes
    set title (string replace -a / _ -- $title | string replace -a '&#39;' "'" | string replace -a '&quot;' '"' | string replace -a '&amp;' '&' | string sub -l 100 | string trim)
    test -n "$title"; or set title reddit-$id
    echo (set_color cyan)"Video: "(set_color normal)$video

    yt-dlp -o "$title.%(ext)s" $argv[2..] $video
end

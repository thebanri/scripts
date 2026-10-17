function zapret-add --description 'Siteyi zapret listesine ekler ve Config reposuna kaydeder: zapret-add <site>...'
    if test (count $argv) -eq 0
        echo "Kullanım: zapret-add <site>...   örn: zapret-add twitch.tv https://www.reddit.com/r/x" >&2
        return 1
    end

    set -l list /opt/zapret/ipset/zapret-hosts-user.txt
    set -l repo ~/Downloads/Config/Zapret/zapret-hosts-user.txt

    set -l new
    for s in $argv
        # https://www.site.com/yol -> site.com (liste alt alan adlarını zaten kapsar)
        set -l h (string lower -- $s | string replace -r '^[a-z]+://' '' | string replace -r '[/:?#].*$' '' | string replace -r '^www\.' '')
        if test -z "$h"
            echo "Geçersiz: $s" >&2
        else if grep -qxF -- $h $list; or contains -- $h $new
            echo "Zaten listede: $h"
        else
            set -a new $h
        end
    end
    test (count $new) -gt 0; or return 0

    printf '%s\n' $new | sudo tee -a $list >/dev/null
    or return
    # nfqws liste dosyası değişince kendisi yeniden okur, yeniden başlatmaya gerek yok
    echo "Eklendi: $new"

    if test -d (path dirname $repo)
        cp $list $repo
        echo "Kaydedildi: $repo"
    end
end

function last-pkgs --description 'Son yüklenen veya güncellenen paketleri gösterir'
    set -l limit 20
    if test (count $argv) -gt 0
        set limit $argv[1]
    end

    echo (set_color blue)"Son $limit paket işlemi:"(set_color normal)
    echo "----------------------------------"

    # pacman.log'dan verileri çekiyoruz
    grep -E "installed|upgraded" /var/log/pacman.log | tail -n $limit | while read -l line
        set -l date (echo $line | awk '{print $1}')
        set -l action (echo $line | grep -oE "installed|upgraded")
        set -l package (echo $line | awk '{print $4}')
        set -l pkg_version (echo $line | awk '{print $5}')

        if test "$action" = "installed"
            echo -s (set_color white)"$date "(set_color normal)(set_color green)"YÜKLENDİ  "(set_color normal)" -> "(set_color yellow)"$package "(set_color normal)"$pkg_version"
        else
            echo -s (set_color white)"$date "(set_color normal)(set_color blue)"GÜNCELLENDİ"(set_color normal)" -> "(set_color yellow)"$package "(set_color normal)"$pkg_version"
        end
    end
end

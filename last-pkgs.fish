function last-pkgs --description 'Son işlemleri veya bugünkü güncellemeleri gösterir'
    # Parametreleri tanımlıyoruz: -d veya --today
    argparse 'd/today' -- $argv
    or return

    set -l count 0
    set -l today (date +%Y-%m-%d)

    if set -q _flag_d
        # EĞER -d PARAMETRESİ VARSA: Sadece bugünün tarihini içeren satırları filtrele
        echo (set_color blue)"Bugün ($today) işlem gören tüm paketler:"(set_color normal)
        echo "--------------------------------------------------------"

        grep "\[$today" /var/log/pacman.log | grep -E "installed|upgraded" | while read -l line
            _display_pkg_line "$line"
            set count (math $count + 1)
        end
    else
        # EĞER PARAMETRE YOKSA: Önceki mantık (Son 3 işlem grubu)
        set -l num_transactions 3
        if test -n "$argv[1]"
            set num_transactions $argv[1]
        end

        set -l start_lines (grep -n "transaction started" /var/log/pacman.log | tail -n $num_transactions | cut -f1 -d:)

        if test -z "$start_lines"
            echo (set_color red)"İşleme dair bir kayıt bulunamadı."(set_color normal)
            return 1
        end

        set -l first_line $start_lines[1]
        echo (set_color blue)"Son $num_transactions işlem grubundaki tüm paketler:"(set_color normal)
        echo "--------------------------------------------------------"

        sed -n "$first_line,\$p" /var/log/pacman.log | grep -E "installed|upgraded" | while read -l line
            _display_pkg_line "$line"
            set count (math $count + 1)
        end
    end

    # Özet bilgisi
    if test $count -eq 0
        echo "Herhangi bir paket işlemi bulunamadı."
    else
        echo "--------------------------------------------------------"
        echo (set_color magenta)"Toplam $count paket işlem gördü."(set_color normal)
    end
end

# Yardımcı fonksiyon: Satırları renklendirip basar
function _display_pkg_line
    set -l line $argv[1]
    set -l date (echo $line | awk '{print $1}' | tr -d '[]')
    set -l action (echo $line | grep -oE "installed|upgraded")
    set -l package (echo $line | awk '{print $4}')
    set -l versions (echo $line | cut -d ' ' -f 5- | tr -d '()')

    if test "$action" = "installed"
        echo -s (set_color white)"$date "(set_color normal)(set_color green)"YÜKLENDİ  "(set_color normal)" -> "(set_color yellow)"$package "(set_color normal)(set_color cyan)"$versions"
    else
        echo -s (set_color white)"$date "(set_color normal)(set_color blue)"GÜNCELLENDİ"(set_color normal)" -> "(set_color yellow)"$package "(set_color normal)(set_color cyan)"$versions"
    end
end

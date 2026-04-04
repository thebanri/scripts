#!/usr/bin/fish
# win-next.fish

function win-next
    # Windows ID'sini otomatik bulalım
set WINDOWS_ID (sudo efibootmgr | string match -r "Boot([0-9A-F]{4}).*(Microsoft|Windows)" | head -n 1 | string replace -r "Boot([0-9A-F]{4}).*" '$1')

    if test -z "$WINDOWS_ID"
        echo "Hata: Windows EFI girişi bulunamadı!"
        return 1
    end

    echo "Sadece bu seferlik Windows ($WINDOWS_ID) açılacak..."
    sudo efibootmgr --bootnext $WINDOWS_ID
    sudo systemctl reboot
end

win-next

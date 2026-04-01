function sh --wraps='systemctl poweroff' --description 'alias sh=systemctl poweroff'
    systemctl poweroff $argv
end

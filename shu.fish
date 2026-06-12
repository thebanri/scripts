function shu --wraps='systemctl poweroff' --description 'alias shu=systemctl poweroff'
    systemctl poweroff $argv
end

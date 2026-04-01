function open --wraps='xdg-open .' --wraps='xdg-open . > /dev/null 2>&1 &'
    if count $argv > /dev/null
        # Eğer bir dosya/klasör ismi verdiysen onu açar
        xdg-open $argv > /dev/null 2>&1 &
    else
        # Eğer hiçbir şey yazmadıysan (.) yani bulunduğun klasörü açar
        xdg-open . > /dev/null 2>&1 &
    end
    disown # Terminali kapattığında Dolphin'in kapanmamasını sağlar
end

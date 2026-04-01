function cache --wraps='sudo rm -rf /var/cache/pacman/pkg/download* && yay -Scc' --wraps="sudo sh -c 'rm -rf /var/cache/pacman/pkg/download*' && yay -Scc" --description "alias cache=sudo sh -c 'rm -rf /var/cache/pacman/pkg/download*' && yay -Scc"
    sudo sh -c 'rm -rf /var/cache/pacman/pkg/download*' && yay -Scc $argv
end

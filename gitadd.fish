function gitadd --description 'Add all changes, commit with oco and push'
    git add .
    if oco --yes
        git push
    else
        echo "oco failed or no changes to commit."
    end
end

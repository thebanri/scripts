function gitadd --description 'Iteratively add and commit changed files using oco'
    for file in (git diff --name-only)
        git add $file && oco --yes
    end
end

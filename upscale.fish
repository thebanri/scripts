function upscale --description 'Resmi Real-ESRGAN ile 4K yapar'
    if test (count $argv) -eq 0
        echo "Kullanım: upscale <resim>..."
        return 1
    end
    set -l dir ~/.local/share/realesrgan
    set -l bin $dir/realesrgan-ncnn-vulkan
    if not test -x $bin
        set -l url https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip
        set -l zip (mktemp --suffix .zip)
        echo "Real-ESRGAN indiriliyor (ilk sefer)..."
        if not curl -fL --progress-bar -o $zip $url
            rm -f $zip
            return 1
        end
        # Resmi v0.2.5.0 zip'inin hash'i; tutmazsa dosya değişmiş demektir, açılmaz
        if not echo "e5aa6eb131234b87c0c51f82b89390f5e3e642b7b70f2b9bbe95b6a285a40c96  $zip" | sha256sum -c --quiet
            echo "Hash tutmadı, indirilen dosya silindi." >&2
            rm -f $zip
            return 1
        end
        mkdir -p $dir
        unzip -oq $zip realesrgan-ncnn-vulkan 'models/*' -d $dir
        rm -f $zip
        chmod +x $bin
    end
    set -l tmp (mktemp -d)
    for f in $argv
        set -l out (string replace -r '\.[^./]+$' '' -- $f)_4K.png
        # Önce 4x (1080p → 8K), sonra Lanczos ile 4K'ya: direkt büyütmekten daha keskin
        $bin -i $f -o $tmp/x4.png -n realesrgan-x4plus -m $dir/models 2>/dev/null
        and magick $tmp/x4.png -filter Lanczos -resize 3840x2160 $out
        and echo "✓ $out"
        or echo "✗ $f" >&2
    end
    rm -rf $tmp
end

function zen_profile_copy --description 'Zen Browser profil verilerini eski profilden yeniye kopyalar'
    # Hedef klasörleri tanımlayalım (.zen klasörü baz alınarak)
    set OLD "$HOME/.zen/cm9i2ba1.Default (release)"
    set NEW "$HOME/.zen/g0k3in8e.sef"

    if not test -d "$OLD"
        echo "Hata: Eski profil dizini bulunamadı ($OLD)"
        return 1
    end

    echo "Zen Browser profil taşıma işlemi başlatılıyor..."

    # 1. Temel Veriler (Çerezler, Şifreler, Yer İmleri, Geçmiş)
    echo "Temel veriler kopyalanıyor..."
    cp "$OLD/cookies.sqlite" "$NEW/"
    cp "$OLD/key4.db" "$NEW/"
    cp "$OLD/logins.json" "$NEW/"
    cp "$OLD/places.sqlite" "$NEW/"
    cp "$OLD/favicons.sqlite" "$NEW/"
    cp "$OLD/formhistory.sqlite" "$NEW/"

    # 2. Eklentiler ve Kayıtları
    echo "Eklentiler kopyalanıyor..."
    cp -r "$OLD/extensions" "$NEW/"
    cp "$OLD/extensions.json" "$NEW/"
    cp "$OLD/extension-preferences.json" "$NEW/"
    cp "$OLD/extension-settings.json" "$NEW/"

    # 3. Zen Browser Özel Ayarları ve Açık Sekmeler
    echo "Tarayıcı ayarları ve sekmeler kopyalanıyor..."
    cp "$OLD/zen-sessions.jsonlz4" "$NEW/"
    cp "$OLD/zen-themes.json" "$NEW/"
    cp "$OLD/zen-keyboard-shortcuts.json" "$NEW/"
    cp -r "$OLD/chrome" "$NEW/"

    # 4. KRİTİK KISIM: Sadece Eklenti Ayarlarını Aktar (YouTube çöplerini geride bırak)
    echo "Eklenti ayarları süzülerek aktarılıyor..."
    mkdir -p "$NEW/storage/default"
    cp -r "$OLD"/storage/default/moz-extension+++* "$NEW/storage/default/"

    echo "Taşıma işlemi başarıyla tamamlandı. Şişmiş veriler ve bozuk ayarlar geride bırakıldı!"
end

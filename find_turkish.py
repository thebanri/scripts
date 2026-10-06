#!/usr/bin/env python3
"""
find_turkish.py - Comprehensive Turkish Text and Word Detector

Scans projects for Turkish words, characters, and phrases across source code,
comments, and documentation with high accuracy and low false-positive rates.

Features:
  - 100% detection of Turkish-specific characters (ç, ğ, ı, ö, ş, ü, Ç, Ğ, İ, Ö, Ş, Ü)
  - Extensive dictionary of Turkish roots, verbs, inflections, and software/UI terminology
  - Morphological suffix & agglutinative word pattern recognition
  - Filter for false positives (English words, programming keywords, hex, URLs)
  - Configurable: comments-only mode, file extension filters, ignore paths, JSON output
  - Suitable for pre-commit hooks, CI/CD pipelines, and local audits
"""

import argparse
import json
import os
import re
import sys
from typing import List, Dict, Set, Tuple, Optional

# ANSI colors for terminal output
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

# Turkish characters regex
RE_TR_CHARS = re.compile(r"[çğıöşüÇĞİÖŞÜ]")

# Common English words that must NOT trigger false positives
ENGLISH_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "almost", "alone",
    "along", "already", "also", "always", "am", "among", "an", "and", "another",
    "any", "anyone", "anything", "anywhere", "apply", "are", "area", "around",
    "as", "at", "auto", "back", "base", "basic", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "call", "came", "can", "case",
    "cell", "change", "check", "close", "code", "color", "come", "data", "day",
    "default", "do", "does", "done", "down", "draw", "drop", "due", "each", "early",
    "easy", "else", "end", "even", "event", "every", "exit", "face", "fail", "fast",
    "few", "file", "fill", "find", "first", "fit", "fixed", "for", "format", "frame",
    "free", "from", "front", "full", "get", "give", "go", "good", "got", "great",
    "had", "half", "has", "have", "he", "held", "help", "her", "here", "high", "him",
    "his", "hit", "hold", "home", "how", "if", "in", "into", "is", "it", "its", "just",
    "keep", "key", "kind", "know", "last", "late", "layer", "layout", "left", "less",
    "let", "like", "limit", "line", "list", "live", "load", "lock", "long", "look",
    "loop", "low", "make", "many", "map", "match", "max", "may", "me", "mean", "min",
    "mode", "more", "most", "move", "much", "must", "my", "name", "near", "need",
    "never", "new", "next", "nil", "no", "node", "none", "not", "now", "of", "off",
    "often", "ok", "old", "on", "once", "one", "only", "open", "or", "order", "other",
    "our", "out", "over", "own", "page", "part", "pass", "path", "per", "pick", "plan",
    "point", "press", "pure", "push", "put", "query", "range", "raw", "read", "real",
    "red", "reset", "right", "root", "row", "rule", "run", "runs", "safe", "same",
    "save", "saw", "say", "scan", "scope", "screen", "see", "seen", "select", "send",
    "set", "sets", "show", "side", "simple", "since", "size", "skip", "slice", "slow",
    "small", "so", "some", "soon", "space", "span", "split", "stack", "start", "state",
    "stay", "step", "still", "stop", "such", "sure", "system", "table", "take", "task",
    "test", "text", "than", "that", "the", "their", "them", "then", "there", "these",
    "they", "thin", "thing", "this", "those", "though", "three", "through", "time",
    "to", "too", "top", "total", "true", "try", "turn", "two", "type", "under", "unit",
    "until", "up", "upon", "use", "used", "user", "using", "valid", "value", "view",
    "wait", "want", "was", "way", "we", "well", "went", "were", "what", "when",
    "where", "which", "while", "white", "who", "whole", "why", "wide", "width",
    "will", "with", "word", "work", "would", "wrap", "write", "wrong", "year",
    "yes", "yet", "you", "your", "zero"
}

# Extensive Turkish word dictionary (both with Turkish chars and ASCII-fied spellings)
TURKISH_WORDS = {
    # Pronouns & Demonstratives
    "ben", "sen", "biz", "siz", "onlar", "bana", "sana", "bize", "size", "onlara",
    "beni", "seni", "bizi", "sizi", "onlari", "onları", "benim", "senin", "onun",
    "bizim", "sizin", "onlarin", "onların", "kendisi", "kendileri", "kendine", "kendini",
    "bunun", "buna", "bunu", "bunda", "bundan", "sunun", "şunun", "suna", "şuna",
    "sunu", "şunu", "sunda", "şunda", "sundan", "şundan", "bunlar", "sunlar", "şunlar",
    "bunlarin", "bunların", "bunlara", "bunlari", "bunları", "burada", "buraya", "buradan",
    "surada", "şurada", "suraya", "şuraya", "oraya", "oradan",

    # Conjunctions & Prepositions
    "veya", "ve", "ile", "icin", "için", "gibi", "kadar", "gore", "göre", "ise",
    "cunku", "çünkü", "halbuki", "oysa", "madem", "meger", "meğer", "boylece", "böylece",
    "dolayisiyla", "dolayısıyla", "ayrica", "ayrıca", "ustelik", "üstelik", "zaten",
    "ancak", "fakat", "lakin", "rağmen", "ragmen", "dolayi", "dolayı", "oturu", "ötürü",

    # Adverbs, Particles, Questions
    "daha", "cok", "çok", "fazla", "sadece", "yalniz", "yalnız", "artik", "artık",
    "henuz", "henüz", "bile", "simdi", "şimdi", "sonra", "once", "önce", "eger", "eğer",
    "sayet", "şayet", "yoksa", "varsa", "degil", "değil", "evet", "hayir", "hayır",
    "neden", "nicin", "niçin", "niye", "nasil", "nasıl", "nerede", "nereden", "nereye",
    "hangi", "hangisi", "kac", "kaç", "kacinci", "kaçıncı",

    # Quantifiers & Indefinites
    "biri", "birisi", "hepsi", "tumu", "tümü", "butunu", "bütünü", "herkes",
    "hicbiri", "hiçbiri", "kimse", "sey", "şey", "seyler", "şeyler", "herhangi",
    "birkac", "birkaç", "bircok", "birçok", "butun", "bütün",

    # Actions / Verbs (Common forms)
    "yap", "yapmak", "yapar", "yapti", "yaptı", "yapiyor", "yapıyor", "yapacak",
    "yapmali", "yapmalı", "yapilsin", "yapılsın", "yapildi", "yapıldı", "yapilir", "yapılır",
    "yapilamaz", "yapılamaz", "yapilacak", "yapılacak", "yapan", "yapilan", "yapılan",
    "et", "etmek", "eder", "etti", "ediyor", "edecek", "etmeli", "edilsin", "edildi",
    "edilir", "edilemez", "edilecek", "eden", "edilen",
    "ol", "olmak", "olur", "oldu", "oluyor", "olacak", "olmali", "olmalı", "olsun",
    "olamaz", "olursa", "oldugu", "olduğu", "olmadigi", "olmadığı", "olan",
    "al", "almak", "alir", "alır", "aldi", "aldı", "aliyor", "alıyor", "alacak",
    "almali", "almalı", "alinsin", "alınsın", "alindi", "alındı", "alinir", "alınır",
    "alan", "alinan", "alınan",
    "ver", "vermek", "verir", "verdi", "veriyor", "verecek", "vermeli", "verilsin",
    "verildi", "verilir", "veren", "verilen",
    "gel", "gelmek", "gelir", "geldi", "geliyor", "gelecek", "gelmeli", "gelen",
    "gitmek", "gider", "gitti", "gidiyor", "gidecek", "gitmeli", "giden",
    "gor", "gör", "gormek", "görmek", "gorur", "görür", "gordu", "gördü", "goruyor", "görüyor",
    "bak", "bakmak", "bakar", "bakti", "baktı", "bakiyor", "bakıyor",
    "bul", "bulmak", "bulur", "buldu", "buluyor", "bulunur", "bulunan",
    "yaz", "yazmak", "yazar", "yazdi", "yazdı", "yaziyor", "yazıyor", "yazacak",
    "yazilsin", "yazılsın", "yazildi", "yazıldı", "yazilir", "yazılır",
    "oku", "okumak", "okur", "okudu", "okuyor", "okunur", "okunan",
    "ekle", "eklemek", "ekler", "ekledi", "ekliyor", "ekleyecek", "eklensin", "eklendi", "eklenir", "eklenen",
    "sil", "silmek", "siler", "sildi", "siliyor", "silinsin", "silindi", "silinir", "silinen",
    "guncelle", "güncelle", "gunceller", "günceller", "guncelledi", "güncelledi", "guncellenir", "güncellenir",
    "temizle", "temizlemek", "temizler", "temizledi", "temizlenir",
    "baslat", "başlat", "baslatir", "başlatır", "baslatti", "başlattı", "baslatilir", "başlatılır",
    "durdur", "durdurmak", "durdurur", "durdurdu", "durdurulur",
    "hesapla", "hesaplamak", "hesaplar", "hesapladi", "hesapladı", "hesaplanir", "hesaplanır", "hesaplanan",
    "belirle", "belirlemek", "belirler", "belirledi", "belirlenir", "belirlenen",
    "tanimla", "tanımla", "tanimlar", "tanımlar", "tanimladi", "tanımladı", "tanimlanir", "tanımlanır",
    "ayarla", "ayarlamak", "ayarlar", "ayarladi", "ayarladı", "ayarlanir", "ayarlanır", "ayarlanan",
    "ciz", "çiz", "cizmek", "çizmek", "cizer", "çizer", "cizdi", "çizdi", "cizilir", "çizilir", "cizilen", "çizilen",
    "dondur", "döndür", "dondurur", "döndürür", "dondurdu", "döndürdü", "dondurulur", "döndürülür",
    "yonlendir", "yönlendir", "yonlendirir", "yönlendirir", "yonlendirilir", "yönlendirilir",
    "gonder", "gönder", "gonderir", "gönderir", "gonderildi", "gönderildi", "gonderilir", "gönderilir",
    "cagir", "çağır", "cagirir", "çağırır", "cagirildi", "çağırıldı", "cagirilir", "çağırılır",
    "kullan", "kullanmak", "kullanir", "kullanır", "kullandi", "kullandı", "kullanilir", "kullanılır", "kullanilan", "kullanılan",
    "kaydet", "kaydetmek", "kaydeder", "kaydetti", "kaydedilir", "kaydedildi", "kaydol",
    "seç", "secmek", "seçmek", "secer", "seçer", "secti", "seçti", "secilir", "seçilir", "secilen", "seçilen",
    "kapat", "kapatmak", "kapatir", "kapatır", "kapatti", "kapattı", "kapatilir", "kapatılır",
    "ac", "aç", "acmak", "açmak", "acar", "açar", "acti", "açtı", "acilir", "açılır",
    "baglan", "bağlan", "baglanir", "bağlanır", "baglandi", "bağlandı",
    "coz", "çöz", "cozmek", "çözmek", "cozer", "çözer", "cozdu", "çözdü", "cozulur", "çözülür",
    "yukle", "yükle", "yukler", "yükler", "yuklendi", "yüklendi", "yuklenir", "yüklenir",
    "indir", "indirmek", "indirir", "indirdi", "indirilir",
    "uret", "üret", "uretir", "üretir", "uretildi", "üretildi", "uretilir", "üretilir",
    "sagla", "sağla", "saglar", "sağlar", "sagladi", "sağladı", "saglanir", "sağlanır",
    "icerir", "içerir", "iceriyor", "içeriyor", "kapsar", "kapsaminda", "kapsamında",

    # Software / UI Domain Concepts
    "ekran", "ekrana", "ekranda", "ekrandan", "pencere", "penceresi", "pencerede",
    "sekme", "sekmesi", "sekmesinde", "sekmesini", "dugme", "düğme", "dugmesi", "düğmesi",
    "buton", "butonu", "butonlar", "butonuna", "kutu", "kutusu", "kutusunda",
    "cerceve", "çerçeve", "cercevesi", "çerçevesi", "kenar", "kenari", "kenarı", "kenarlik", "kenarlık",
    "kenarligi", "kenarlığı", "kenarliklar", "kenarlıklar", "golge", "gölge", "golgesi", "gölgesi",
    "metin", "metni", "metinler", "yazi", "yazı", "yazisi", "yazısı", "baslik", "başlık",
    "basligi", "başlığı", "altbilgi", "etiket", "etiketi", "karakter", "karakterler",
    "harf", "harfler", "simge", "simgesi", "sembol",
    "satir", "satır", "satiri", "satırı", "satirlar", "satırlar", "sutun", "sütun",
    "sutunu", "sütunu", "sutunlar", "sütunlar", "hucre", "hücre", "hucresi", "hücresi",
    "hucreler", "hücreler", "tablo", "tablosu", "tabloda", "liste", "listesi", "listede",
    "oge", "öğe", "ogesi", "öğesi", "ogeler", "öğeleri", "eleman", "elemani", "elemanı",
    "elemanlar", "elemanları", "dugum", "düğüm", "dugumu", "düğümü", "agac", "ağaç",
    "agaci", "ağacı", "kok", "kök", "koku", "kökü", "yaprak",
    "alan", "alani", "alanı", "alanlar", "alanları", "boyut", "boyutu", "boyutlandirma", "boyutlandırma",
    "genislik", "genişlik", "genisligi", "genişliği", "yukseklik", "yükseklik", "yuksekligi", "yüksekliği",
    "olcek", "ölçek", "olcekleme", "ölçekleme", "oran", "orani", "oranı", "yuzde", "yüzde",
    "sabit", "esnek", "konum", "konumu", "koordinat", "koordinati", "koordinatı",
    "nokta", "noktasi", "noktası", "cizgi", "çizgi", "cizgisi", "çizgisi", "daire",
    "ucgen", "üçgen", "dikdortgen", "dikdörtgen", "kare",
    "renk", "rengi", "renkler", "renkleri", "dolgu", "dolgusu", "parlak", "koyu",
    "acik", "açık", "kapali", "kapalı", "saydam", "opak",
    "arka", "sol", "sag", "sağ", "ust", "üst", "orta", "tepe", "taban", "merkez",
    "klavye", "klavyeden", "klavyesi", "fare", "fareyle", "fareden", "fareyi",
    "tus", "tuş", "tusu", "tuşu", "tuslar", "tuşlar", "tuslari", "tuşları", "tusuna", "tuşuna",
    "tiklama", "tıklama", "tiklandi", "tıklandı", "tiklaninca", "tıklanınca",
    "surukle", "sürükle", "surukleme", "sürükleme", "birak", "bırak", "kaydir", "kaydır",
    "kaydirma", "kaydırma", "kaydirici", "kaydırıcı", "tekerlek",
    "odak", "odagi", "odağı", "odaklanmis", "odaklanmış", "odaklanabilir", "odaklama",
    "secili", "seçili", "secim", "seçim", "secimi", "seçimi", "vurgu", "vurgulama",
    "katman", "katmani", "katmanı", "katmanlar", "katmanlari", "katmanları", "oncelik", "öncelik",
    "derinlik", "derinligi", "derinliği",
    "tampon", "tamponu", "bellek", "bellegi", "belleği", "dizi", "dizisi", "yigin", "yığın", "kuyruk",
    "hata", "hatasi", "hatası", "hatali", "hatalı", "uyari", "uyarı", "uyarisi", "uyarısı",
    "bilgi", "bilgisi", "basari", "başarı", "basarili", "başarılı", "basarisiz", "başarısız",
    "giris", "giriş", "girisi", "girişi", "cikis", "çıkış", "cikisi", "çıkışı",
    "durum", "durumu", "durumlar", "durumlari", "durumları",
    "deger", "değer", "degeri", "değeri", "degerler", "değerler", "degisken", "değişken",
    "zaman", "zamani", "zamanı", "sure", "süre", "suresi", "süresi", "gecikme", "hiz", "hız",
    "hizi", "hızı", "ivme", "dongu", "döngü", "dongusu", "döngüsü", "adim", "adım", "adimi", "adımı",
    "ornek", "örnek", "ornegi", "örneği", "sablon", "şablon", "sablonu", "şablonu",
    "kural", "kurallar", "kosul", "koşul", "kosulu", "koşulu", "sart", "şart",
    "arama", "filtre", "filtreleme", "sirala", "sırala", "siralama", "sıralama",
    "gorunum", "görünüm", "gorunur", "görünür", "gorunmez", "görünmez", "gizli",
    "varsayilan", "varsayılan", "otomatik", "dogrudan", "doğrudan", "ozel", "özel", "genel"
}

# Regex for common Turkish verb and grammatical endings in ASCII-written words
RE_TR_VERB_ENDINGS = re.compile(
    r"\b[a-z]{3,}(?:iyor|uyor|uyor|uyor|dugu|tigi|dikce|dikten|meden|madan|erek|arak|"
    r"ebil|abil|elim|alim|siniz|sunuz|yapan|yici|ici|leri|lari|inda|inde|indan|inden|"
    r"iyle|iyle|sinda|sinde|landir|lendir|lestir|lastir)\b",
    re.IGNORECASE
)

DEFAULT_IGNORE_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "vendor", "dist", "build",
    ".idea", ".vscode", "__pycache__", ".venv", "venv", ".brain"
}

DEFAULT_EXTENSIONS = {
    ".go", ".py", ".rs", ".js", ".jsx", ".ts", ".tsx", ".c", ".h", ".cpp",
    ".hpp", ".java", ".kt", ".swift", ".sh", ".bash", ".zsh", ".yaml", ".yml",
    ".toml", ".json", ".md", ".html", ".css", ".txt"
}


class MatchInfo:
    def __init__(self, line_num: int, line_content: str, word: str, match_type: str):
        self.line_num = line_num
        self.line_content = line_content.strip()
        self.word = word
        self.match_type = match_type

    def to_dict(self):
        return {
            "line": self.line_num,
            "word": self.word,
            "type": self.match_type,
            "snippet": self.line_content
        }


def extract_comment(line: str, ext: str) -> Optional[str]:
    """Extract comment portion of a line based on file extension."""
    s = line.strip()
    if not s:
        return None

    # Skip compiler directives
    if s.startswith(("//go:", "// +build", "#pragma", "#!")):
        return None

    if ext in {".go", ".rs", ".js", ".jsx", ".ts", ".tsx", ".c", ".h", ".cpp", ".hpp", ".java", ".kt", ".swift"}:
        if "//" in s:
            return s[s.index("//") + 2:].strip()
        if "/*" in s:
            part = s[s.index("/*") + 2:]
            return part[:part.index("*/")].strip() if "*/" in part else part.strip()
        if s.startswith("*"):
            return s[1:].strip()

    elif ext in {".py", ".sh", ".bash", ".zsh", ".yaml", ".yml", ".toml"}:
        if "#" in s:
            return s[s.index("#") + 1:].strip()

    elif ext in {".html", ".xml", ".md"}:
        if "<!--" in s:
            part = s[s.index("<!--") + 4:]
            return part[:part.index("-->")].strip() if "-->" in part else part.strip()

    return None


def is_false_positive_word(word: str) -> bool:
    """Check if token is obviously English, hex, URL or technical symbol."""
    w = word.lower()
    if w in ENGLISH_STOPWORDS:
        return True
    # Hex or identifier
    if re.match(r"^(0x[0-9a-f]+|#[0-9a-f]{3,8}|[0-9a-f]{6,})$", w):
        return True
    # URL or path-like
    if "http" in w or "www" in w or "/" in w or "\\" in w:
        return True
    # Single letter or numbers
    if len(w) <= 1 or w.isdigit():
        return True
    return False


def analyze_text(text: str) -> List[Tuple[str, str]]:
    """
    Analyze given text line for Turkish words or patterns.
    Returns list of (word, reason).
    """
    detected = []
    # Tokenize word-like chunks (Unicode-aware)
    tokens = re.findall(r"[A-Za-zçğıöşüÇĞİÖŞÜ0-9_]+", text)

    for tok in tokens:
        # Check 1: Turkish-specific characters
        if RE_TR_CHARS.search(tok):
            # Ignore single letters if just symbol
            if len(tok) >= 2 or tok in "çğıöşüÇĞİÖŞÜ":
                detected.append((tok, "Turkish Character (ç,ğ,ı,ö,ş,ü)"))
                continue

        lower = tok.lower()
        if is_false_positive_word(lower):
            continue

        # Check 2: Direct match in Turkish vocabulary
        if lower in TURKISH_WORDS:
            detected.append((tok, "Turkish Word Dictionary"))
            continue

        # Check 3: Morphological verb/grammar ending match
        if len(lower) >= 5 and RE_TR_VERB_ENDINGS.search(lower):
            # Verify it's not a common English word
            if lower not in ENGLISH_STOPWORDS:
                detected.append((tok, "Turkish Grammatical Pattern"))
                continue

    return detected


def scan_file(filepath: str, comments_only: bool = False) -> List[MatchInfo]:
    """Scan a single file for Turkish tokens."""
    matches = []
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f, 1):
                target_text = line
                if comments_only:
                    comment = extract_comment(line, ext)
                    if not comment:
                        continue
                    target_text = comment

                hits = analyze_text(target_text)
                for word, reason in hits:
                    matches.append(MatchInfo(idx, line, word, reason))
    except (UnicodeDecodeError, PermissionError, IsADirectoryError, OSError):
        pass

    return matches


def scan_directory(
    root_dir: str,
    extensions: Set[str],
    ignore_dirs: Set[str],
    comments_only: bool = False
) -> Dict[str, List[MatchInfo]]:
    """Recursively scan a directory for files containing Turkish words."""
    results = {}
    for root, dirs, files in os.walk(root_dir):
        # Exclude ignored directories in-place
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]

        for f in files:
            _, ext = os.path.splitext(f)
            if extensions and ext.lower() not in extensions:
                continue

            path = os.path.normpath(os.path.join(root, f))
            file_matches = scan_file(path, comments_only=comments_only)
            if file_matches:
                results[path] = file_matches

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Turkish Word and Text Scanner for Projects"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to file or directory to scan (default: current directory)"
    )
    parser.add_argument(
        "-c", "--comments-only",
        action="store_true",
        help="Scan only comment lines instead of full files"
    )
    parser.add_argument(
        "-e", "--ext",
        help="Comma-separated file extensions to scan (e.g. .go,.py,.js)"
    )
    parser.add_argument(
        "-i", "--ignore",
        help="Comma-separated directory or file names to ignore"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "-s", "--summary",
        action="store_true",
        help="Show only summary counts per file"
    )

    args = parser.parse_args()

    extensions = DEFAULT_EXTENSIONS
    if args.ext:
        extensions = {("." + e.lstrip(".")).lower() for e in args.ext.split(",")}

    ignore_dirs = set(DEFAULT_IGNORE_DIRS)
    if args.ignore:
        ignore_dirs.update(args.ignore.split(","))

    target = args.path
    results: Dict[str, List[MatchInfo]] = {}

    if os.path.isfile(target):
        file_matches = scan_file(target, comments_only=args.comments_only)
        if file_matches:
            results[target] = file_matches
    elif os.path.isdir(target):
        results = scan_directory(
            target,
            extensions=extensions,
            ignore_dirs=ignore_dirs,
            comments_only=args.comments_only
        )
    else:
        print(f"Error: Path '{target}' not found.", file=sys.stderr)
        sys.exit(2)

    total_matches = sum(len(m) for m in results.values())
    total_files = len(results)

    if args.json:
        out = {
            "total_files": total_files,
            "total_matches": total_matches,
            "files": {path: [m.to_dict() for m in matches] for path, matches in results.items()}
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        sys.exit(1 if total_matches > 0 else 0)

    # Human-readable output
    print(f"\n{COLOR_BOLD}=== Turkish Word & Character Scanner ==={COLOR_RESET}")
    print(f"Scanned path: {os.path.abspath(target)}")
    print(f"Mode: {'Comments Only' if args.comments_only else 'Full Content (Code + Comments + Strings)'}")
    print(f"Files found with Turkish words: {total_files}")
    print(f"Total occurrences: {total_matches}\n")

    if not results:
        print(f"{COLOR_GREEN}✓ No Turkish words found in the scanned files.{COLOR_RESET}\n")
        sys.exit(0)

    for path, matches in sorted(results.items()):
        print(f"{COLOR_CYAN}{COLOR_BOLD}{path}{COLOR_RESET} ({len(matches)} match{'es' if len(matches) > 1 else ''}):")
        if args.summary:
            continue
        for m in matches[:15]:
            print(f"  {COLOR_YELLOW}L{m.line_num}:{COLOR_RESET} [{COLOR_RED}{m.word}{COLOR_RESET}] ({m.match_type}) -> {m.line_content}")
        if len(matches) > 15:
            print(f"  ... and {len(matches) - 15} more matches in this file")
        print()

    sys.exit(1 if total_matches > 0 else 0)


if __name__ == "__main__":
    main()

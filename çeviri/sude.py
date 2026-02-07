import json

# ---------------- JSON YARDIMCI ----------------
def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"❕ {path} okunamadı, varsayılan değer kullanılacak")
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_dictionary(path="sözlük.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ sözlük.json bulunamadı veya bozuk")
        return {}

# ---------------- VERİLER ----------------
sozluk = load_dictionary()
history = load_json("geçmiş.json", [])
favorites = load_json("favoriler.json", [])

if not sozluk:
    exit()

# ---------------- ALFABE TABLOLARI ----------------
latin_to_cyrillic = {
    'a':'а','b':'б','v':'в','g':'г','d':'д','ye':'е','yo':'ё','j':'ж','z':'з','i':'и','iy':'й','k':'к',
    'l':'л','m':'м','n':'н','o':'о','p':'п','r':'р','s':'с','t':'т','u':'у','f':'ф','h':'х',
    'ch':'ч','sh':'ш','sht':'щ','yu':'ю','ya':'я','e':'э'
}

latin_to_greek = {
    'a':'α','v':'β','g':'γ','d':'δ','e':'ε','z':'ζ','i':'η','th':'θ','ch':'χ','k':'κ','l':'λ',
    'm':'μ','n':'ν','x':'ξ','o':'ο','p':'π','r':'ρ','s':'σ','t':'τ','y':'υ','f':'φ','ps':'ψ','b':'μπ'
}

# ---------------- ALFABE DÖNÜŞTÜRÜCÜ ----------------
def convert_alphabet(word, table):
    word = word.lower()
    result = ""
    i = 0
    while i < len(word):
        if i+3 <= len(word) and word[i:i+3] in table:
            result += table[word[i:i+3]]
            i += 3
        elif i+2 <= len(word) and word[i:i+2] in table:
            result += table[word[i:i+2]]
            i += 2
        elif word[i] in table:
            result += table[word[i]]
            i += 1
        else:
            result += word[i]
            i += 1
    return result

# ---------------- ANA PROGRAM ----------------
print("🗺 Çok Dilli Çeviri Uygulamasına Hoş Geldiniz!")
print("Diller: tr, ru, el, de")
print("--------------------------------------------")

kaynak_dil = input("Kaynak dili seçin: ").strip().lower()
hedef_dil = input("Hedef dili seçin: ").strip().lower()
destekli = {"tr","ru","el","de"}
if kaynak_dil not in destekli or hedef_dil not in destekli:
    print("❌ Desteklenmeyen dil girdisi")
    exit()
kelime = input("Bir kelime yaz: ").strip().lower()

anahtar = None
for key, diller in sozluk.items():
    if kelime == diller.get(kaynak_dil, "").lower():
        anahtar = key
        break

if not anahtar:
    print("❌ Kelime sözlükte yok")
    exit()

# --- Alfabe ---
kaynak_yazi = sozluk[anahtar].get(kaynak_dil)
hedef_yazi = sozluk[anahtar].get(hedef_dil)
if kaynak_yazi is None or hedef_yazi is None:
    print("❌ Bu kelimenin seçilen dilde karşılığı yok")
    exit()

if kaynak_dil == "ru":
    kaynak_yazi = convert_alphabet(kaynak_yazi, latin_to_cyrillic)
elif kaynak_dil == "el":
    kaynak_yazi = convert_alphabet(kaynak_yazi, latin_to_greek)

if hedef_dil == "ru":
    hedef_yazi = convert_alphabet(hedef_yazi, latin_to_cyrillic)
elif hedef_dil == "el":
    hedef_yazi = convert_alphabet(hedef_yazi, latin_to_greek)

# ---------------- SONUÇ ----------------
print("\n--- SONUÇ ---")
print("Kaynak :", kaynak_yazi)
print("Hedef  :", hedef_yazi)

history.append({
    "from": kaynak_dil,
    "to": hedef_dil,
    "input": kelime,
    "output": hedef_yazi
})
# dosya şişmesin
if len(history) > 200:
    del history[:-200]
save_json("geçmiş.json", history)

fav = input("⭐ Favorilere eklensin mi? (e/h): ").lower()
if fav == "e":
    favorites.append({
        "from": kaynak_dil,
        "to": hedef_dil,
        "input": kelime,
        "output": hedef_yazi
    })
    save_json("favoriler.json", favorites)

print("\n🕘 SON 5 GEÇMİŞ")
for item in history[-5:]:
    print(f'{item["input"]} → {item["output"]}')

print("\n⭐ FAVORİLER")
for item in favorites:
    print(f'{item["input"]} → {item["output"]}')

import json
import tkinter as tk
from tkinter import ttk

# ---------------- JSON ----------------
def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Dosya yoksa veya bozuksa varsayılana dön
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

sozluk = load_json("sözlük.JSON", {})
history = load_json("geçmiş.json", [])
favorites = load_json("favoriler.json", [])
last_translation = ""
last_pronunciation = ""

# ---------------- ALFABE ----------------
latin_to_cyrillic = {
    'a':'а','b':'б','v':'в','g':'г','d':'д','ye':'е','yo':'ё','j':'ж','z':'з','i':'и','iy':'й','k':'к',
    'l':'л','m':'м','n':'н','o':'о','p':'п','r':'р','s':'с','t':'т','u':'у','f':'ф','h':'х',
    'ch':'ч','sh':'ш','sht':'щ','yu':'ю','ya':'я','e':'э'
}

latin_to_greek = {
    "a":"α","b":"β","g":"γ","d":"δ","e":"ε","z":"ζ","i":"ι","k":"κ",
    "l":"λ","m":"μ","n":"ν","o":"ο","p":"π","r":"ρ","s":"σ","t":"τ",
    "y":"υ","f":"φ","ch":"χ"
}

def convert(word, table):
    out, i = "", 0
    while i < len(word):
        if i+2 <= len(word) and word[i:i+2] in table:
            out += table[word[i:i+2]]
            i += 2
        elif word[i] in table:
            out += table[word[i]]
            i += 1
        else:
            out += word[i]
            i += 1
    return out

# ---------------- TEMALAR ----------------
THEMES = {
    "light": {
        "bg": "#f5f5f7",
        "panel": "#e5e7eb",
        "card": "#ffffff",
        "text": "#111827",
        "accent": "#4f46e5",
        "hover": "#6366f1",
        "border": "#d1d5db",
        "muted": "#6b7280"
    },
    "dark": {
        "bg": "#1f1f1f",
        "panel": "#171717",
        "card": "#2b2b2b",
        "text": "#f5f5f5",
        "accent": "#0055f2",
        "hover": "#3a3a3a",
        "border": "#333333",
        "muted": "#9ca3af"
    }
}

current_theme = "dark"

# ---------------- ROOT ----------------
root = tk.Tk()
root.title("MiniTranslate")
root.geometry("760x500")
root.resizable(False, False)

style = ttk.Style(root)
try:
    style.theme_use("clam")
except tk.TclError:
    pass

main = tk.Frame(root)
main.pack(fill="both", expand=True, padx=5, pady=5)

# -------- SOL PANEL --------
left = tk.Frame(main, width=220)
left.pack(side="left", fill="y", padx=5, pady=5)
left.pack_propagate(False)

left_title = tk.Label(left, text="Menü", font=("Segoe UI",12,"bold"))
left_title.pack(pady=10)

list_frame = tk.Frame(left)
list_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Button creation helper
def make_button(parent, text, command, icon=None):
    t = THEMES[current_theme]
    b = tk.Frame(parent, bg=t['card'], highlightthickness=1, highlightbackground=t['border'], padx=5, pady=5)
    b.pack(fill="x", pady=5)
    b.bind("<Button-1>", lambda e: command())
    lbl = tk.Label(b, text=text, bg=t['card'], fg=t['text'], font=("Segoe UI",10))
    lbl.pack(side="left")
    lbl.bind("<Button-1>", lambda e: command())
    return b

def make_list_item(parent, text, on_select, on_delete):
    """List item with selectable area and delete button."""
    t = THEMES[current_theme]
    item = tk.Frame(parent, bg=t['card'], highlightthickness=1, highlightbackground=t['border'], padx=5, pady=5)
    item.pack(fill="x", pady=5)
    item.bind("<Button-1>", lambda e: on_select())

    lbl = tk.Label(item, text=text, bg=t['card'], fg=t['text'], font=("Segoe UI",10), anchor="w")
    lbl.pack(side="left", fill="x", expand=True)
    lbl.bind("<Button-1>", lambda e: on_select())

    del_btn = tk.Button(item, text="✖", fg="#ef4444", bg=t['card'],
                        relief="flat", bd=0, font=("Segoe UI",10,"bold"),
                        command=on_delete, cursor="hand2")
    del_btn.pack(side="right", padx=4)
    return item

# Menu buttons
def show_menu():
    left_title.config(text="Menü")
    for widget in list_frame.winfo_children(): widget.destroy()
    make_button(list_frame, "🕘 Geçmiş", show_history)
    make_button(list_frame, "⭐ Favoriler", show_fav)

def show_history():
    left_title.config(text="🕘 Geçmiş")
    for widget in list_frame.winfo_children(): widget.destroy()
    for h in history[-20:]:
        make_list_item(
            list_frame,
            f'{h["input"]} → {h["output"]}',
            on_select=lambda h=h: recall_entry(h["input"], h["output"], h.get("pron")),
            on_delete=lambda h=h: remove_history_item(h)
        )
    make_button(list_frame, "🗑️ Geçmişi Temizle", clear_history)
    make_button(list_frame, "← Geri", show_menu)

def show_fav():
    left_title.config(text="⭐ Favoriler")
    for widget in list_frame.winfo_children(): widget.destroy()
    for f in favorites:
        make_list_item(
            list_frame,
            f'{f["input"]} → {f["output"]}',
            on_select=lambda f=f: recall_entry(f["input"], f["output"], f.get("pron")),
            on_delete=lambda f=f: remove_fav_item(f)
        )
    make_button(list_frame, "🗑️ Favorileri Temizle", clear_favorites)
    make_button(list_frame, "← Geri", show_menu)

def clear_history():
    global history
    history = []
    save_json("geçmiş.json", history)
    show_history()

def clear_favorites():
    global favorites
    favorites = []
    save_json("favoriler.json", favorites)
    show_fav()

def remove_history_item(item):
    if item in history:
        history.remove(item)
        save_json("geçmiş.json", history)
        show_history()

def remove_fav_item(item):
    if item in favorites:
        favorites.remove(item)
        save_json("favoriler.json", favorites)
        show_fav()

# -------- ORTA PANEL --------
center = tk.Frame(main, bg=THEMES[current_theme]['bg'])
center.pack(fill="both", expand=True, padx=5, pady=5)

title_label = tk.Label(center, text="MiniTranslate 🌍", font=("Segoe UI",16,"bold"), bg=THEMES[current_theme]['bg'])
title_label.pack(pady=15)

langs = ["tr","ru","el","de"]
src = tk.StringVar(value="tr")
dst = tk.StringVar(value="ru")

lang = tk.Frame(center, bg=THEMES[current_theme]['bg'])
lang.pack()
src_menu = ttk.OptionMenu(lang, src, "tr", *langs)
src_menu.pack(side="left", padx=10)
arrow_label = tk.Label(lang, text="→", bg=THEMES[current_theme]['bg'])
arrow_label.pack(side="left")
dst_menu = ttk.OptionMenu(lang, dst, "ru", *langs)
dst_menu.pack(side="left", padx=10)

entry_frame = tk.Frame(center, bg=THEMES[current_theme]['card'], padx=5, pady=5)
entry_frame.pack(pady=15, ipadx=2, ipady=2)
entry = tk.Entry(entry_frame, font=("Segoe UI",13), justify="center", bd=0, relief="flat")
entry.pack(ipadx=100, ipady=6)
entry.bind("<Return>", lambda event: translate())

result_frame = tk.Frame(center, bg=THEMES[current_theme]['card'], padx=5, pady=5)
result_frame.pack(pady=10)
result = tk.Text(result_frame, height=6, width=50, font=("Segoe UI",11), bd=0, relief="flat")
result.pack()
result.insert("end","çeviri")
result.config(state="disabled")

btn_frame = tk.Frame(center)
btn_frame.pack(pady=5)
translate_btn = tk.Button(btn_frame, text="ÇEVİR", bg=THEMES[current_theme]['accent'], fg="#111827", relief="flat", padx=15, pady=5, font=("Segoe UI",11,"bold"))
translate_btn.pack(side="left", padx=10)
fav_btn = tk.Button(btn_frame, text="⭐", bg=THEMES[current_theme]['accent'], fg="#111827", relief="flat", padx=12, pady=5, font=("Segoe UI",11,"bold"))
fav_btn.pack(side="left")

# ---------------- ANİMASYONLU FAVORİ YILDIZI ----------------
def update_fav_star():
    current_word = entry.get().strip().lower()
    found = any(f["input"].lower() == current_word for f in favorites)
    target_color = "#FFD700" if found else "#B0B0B0"  # sarı veya gri
    fav_btn.config(fg=target_color)

entry.bind("<KeyRelease>", lambda e: update_fav_star())

# ---------------- FONKSİYONLAR ----------------
def translate():
    global last_translation, last_pronunciation
    word = entry.get().lower().strip()
    s, t = src.get(), dst.get()
    key = None
    for k,v in sozluk.items():
        if v.get(s,"") == word:
            key = k
            break
    result.config(state="normal")
    result.delete("1.0","end")
    last_translation = ""
    last_pronunciation = ""
    if not key:
        result.insert("end","❌ Kelime bulunamadı")
    else:
        out_raw = sozluk[key].get(t)
        if out_raw is None:
            result.insert("end","❌ Bu kelimenin seçilen dilde karşılığı yok")
            result.config(state="disabled")
            update_fav_star()
            return
        pron = out_raw
        out = out_raw
        if t=="ru": out = convert(out_raw, latin_to_cyrillic)
        if t=="el": out = convert(out_raw, latin_to_greek)
        result.insert("end", out)
        result.insert("end", f"\nOkunuş: {pron}")
        last_translation = out
        last_pronunciation = pron
        history.append({"input":word,"output":out,"pron":pron})
        # Tarihçe dosyas? s?n?rs?z b?y?mesin
        if len(history) > 200:
            del history[:-200]
        save_json("geçmiş.json", history)
    result.config(state="disabled")
    update_fav_star()  # çeviri sonrası yıldız güncelle
def add_fav():
    global last_translation, last_pronunciation
    word = entry.get().strip()
    out = last_translation
    pron = last_pronunciation
    if word and out:
        if not any(f["input"].lower() == word.lower() for f in favorites):
            favorites.append({"input": word, "output": out, "pron": pron})
            save_json("favoriler.json", favorites)
    update_fav_star()
def recall_entry(word, output, pron=None):
    global last_translation, last_pronunciation
    if not pron:
        pron = output
    entry.delete(0, "end")
    entry.insert(0, word)
    result.config(state="normal")
    result.delete("1.0", "end")
    result.insert("end", output)
    result.insert("end", f"\nOkunuş: {pron}")
    result.config(state="disabled")
    last_translation = output
    last_pronunciation = pron
    update_fav_star()
translate_btn.config(command=translate)
fav_btn.config(command=add_fav)

# ---------------- TEMA ----------------
def apply_theme():
    t = THEMES[current_theme]
    root.configure(bg=t['bg'])
    main.configure(bg=t['bg'])
    left.configure(bg=t['panel'])
    left_title.configure(bg=t['panel'], fg=t['text'])
    list_frame.configure(bg=t['panel'])
    center.configure(bg=t['bg'])
    title_label.configure(bg=t['bg'], fg=t['text'])
    lang.configure(bg=t['bg'])
    arrow_label.configure(bg=t['bg'], fg=t['text'])

    entry_frame.configure(bg=t['card'], highlightthickness=1, highlightbackground=t['border'])
    entry.configure(bg=t['card'], fg=t['text'], insertbackground=t['text'])
    result_frame.configure(bg=t['card'], highlightthickness=1, highlightbackground=t['border'])
    result.configure(bg=t['card'], fg=t['text'], insertbackground=t['text'])

    btn_frame.configure(bg=t['bg'])
    translate_btn.configure(bg=t['accent'], fg="#111827", activebackground=t['accent'])
    fav_btn.configure(bg=t['accent'], fg="#111827", activebackground=t['accent'])

    style.configure("TMenubutton", background=t['card'], foreground=t['text'], borderwidth=1, relief="flat", padding=6)
    style.map("TMenubutton", background=[("active", t['hover'])], foreground=[("active", t['text'])])
    root.option_add("*Menu.background", t['card'])
    root.option_add("*Menu.foreground", t['text'])
    root.option_add("*Menu.activeBackground", t['hover'])
    root.option_add("*Menu.activeForeground", t['text'])
    for m in (src_menu["menu"], dst_menu["menu"]):
        m.configure(bg=t['card'], fg=t['text'], activebackground=t['hover'], activeforeground=t['text'], bd=0, relief="flat")
apply_theme()
show_menu()
update_fav_star()  # açılışta yıldız rengini senkronize et
root.mainloop()

import tkinter as tk
from tkinter import font as tkfont
import time, random, sys, os, winsound, sqlite3, json, datetime

TEMALAR = {
    "koyu": {
        "BG": "#0a0a0f", "PANEL": "#13131a", "BORDER": "#1e1e2e",
        "ACCENT": "#64c8ff", "ACCENT2": "#a78bfa",
        "TEXT_DIM": "#4a4a6a", "TEXT_MID": "#8888aa", "TEXT_BRIGHT": "#e2e8f0",
        "GREEN": "#4ade80", "RED": "#f87171", "YELLOW": "#fbbf24",
        "BTN_FG_ACCENT": "#0a0a0f",
    },
    "acik": {
        "BG": "#f5f5f7", "PANEL": "#ffffff", "BORDER": "#dcdce4",
        "ACCENT": "#2563eb", "ACCENT2": "#7c3aed",
        "TEXT_DIM": "#9a9aab", "TEXT_MID": "#55556b", "TEXT_BRIGHT": "#15151f",
        "GREEN": "#16a34a", "RED": "#dc2626", "YELLOW": "#d97706",
        "BTN_FG_ACCENT": "#ffffff",
    },
}

BG = PANEL = BORDER = ACCENT = ACCENT2 = ""
TEXT_DIM = TEXT_MID = TEXT_BRIGHT = ""
GREEN = RED = YELLOW = BTN_FG_ACCENT = ""


def _uygula_tema(ad):
    global BG, PANEL, BORDER, ACCENT, ACCENT2
    global TEXT_DIM, TEXT_MID, TEXT_BRIGHT, GREEN, RED, YELLOW, BTN_FG_ACCENT
    t = TEMALAR.get(ad, TEMALAR["koyu"])
    BG, PANEL, BORDER = t["BG"], t["PANEL"], t["BORDER"]
    ACCENT, ACCENT2 = t["ACCENT"], t["ACCENT2"]
    TEXT_DIM, TEXT_MID, TEXT_BRIGHT = t["TEXT_DIM"], t["TEXT_MID"], t["TEXT_BRIGHT"]
    GREEN, RED, YELLOW = t["GREEN"], t["RED"], t["YELLOW"]
    BTN_FG_ACCENT = t["BTN_FG_ACCENT"]


_uygula_tema("koyu")


def _veri_yolu():
    base = os.path.join(os.path.expanduser("~"), ".hizliyaz")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "veri.db")


class VeriTabani:

    def __init__(self):
        self.yol = _veri_yolu()
        self.con = sqlite3.connect(self.yol)
        self.con.execute("PRAGMA journal_mode=WAL")
        self._olustur()

    def _olustur(self):
        c = self.con
        c.execute("""
            CREATE TABLE IF NOT EXISTS oturumlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT NOT NULL,
                seviye_idx INTEGER,
                seviye_ad TEXT,
                mod TEXT,
                hiz INTEGER,
                dogruluk INTEGER,
                hata INTEGER,
                sure REAL,
                karakter_sayisi INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS harf_hatalari (
                harf TEXT PRIMARY KEY,
                hata_sayisi INTEGER NOT NULL DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS ayarlar (
                anahtar TEXT PRIMARY KEY,
                deger TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS rekorlar (
                seviye_idx INTEGER PRIMARY KEY,
                en_iyi_hiz INTEGER NOT NULL DEFAULT 0,
                en_iyi_dogruluk INTEGER NOT NULL DEFAULT 0,
                tarih TEXT
            )
        """)
        c.commit()

    def ayar_al(self, anahtar, varsayilan=None):
        try:
            row = self.con.execute("SELECT deger FROM ayarlar WHERE anahtar=?", (anahtar,)).fetchone()
            return row[0] if row else varsayilan
        except Exception:
            return varsayilan

    def ayar_kaydet(self, anahtar, deger):
        try:
            self.con.execute(
                "INSERT INTO ayarlar (anahtar, deger) VALUES (?, ?) "
                "ON CONFLICT(anahtar) DO UPDATE SET deger=excluded.deger",
                (anahtar, str(deger)))
            self.con.commit()
        except Exception:
            pass

    def oturum_kaydet(self, seviye_idx, seviye_ad, mod, hiz, dogruluk, hata, sure, karakter_sayisi):
        try:
            self.con.execute(
                "INSERT INTO oturumlar (tarih, seviye_idx, seviye_ad, mod, hiz, dogruluk, hata, sure, karakter_sayisi) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (datetime.datetime.now().isoformat(), seviye_idx, seviye_ad, mod, hiz, dogruluk, hata, sure, karakter_sayisi))
            self.con.commit()
        except Exception:
            pass

    def son_oturumlar(self, limit=30):
        try:
            return self.con.execute(
                "SELECT tarih, seviye_ad, mod, hiz, dogruluk, hata, sure FROM oturumlar "
                "ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        except Exception:
            return []

    def hiz_serisi(self, limit=50):
        try:
            rows = self.con.execute(
                "SELECT hiz FROM oturumlar ORDER BY id ASC LIMIT ?", (limit,)).fetchall()
            return [r[0] for r in rows]
        except Exception:
            return []

    def rekor_al(self, seviye_idx):
        try:
            row = self.con.execute(
                "SELECT en_iyi_hiz, en_iyi_dogruluk FROM rekorlar WHERE seviye_idx=?",
                (seviye_idx,)).fetchone()
            return row if row else (0, 0)
        except Exception:
            return (0, 0)

    def rekor_guncelle(self, seviye_idx, hiz, dogruluk):
        try:
            mevcut_hiz, _ = self.rekor_al(seviye_idx)
            if hiz > mevcut_hiz:
                self.con.execute(
                    "INSERT INTO rekorlar (seviye_idx, en_iyi_hiz, en_iyi_dogruluk, tarih) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(seviye_idx) DO UPDATE SET en_iyi_hiz=excluded.en_iyi_hiz, "
                    "en_iyi_dogruluk=excluded.en_iyi_dogruluk, tarih=excluded.tarih",
                    (seviye_idx, hiz, dogruluk, datetime.datetime.now().isoformat()))
                self.con.commit()
                return True
            return False
        except Exception:
            return False

    def tum_rekorlar(self):
        try:
            rows = self.con.execute("SELECT seviye_idx, en_iyi_hiz, en_iyi_dogruluk FROM rekorlar").fetchall()
            return {r[0]: (r[1], r[2]) for r in rows}
        except Exception:
            return {}

    def harf_hata_ekle(self, harf):
        try:
            self.con.execute(
                "INSERT INTO harf_hatalari (harf, hata_sayisi) VALUES (?, 1) "
                "ON CONFLICT(harf) DO UPDATE SET hata_sayisi = hata_sayisi + 1",
                (harf,))
            self.con.commit()
        except Exception:
            pass

    def harf_hatalari_sirali(self, limit=10):
        try:
            return self.con.execute(
                "SELECT harf, hata_sayisi FROM harf_hatalari ORDER BY hata_sayisi DESC LIMIT ?",
                (limit,)).fetchall()
        except Exception:
            return []

    def pratik_gunleri(self):
        try:
            rows = self.con.execute(
                "SELECT DISTINCT date(tarih) FROM oturumlar ORDER BY date(tarih) DESC").fetchall()
            return [r[0] for r in rows]
        except Exception:
            return []

    def streak_hesapla(self):
        gunler = self.pratik_gunleri()
        if not gunler:
            return 0
        gun_set = {datetime.date.fromisoformat(g) for g in gunler}
        bugun = datetime.date.today()
        streak = 0
        gun = bugun
        if bugun not in gun_set:
            gun = bugun - datetime.timedelta(days=1)
        while gun in gun_set:
            streak += 1
            gun -= datetime.timedelta(days=1)
        return streak

SEVIYELER = [
    {"ad": "1 — Temel Harfler",      "tip": "harf",    "chars": "asdf jkl;", "uzunluk": 20},
    {"ad": "2 — Sol El",             "tip": "harf",    "chars": "asdfgqwert", "uzunluk": 25},
    {"ad": "3 — Sağ El",             "tip": "harf",    "chars": "hjkl;yuiop", "uzunluk": 25},
    {"ad": "4 — İki El",             "tip": "harf",    "chars": "asdfghjkl;", "uzunluk": 30},
    {"ad": "5 — Büyük Harf",         "tip": "harf",    "chars": "AaBbCcDdEeFf", "uzunluk": 30},
    {"ad": "6 — Rakamlar",           "tip": "harf",    "chars": "1234567890", "uzunluk": 30},
    {"ad": "7 — Noktalama",          "tip": "harf",    "chars": ".,;:!?", "uzunluk": 25},
    {"ad": "8 — Kısa Kelimeler",     "tip": "kelime",  "kelimeler": ["al","ver","git","gel","bak","yaz","oku","bil","gör","tut"], "uzunluk": 40},
    {"ad": "9 — Orta Kelimeler",     "tip": "kelime",  "kelimeler": ["hızlı","doğru","klavye","yazma","pratik","tekrar","başar","öğren","geliş","çalış"], "uzunluk": 50},
    {"ad": "10 — Uzun Kelimeler",    "tip": "kelime",  "kelimeler": ["bilgisayar","programlama","geliştirme","mükemmellik","başarılarım","öğreniyorum","çalışıyorum"], "uzunluk": 60},
    {"ad": "11 — Kısayollar",        "tip": "kisayol", "kisayollar": ["Ctrl+C","Ctrl+V","Ctrl+Z","Ctrl+X","Ctrl+S","Ctrl+A","Alt+F4","Ctrl+W"], "uzunluk": 40},
    {"ad": "12 — Terminal",          "tip": "kelime",  "kelimeler": ["ls -la","cd ..","grep -r","git push","pip install","mkdir -p","chmod +x","sudo apt"], "uzunluk": 60},
    {"ad": "13 — Türkçe Cümleler",   "tip": "cumle",   "uzunluk": 70},
    {"ad": "14 — İngilizce Mix",     "tip": "kelime",  "kelimeler": ["function","variable","import","return","class","object","method","string","boolean","integer"], "uzunluk": 70},
    {"ad": "15 — Usta Meydan Okuma", "tip": "cumle",   "uzunluk": 100},
    {"ad": "16 — Türkçe Karakterler", "tip": "tr_karakter", "uzunluk": 35},
]

TR_KELIMELER = [
    "çiçek", "şeker", "ağaç", "üzüm", "gözlük", "ışık", "çocuk", "şişe",
    "öğretmen", "güneş", "gül", "çay", "şehir", "ağır", "üç", "ödev",
    "çamur", "şarkı", "ığdır", "öykü", "çatı", "şahin", "ağız", "üstün",
    "gök", "çorba", "şaka", "ağla", "üzgün", "öpücük",
]

CUMLELER_TR = [
    "Hız ve doğruluk birlikte gelişir biri olmadan diğeri eksik kalır.",
    "Klavye bir enstrümandır onu çalmayı öğrenmek zaman alır.",
    "Her gün biraz daha hızlı yazmak büyük bir fark yaratır.",
    "Parmaklarını doğru konumlandır geri kalanı kendiliğinden gelir.",
    "On parmak yazma tekniğini öğrenen kimse pişman olmaz.",
    "Ritim bulmak hız kazanmaktan daha önemlidir.",
    "Doğruluk yüzde doksanın altına düştüğünde yavaşla.",
    "Sabah on dakika pratik akşam fark edilir ilerleme demektir.",
]

OZEL_METINLER = []


def metin_uret(seviye):
    tip = seviye["tip"]
    uzunluk = seviye["uzunluk"]

    if tip == "harf":
        chars = seviye["chars"].replace(" ", "")
        parcalar = []
        while sum(len(p) for p in parcalar) < uzunluk:
            n = random.randint(2, 5)
            parcalar.append("".join(random.choice(chars) for _ in range(n)))
        return " ".join(parcalar)[:uzunluk].strip()

    if tip == "kelime":
        kelimeler = seviye["kelimeler"]
        secilen = []
        while sum(len(k) for k in secilen) + len(secilen) < uzunluk:
            secilen.append(random.choice(kelimeler))
        return " ".join(secilen)

    if tip == "kisayol":
        kisayollar = seviye["kisayollar"]
        secilen = []
        while sum(len(k) for k in secilen) + len(secilen) < uzunluk:
            secilen.append(random.choice(kisayollar))
        return " ".join(secilen)

    if tip == "tr_karakter":
        secilen = []
        while sum(len(k) for k in secilen) + len(secilen) < uzunluk:
            secilen.append(random.choice(TR_KELIMELER))
        return " ".join(secilen)

    if tip == "cumle":
        if OZEL_METINLER:
            return random.choice(OZEL_METINLER)
        return random.choice(CUMLELER_TR)

    return ""


def ses_dogru():
    try:
        winsound.Beep(1200, 40)
    except Exception:
        pass


def ses_yanlis():
    try:
        winsound.Beep(300, 80)
    except Exception:
        pass


class App:
    def __init__(self):
        self.db = VeriTabani()

        tema = self.db.ayar_al("tema", "koyu")
        _uygula_tema(tema)
        self.tema_adi = tema
        self.font_boyutu = int(self.db.ayar_al("font_boyutu", 15))

        self.root = tk.Tk()
        self.root.title("HızlıYaz")
        self.root.configure(bg=BG)
        self.root.geometry("960x640")
        self.root.minsize(800, 560)

        icon_path = self._res("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self._fonts()
        self.mevcut_seviye = 0
        self.tamamlanan = set()
        self._menu()
        self.root.mainloop()

    def _res(self, name):
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, name)

    def _fonts(self):
        b = self.font_boyutu
        self.fm = tkfont.Font(family="Consolas", size=b)
        self.fm_lg = tkfont.Font(family="Consolas", size=b + 2, weight="bold")
        self.fu = tkfont.Font(family="Segoe UI", size=11)
        self.fu_sm = tkfont.Font(family="Segoe UI", size=9)
        self.fu_lg = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.f_title = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.f_stat = tkfont.Font(family="Consolas", size=24, weight="bold")

    def _temizle(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _tema_degistir(self, ad):
        _uygula_tema(ad)
        self.tema_adi = ad
        self.db.ayar_kaydet("tema", ad)
        self.root.configure(bg=BG)
        self._ayarlar()

    def _font_degistir(self, delta):
        yeni = max(11, min(24, self.font_boyutu + delta))
        if yeni == self.font_boyutu:
            return
        self.font_boyutu = yeni
        self.db.ayar_kaydet("font_boyutu", yeni)
        self._fonts()
        self._ayarlar()

    def _btn(self, parent, text, cmd, accent=False, sm=False):
        bg = ACCENT if accent else PANEL
        fg = BTN_FG_ACCENT if accent else TEXT_MID
        hbg = "#7dd3fc" if accent else BORDER
        f = self.fu_sm if sm else self.fu
        b = tk.Label(parent, text=text, font=f, bg=bg, fg=fg,
                     padx=14, pady=7 if not sm else 4,
                     cursor="hand2", relief="flat",
                     highlightthickness=1 if not accent else 0,
                     highlightbackground=BORDER)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(bg=hbg))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _menu(self):
        self._temizle()

        nav = tk.Frame(self.root, bg=PANEL, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        tk.Label(nav, text="HızlıYaz", font=self.fu_lg, bg=PANEL, fg=ACCENT).pack(side="left", padx=20, pady=12)

        streak = self.db.streak_hesapla()
        if streak > 0:
            tk.Label(nav, text=f"{streak} gün", font=self.fu_sm, bg=PANEL, fg=YELLOW).pack(side="left", padx=(0, 4))

        nav_sag = tk.Frame(nav, bg=PANEL)
        nav_sag.pack(side="right", padx=16, pady=8)
        for etiket, cmd in [
            ("Geri Sayım", self._geri_sayim_baslat),
            ("Geçmiş", self._gecmis_ekrani),
            ("Hata Analizi", self._hata_analizi_ekrani),
            ("Ayarlar", self._ayarlar),
        ]:
            self._btn(nav_sag, etiket, cmd, sm=True).pack(side="left", padx=4)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=40, pady=24)

        sol = tk.Frame(body, bg=BG)
        sol.pack(side="left", fill="y")

        tk.Label(sol, text="Alıştırmalar", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 12))

        canvas = tk.Canvas(sol, bg=BG, highlightthickness=0, width=320)
        canvas.pack(side="left", fill="both", expand=True)
        scroll = tk.Scrollbar(sol, orient="vertical", command=canvas.yview)
        scroll.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scroll.set)

        liste = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=liste, anchor="nw")

        rekorlar = self.db.tum_rekorlar()
        for i, sev in enumerate(SEVIYELER):
            tamamlandi = i in self.tamamlanan
            aktif = i == self.mevcut_seviye
            kilidi_acik = i <= self.mevcut_seviye

            satirbg = PANEL if aktif else BG
            fg = TEXT_BRIGHT if kilidi_acik else TEXT_DIM

            satir = tk.Frame(liste, bg=satirbg, pady=6,
                             highlightthickness=1,
                             highlightbackground=ACCENT if aktif else BORDER)
            satir.pack(fill="x", pady=2, padx=2)

            ikon = "✓" if tamamlandi else ("▶" if aktif else ("○" if kilidi_acik else "x"))
            ikon_fg = GREEN if tamamlandi else (ACCENT if aktif else fg)

            tk.Label(satir, text=ikon, font=self.fu, bg=satirbg, fg=ikon_fg, width=2).pack(side="left", padx=(8, 4))
            tk.Label(satir, text=sev["ad"], font=self.fu_sm, bg=satirbg, fg=fg).pack(side="left", padx=4)

            if i in rekorlar:
                rekor_hiz, _ = rekorlar[i]
                tk.Label(satir, text=f"En iyi: {rekor_hiz}", font=self.fu_sm, bg=satirbg, fg=YELLOW).pack(side="right", padx=(4, 10))

            if kilidi_acik:
                idx = i
                satir.bind("<Button-1>", lambda e, x=idx: self._baslat_alistirma(x))
                for child in satir.winfo_children():
                    child.bind("<Button-1>", lambda e, x=idx: self._baslat_alistirma(x))
                satir.config(cursor="hand2")

        liste.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y", padx=24)

        sag = tk.Frame(body, bg=BG)
        sag.pack(side="left", fill="both", expand=True)

        tk.Label(sag, text="Hızlı Test", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 8))
        tk.Label(sag, text="Tüm seviyeleri tamamlayınca aktif olur", font=self.fu_sm, bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 12))

        toplam_seviye = len(SEVIYELER)
        hizli_fg = TEXT_MID if len(self.tamamlanan) == toplam_seviye else TEXT_DIM
        hizli_f = self._btn(sag, "Hızlı Yazma Testini Başlat",
                            self._hizli_test if len(self.tamamlanan) == toplam_seviye else lambda: None,
                            accent=len(self.tamamlanan) == toplam_seviye)
        hizli_f.pack(anchor="w")

        tk.Frame(sag, bg=BORDER, height=1).pack(fill="x", pady=20)

        tk.Label(sag, text="Kendi Metinlerin", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 8))
        tk.Label(sag, text="Her satıra bir metin — boş bırakırsan hazır metinler kullanılır", font=self.fu_sm, bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 8))

        self.ozel_text = tk.Text(sag, height=6, font=self.fm,
                                 bg=PANEL, fg=TEXT_BRIGHT, insertbackground=ACCENT,
                                 relief="flat", padx=12, pady=10, wrap="word",
                                 highlightthickness=1, highlightbackground=BORDER)
        self.ozel_text.pack(fill="x")
        if OZEL_METINLER:
            self.ozel_text.insert("1.0", "\n".join(OZEL_METINLER))

        self._btn(sag, "Kaydet", self._kaydet_ozel, sm=True).pack(anchor="w", pady=(8, 0))

    def _kaydet_ozel(self):
        global OZEL_METINLER
        raw = self.ozel_text.get("1.0", "end-1c").strip()
        OZEL_METINLER = [l.strip() for l in raw.splitlines() if l.strip()]

    def _geri_buton(self, parent):
        geri = tk.Label(parent, text="← Geri", font=self.fu_sm, bg=PANEL, fg=TEXT_DIM, cursor="hand2")
        geri.pack(side="left", padx=16, pady=14)
        geri.bind("<Button-1>", lambda e: self._menu())

    def _gecmis_ekrani(self):
        self._temizle()

        nav = tk.Frame(self.root, bg=PANEL, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        self._geri_buton(nav)
        tk.Label(nav, text="İstatistik Geçmişi", font=self.fu_lg, bg=PANEL, fg=TEXT_BRIGHT).pack(side="left", padx=8)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=40, pady=20)

        oturumlar = self.db.son_oturumlar(limit=20)

        if not oturumlar:
            tk.Label(body, text="Henüz kayıtlı bir oturum yok. Bir alıştırma bitir, burada görünecek.",
                    font=self.fu, bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=40)
            return

        hiz_serisi = self.db.hiz_serisi(limit=50)
        tk.Label(body, text="Hız İlerlemesi (DAK/KW)", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 8))
        self._cizgi_grafik(body, hiz_serisi, yukseklik=140)

        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=18)

        tk.Label(body, text="Son Oturumlar", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 10))

        tablo_wrap = tk.Frame(body, bg=BG)
        tablo_wrap.pack(fill="both", expand=True)

        canvas = tk.Canvas(tablo_wrap, bg=BG, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scroll = tk.Scrollbar(tablo_wrap, orient="vertical", command=canvas.yview)
        scroll.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scroll.set)

        liste = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=liste, anchor="nw", width=860)

        basliklar = ["Tarih", "Seviye", "Hız", "Doğruluk", "Hata", "Süre"]
        baslik_f = tk.Frame(liste, bg=PANEL)
        baslik_f.pack(fill="x", pady=(0, 2))
        genislikler = [16, 26, 8, 10, 8, 8]
        for b, g in zip(basliklar, genislikler):
            tk.Label(baslik_f, text=b, font=self.fu_sm, bg=PANEL, fg=TEXT_DIM, width=g, anchor="w").pack(side="left", padx=6, pady=6)

        for tarih, sev_ad, mod, hiz, dogruluk, hata, sure in oturumlar:
            try:
                t = datetime.datetime.fromisoformat(tarih).strftime("%d.%m %H:%M")
            except Exception:
                t = tarih[:16]
            satir = tk.Frame(liste, bg=BG)
            satir.pack(fill="x")
            renk_d = GREEN if dogruluk >= 90 else YELLOW if dogruluk >= 70 else RED
            for val, g, renk in [
                (t, genislikler[0], TEXT_MID),
                (sev_ad or "Hızlı Test", genislikler[1], TEXT_MID),
                (str(hiz), genislikler[2], ACCENT),
                (f"%{dogruluk}", genislikler[3], renk_d),
                (str(hata), genislikler[4], TEXT_MID),
                (f"{sure:.1f}s", genislikler[5], TEXT_MID),
            ]:
                tk.Label(satir, text=val, font=self.fu_sm, bg=BG, fg=renk, width=g, anchor="w").pack(side="left", padx=6, pady=4)

        liste.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def _cizgi_grafik(self, parent, degerler, yukseklik=140):
        """Basit bir Canvas tabanlı çizgi grafiği çizer (ekstra kütüphane gerektirmez)."""
        cv = tk.Canvas(parent, bg=PANEL, height=yukseklik,
                       highlightthickness=1, highlightbackground=BORDER)
        cv.pack(fill="x")

        if len(degerler) < 2:
            cv.create_text(10, yukseklik // 2, text="Grafik için en az 2 oturum gerekli",
                           fill=TEXT_DIM, font=self.fu_sm, anchor="w")
            return

        def cizimi_yap(event=None):
            cv.delete("all")
            w = cv.winfo_width() or 800
            h = yukseklik
            pad = 24
            vmax = max(degerler) or 1
            vmin = min(degerler)
            span = max(vmax - vmin, 1)
            n = len(degerler)
            stepx = (w - 2 * pad) / max(n - 1, 1)

            for frac in (0, 0.5, 1):
                y = pad + (1 - frac) * (h - 2 * pad)
                cv.create_line(pad, y, w - pad, y, fill=BORDER)
                cv.create_text(w - pad, y, text=str(int(vmin + frac * span)),
                               fill=TEXT_DIM, font=self.fu_sm, anchor="e")

            noktalar = []
            for i, v in enumerate(degerler):
                x = pad + i * stepx
                y = pad + (1 - (v - vmin) / span) * (h - 2 * pad)
                noktalar.append((x, y))

            for i in range(len(noktalar) - 1):
                cv.create_line(*noktalar[i], *noktalar[i + 1], fill=ACCENT, width=2)
            for x, y in noktalar:
                cv.create_oval(x - 3, y - 3, x + 3, y + 3, fill=ACCENT, outline="")

        cv.bind("<Configure>", cizimi_yap)
        cv.after(10, cizimi_yap)

    def _hata_analizi_ekrani(self):
        self._temizle()

        nav = tk.Frame(self.root, bg=PANEL, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        self._geri_buton(nav)
        tk.Label(nav, text="Hata Analizi", font=self.fu_lg, bg=PANEL, fg=TEXT_BRIGHT).pack(side="left", padx=8)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=40, pady=24)

        hatalar = self.db.harf_hatalari_sirali(limit=12)

        if not hatalar:
            tk.Label(body, text="Henüz yeterli hata verisi yok. Birkaç alıştırma yaptıkça burada\n"
                                "hangi harflerde en çok zorlandığını görebileceksin.",
                    font=self.fu, bg=BG, fg=TEXT_DIM, justify="left").pack(anchor="w", pady=40)
            return

        tk.Label(body, text="En çok yanlış yaptığın harfler", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 16))

        maks = max(h for _, h in hatalar) or 1
        for harf, sayi in hatalar:
            satir = tk.Frame(body, bg=BG)
            satir.pack(fill="x", pady=4)

            gosterilen = harf if harf != " " else "(boşluk)"
            tk.Label(satir, text=gosterilen, font=self.fm_lg, bg=BG, fg=TEXT_BRIGHT, width=10, anchor="w").pack(side="left")

            bar_wrap = tk.Frame(satir, bg=PANEL, height=20)
            bar_wrap.pack(side="left", fill="x", expand=True, padx=(8, 8))
            bar_wrap.pack_propagate(False)
            oran = sayi / maks
            renk = RED if oran > 0.66 else YELLOW if oran > 0.33 else ACCENT
            bar = tk.Frame(bar_wrap, bg=renk)
            bar.place(relx=0, rely=0, relwidth=oran, relheight=1)

            tk.Label(satir, text=str(sayi), font=self.fu_sm, bg=BG, fg=TEXT_DIM, width=4).pack(side="left")

    def _ayarlar(self):
        self._temizle()

        nav = tk.Frame(self.root, bg=PANEL, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        self._geri_buton(nav)
        tk.Label(nav, text="Ayarlar", font=self.fu_lg, bg=PANEL, fg=TEXT_BRIGHT).pack(side="left", padx=8)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=40, pady=24)

        tk.Label(body, text="Tema", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 10))
        tema_f = tk.Frame(body, bg=BG)
        tema_f.pack(anchor="w", pady=(0, 24))
        for ad, etiket in [("koyu", "Koyu Mod"), ("acik", "Açık Mod")]:
            secili = self.tema_adi == ad
            self._btn(tema_f, etiket, lambda a=ad: self._tema_degistir(a), accent=secili).pack(side="left", padx=(0, 8))

        tk.Label(body, text="Yazı Tipi Büyüklüğü", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 10))
        font_f = tk.Frame(body, bg=BG)
        font_f.pack(anchor="w", pady=(0, 24))
        self._btn(font_f, "A-", lambda: self._font_degistir(-1)).pack(side="left", padx=(0, 8))
        tk.Label(font_f, text=str(self.font_boyutu), font=self.fu_lg, bg=BG, fg=ACCENT, width=3).pack(side="left")
        self._btn(font_f, "A+", lambda: self._font_degistir(1)).pack(side="left", padx=(8, 0))
        tk.Label(font_f, text="  Önizleme: hızlı yazmayı öğreniyorum", font=self.fm, bg=BG, fg=TEXT_MID).pack(side="left", padx=16)

        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=8)
        tk.Label(body, text="Veriler", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(16, 10))
        tk.Label(body, text=f"İstatistikler şurada saklanıyor: {self.db.yol}",
                font=self.fu_sm, bg=BG, fg=TEXT_DIM).pack(anchor="w")

    def _geri_sayim_baslat(self, sure=60):
        self._temizle()

        nav = tk.Frame(self.root, bg=PANEL, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        self._geri_buton(nav)
        tk.Label(nav, text="Geri Sayım Modu", font=self.fu_lg, bg=PANEL, fg=TEXT_BRIGHT).pack(side="left", padx=8)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=40, pady=40)

        tk.Label(body, text=f"{sure} saniyede kaç kelime yazabilirsin?", font=self.f_title, bg=BG, fg=TEXT_BRIGHT).pack(pady=(20, 8))
        tk.Label(body, text="Süre yazmaya başladığın an işlemeye başlar. Hazır olduğunda yazmaya başla.",
                font=self.fu, bg=BG, fg=TEXT_DIM).pack(pady=(0, 30))

        self._btn(body, "▶  Başla", lambda: self._geri_sayim_yazma_ekrani(sure)).pack()

    def _geri_sayim_yazma_ekrani(self, toplam_sure):
        self._temizle()

        self.gs_kalan_metin_havuzu = (OZEL_METINLER or CUMLELER_TR) * 6
        self.gs_hedef_havuz = " ".join(random.sample(self.gs_kalan_metin_havuzu, len(self.gs_kalan_metin_havuzu)))
        self.gs_yazilan_toplam = ""
        self.gs_toplam_sure = toplam_sure
        self.gs_baslangic = None
        self.gs_bitti = False
        self.gs_hata_sayisi = 0
        self.gs_dogru_karakter = 0
        self.gs_toplam_karakter = 0

        nav = tk.Frame(self.root, bg=PANEL, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        self._geri_buton(nav)
        tk.Label(nav, text="Geri Sayım Modu", font=self.fu_lg, bg=PANEL, fg=TEXT_BRIGHT).pack(side="left", padx=8)

        stat_f = tk.Frame(self.root, bg=BG)
        stat_f.pack(fill="x", padx=40, pady=(20, 0))
        self.gs_sure_lbl = self._stat(stat_f, "KALAN SÜRE", f"{toplam_sure}s")
        self.gs_kelime_lbl = self._stat(stat_f, "KELİME", "0")
        self.gs_dogru_lbl = self._stat(stat_f, "DOĞRULUK", "—")

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=40, pady=16)

        metin_wrap = tk.Frame(self.root, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        metin_wrap.pack(fill="x", padx=40)

        self.gs_metin_c = tk.Text(metin_wrap, font=self.fm_lg, bg=PANEL, fg=TEXT_DIM,
                                  relief="flat", padx=20, pady=16, wrap="word",
                                  cursor="arrow", state="normal", height=4)
        self.gs_metin_c.pack(fill="x")
        self.gs_metin_c.insert("1.0", self.gs_hedef_havuz)
        self.gs_metin_c.tag_config("done", fg=GREEN)
        self.gs_metin_c.tag_config("current", fg=ACCENT, underline=True)
        self.gs_metin_c.tag_config("wrong", fg=RED, background="#2d0f0f")
        self.gs_metin_c.tag_config("pending", fg=TEXT_DIM)
        self.gs_metin_c.config(state="disabled")

        giris_f = tk.Frame(self.root, bg=BG)
        giris_f.pack(fill="x", padx=40, pady=(16, 0))
        tk.Label(giris_f, text="Buraya yaz →", font=self.fu_sm, bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 6))

        self.gs_giris = tk.Text(giris_f, height=3, font=self.fm,
                                bg=PANEL, fg=TEXT_BRIGHT, insertbackground=ACCENT,
                                relief="flat", padx=16, pady=12, wrap="word",
                                highlightthickness=1, highlightbackground=BORDER,
                                highlightcolor=ACCENT)
        self.gs_giris.pack(fill="x")
        self.gs_giris.bind("<KeyRelease>", lambda e: self._geri_sayim_kontrol())
        self.gs_giris.focus_set()

        self._geri_sayim_tick()

    def _geri_sayim_tick(self):
        if self.gs_bitti:
            return
        if self.gs_baslangic is not None:
            gecen = time.time() - self.gs_baslangic
            kalan = max(0, self.gs_toplam_sure - gecen)
            self.gs_sure_lbl.config(text=f"{kalan:.0f}s")
            if kalan <= 0:
                self._geri_sayim_bitis()
                return
        self.root.after(200, self._geri_sayim_tick)

    def _geri_sayim_kontrol(self):
        if self.gs_bitti:
            return
        yazilan = self.gs_giris.get("1.0", "end-1c")
        if yazilan and self.gs_baslangic is None:
            self.gs_baslangic = time.time()

        n = len(yazilan)
        hedef = self.gs_hedef_havuz
        yanlis = {i for i, c in enumerate(yazilan) if i < len(hedef) and c != hedef[i]}

        yeni_hata_harfi = None
        if n > self.gs_toplam_karakter:
            if n - 1 < len(hedef) and yazilan[-1] != hedef[n - 1]:
                self.gs_hata_sayisi += 1
                self.root.after(0, ses_yanlis)
                yeni_hata_harfi = hedef[n - 1]
            else:
                self.root.after(0, ses_dogru)
        self.gs_toplam_karakter = n

        self.gs_metin_c.config(state="normal")
        for tag in ("done", "current", "wrong", "pending"):
            self.gs_metin_c.tag_remove(tag, "1.0", "end")
        for i in range(min(len(hedef), n + 200)):
            s, e = f"1.{i}", f"1.{i+1}"
            if i < n:
                self.gs_metin_c.tag_add("wrong" if i in yanlis else "done", s, e)
            elif i == n:
                self.gs_metin_c.tag_add("current", s, e)
            else:
                self.gs_metin_c.tag_add("pending", s, e)
        self.gs_metin_c.config(state="disabled")

        if yeni_hata_harfi is not None:
            self.db.harf_hata_ekle(yeni_hata_harfi)

        kelime = len(yazilan.split())
        self.gs_kelime_lbl.config(text=str(kelime))
        dogru_n = sum(1 for i, c in enumerate(yazilan) if i < len(hedef) and c == hedef[i])
        self.gs_dogru_karakter = dogru_n
        if n > 0:
            oran = int(dogru_n / n * 100)
            renk = GREEN if oran >= 90 else YELLOW if oran >= 70 else RED
            self.gs_dogru_lbl.config(text=f"%{oran}", fg=renk)

        if n >= len(hedef) - 50:
            self.gs_hedef_havuz += " " + " ".join(random.sample(self.gs_kalan_metin_havuzu, 5))

    def _geri_sayim_bitis(self):
        self.gs_bitti = True
        self.gs_giris.config(state="disabled")

        yazilan = self.gs_giris.get("1.0", "end-1c")
        kelime = len(yazilan.split())
        oran = int(self.gs_dogru_karakter / max(len(yazilan), 1) * 100)

        self.db.oturum_kaydet(None, "Geri Sayım (60s)", "geri_sayim", kelime, oran,
                              self.gs_hata_sayisi, self.gs_toplam_sure, len(yazilan))

        overlay = tk.Frame(self.root, bg=BG)
        overlay.pack(pady=20, padx=40, fill="x")
        tk.Frame(overlay, bg=BORDER, height=1).pack(fill="x", pady=(0, 16))

        tk.Label(overlay, text="Süre Doldu", font=self.f_title, bg=BG, fg=ACCENT).pack(pady=(0, 12))

        row = tk.Frame(overlay, bg=BG)
        row.pack()
        renk_d = GREEN if oran >= 90 else YELLOW if oran >= 70 else RED
        for val, lbl, renk in [
            (str(kelime), "KELİME", ACCENT),
            (f"%{oran}", "DOĞRULUK", renk_d),
            (str(self.gs_hata_sayisi), "HATA", RED if self.gs_hata_sayisi > 5 else GREEN),
        ]:
            blk = tk.Frame(row, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
            blk.pack(side="left", padx=8, ipadx=20, ipady=10)
            tk.Label(blk, text=val, font=self.f_stat, bg=PANEL, fg=renk).pack()
            tk.Label(blk, text=lbl, font=self.fu_sm, bg=PANEL, fg=TEXT_DIM).pack()

        btn_row = tk.Frame(overlay, bg=BG)
        btn_row.pack(pady=(20, 0))
        self._btn(btn_row, "Tekrar", lambda: self._geri_sayim_yazma_ekrani(self.gs_toplam_sure), accent=True).pack(side="left", padx=6)
        self._btn(btn_row, "Ana Menü", self._menu).pack(side="left", padx=6)

    def _baslat_alistirma(self, idx):
        self.mevcut_seviye = idx
        sev = SEVIYELER[idx]
        self._yazma_ekrani(metin_uret(sev), mod="alistirma", seviye_idx=idx)

    def _hizli_test(self):
        if OZEL_METINLER:
            metin = random.choice(OZEL_METINLER)
        else:
            metin = random.choice(CUMLELER_TR)
        self._yazma_ekrani(metin, mod="test")

    def _yazma_ekrani(self, hedef, mod, seviye_idx=None):
        self._temizle()

        self.hedef = hedef
        self.baslangic = None
        self.bitti = False
        self.son_uzunluk = 0

        nav = tk.Frame(self.root, bg=PANEL, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        geri = tk.Label(nav, text="← Geri", font=self.fu_sm, bg=PANEL, fg=TEXT_DIM, cursor="hand2")
        geri.pack(side="left", padx=16, pady=14)
        geri.bind("<Button-1>", lambda e: self._menu())

        baslik = SEVIYELER[seviye_idx]["ad"] if seviye_idx is not None else "Hızlı Test"
        tk.Label(nav, text=baslik, font=self.fu_lg, bg=PANEL, fg=TEXT_BRIGHT).pack(side="left", padx=8)

        stat_f = tk.Frame(self.root, bg=BG)
        stat_f.pack(fill="x", padx=40, pady=(20, 0))

        self.hiz_lbl = self._stat(stat_f, "DAK/KW", "—")
        self.dogru_lbl = self._stat(stat_f, "DOĞRULUK", "—")
        self.sure_lbl = self._stat(stat_f, "SÜRE", "0s")
        self.hata_lbl = self._stat(stat_f, "HATA", "0")

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=40, pady=16)

        metin_wrap = tk.Frame(self.root, bg=PANEL,
                              highlightthickness=1, highlightbackground=BORDER)
        metin_wrap.pack(fill="x", padx=40)

        self.metin_c = tk.Text(metin_wrap, font=self.fm_lg, bg=PANEL, fg=TEXT_DIM,
                               relief="flat", padx=20, pady=16, wrap="word",
                               cursor="arrow", state="normal", height=4)
        self.metin_c.pack(fill="x")
        self.metin_c.insert("1.0", self.hedef)
        self.metin_c.tag_config("done", fg=GREEN)
        self.metin_c.tag_config("current", fg=ACCENT, underline=True)
        self.metin_c.tag_config("wrong", fg=RED, background="#2d0f0f")
        self.metin_c.tag_config("pending", fg=TEXT_DIM)
        self.metin_c.config(state="disabled")
        self._renkle(0, set())

        giris_f = tk.Frame(self.root, bg=BG)
        giris_f.pack(fill="x", padx=40, pady=(16, 0))

        tk.Label(giris_f, text="Buraya yaz →", font=self.fu_sm, bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 6))

        self.giris = tk.Text(giris_f, height=3, font=self.fm,
                             bg=PANEL, fg=TEXT_BRIGHT, insertbackground=ACCENT,
                             relief="flat", padx=16, pady=12, wrap="word",
                             highlightthickness=1, highlightbackground=BORDER,
                             highlightcolor=ACCENT)
        self.giris.pack(fill="x")
        self.giris.bind("<KeyRelease>", lambda e: self._kontrol(mod, seviye_idx))
        self.giris.focus_set()

        self._seviye_idx = seviye_idx
        self._mod = mod
        self._hata_sayisi = 0
        self._sure_tick()

    def _stat(self, parent, baslik, deger):
        f = tk.Frame(parent, bg=BG)
        f.pack(side="left", padx=(0, 32))
        lbl = tk.Label(f, text=deger, font=self.f_stat, bg=BG, fg=ACCENT)
        lbl.pack(anchor="w")
        tk.Label(f, text=baslik, font=self.fu_sm, bg=BG, fg=TEXT_DIM).pack(anchor="w")
        return lbl

    def _renkle(self, n, yanlis_pos):
        self.metin_c.config(state="normal")
        for tag in ("done", "current", "wrong", "pending"):
            self.metin_c.tag_remove(tag, "1.0", "end")
        for i in range(len(self.hedef)):
            s, e = f"1.{i}", f"1.{i+1}"
            if i < n:
                self.metin_c.tag_add("wrong" if i in yanlis_pos else "done", s, e)
            elif i == n:
                self.metin_c.tag_add("current", s, e)
            else:
                self.metin_c.tag_add("pending", s, e)
        self.metin_c.config(state="disabled")

    def _kontrol(self, mod, seviye_idx):
        if self.bitti:
            return
        yazilan = self.giris.get("1.0", "end-1c")
        if yazilan and self.baslangic is None:
            self.baslangic = time.time()

        n = len(yazilan)
        yanlis = {i for i, c in enumerate(yazilan)
                  if i < len(self.hedef) and c != self.hedef[i]}

        yeni_hata_harfi = None
        if n > self.son_uzunluk:
            if n - 1 < len(self.hedef) and yazilan[-1] != self.hedef[n - 1]:
                self._hata_sayisi += 1
                self.root.after(0, ses_yanlis)
                yeni_hata_harfi = self.hedef[n - 1]
            else:
                self.root.after(0, ses_dogru)
        self.son_uzunluk = n

        self._renkle(n, yanlis)

        if yeni_hata_harfi is not None:
            self.db.harf_hata_ekle(yeni_hata_harfi)

        if n > 0 and self.baslangic:
            gecen = time.time() - self.baslangic
            kelime = len(yazilan.split())
            hiz = int(kelime / (gecen / 60)) if gecen > 0 else 0
            self.hiz_lbl.config(text=str(hiz))

            dogru_n = sum(1 for i, c in enumerate(yazilan)
                          if i < len(self.hedef) and c == self.hedef[i])
            oran = int(dogru_n / max(n, 1) * 100)
            renk = GREEN if oran >= 90 else YELLOW if oran >= 70 else RED
            self.dogru_lbl.config(text=f"%{oran}", fg=renk)
            self.hata_lbl.config(text=str(self._hata_sayisi))

        if yazilan == self.hedef:
            self.bitti = True
            self._bitis(mod, seviye_idx)

    def _sure_tick(self):
        if self.bitti:
            return
        if self.baslangic:
            self.sure_lbl.config(text=f"{int(time.time()-self.baslangic)}s")
        self.root.after(500, self._sure_tick)

    def _bitis(self, mod, seviye_idx):
        self.giris.config(state="disabled")
        gecen = time.time() - self.baslangic
        yazilan = self.giris.get("1.0", "end-1c")
        hiz = int(len(yazilan.split()) / (gecen / 60)) if gecen > 0 else 0
        dogru = sum(1 for i, c in enumerate(yazilan)
                    if i < len(self.hedef) and c == self.hedef[i])
        oran = int(dogru / len(self.hedef) * 100)

        seviye_ad = SEVIYELER[seviye_idx]["ad"] if seviye_idx is not None else None
        self.db.oturum_kaydet(seviye_idx, seviye_ad, mod, hiz, oran, self._hata_sayisi, gecen, len(yazilan))

        yeni_rekor = False
        if seviye_idx is not None:
            yeni_rekor = self.db.rekor_guncelle(seviye_idx, hiz, oran)

        if mod == "alistirma" and seviye_idx is not None and oran >= 80:
            self.tamamlanan.add(seviye_idx)
            if seviye_idx + 1 < len(SEVIYELER):
                self.mevcut_seviye = seviye_idx + 1

        overlay = tk.Frame(self.root, bg=BG)
        overlay.pack(pady=20, padx=40, fill="x")
        tk.Frame(overlay, bg=BORDER, height=1).pack(fill="x", pady=(0, 16))

        if yeni_rekor:
            tk.Label(overlay, text="Yeni Kişisel Rekor!", font=self.fu_lg, bg=BG, fg=YELLOW).pack(pady=(0, 10))

        row = tk.Frame(overlay, bg=BG)
        row.pack()

        renk_d = GREEN if oran >= 90 else YELLOW if oran >= 70 else RED
        gec_bilgi = oran >= 80 and mod == "alistirma"

        for val, lbl, renk in [
            (f"{hiz}", "DAK/KW", ACCENT),
            (f"%{oran}", "DOĞRULUK", renk_d),
            (f"{gecen:.1f}s", "SÜRE", ACCENT2),
            (f"{self._hata_sayisi}", "HATA", RED if self._hata_sayisi > 5 else GREEN),
        ]:
            blk = tk.Frame(row, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
            blk.pack(side="left", padx=8, ipadx=20, ipady=10)
            tk.Label(blk, text=val, font=self.f_stat, bg=PANEL, fg=renk).pack()
            tk.Label(blk, text=lbl, font=self.fu_sm, bg=PANEL, fg=TEXT_DIM).pack()

        if mod == "alistirma":
            if gec_bilgi:
                msg = "Seviye Geçildi!" if seviye_idx + 1 < len(SEVIYELER) else "Tüm Seviyeler Tamamlandı!"
                tk.Label(overlay, text=msg, font=self.fu_lg, bg=BG, fg=GREEN).pack(pady=(12, 0))
            else:
                tk.Label(overlay, text="Geçmek için %80 doğruluk gerekli", font=self.fu_sm, bg=BG, fg=YELLOW).pack(pady=(12, 0))

        btn_row = tk.Frame(overlay, bg=BG)
        btn_row.pack(pady=(14, 0))
        self._btn(btn_row, "Tekrar", lambda: self._yazma_ekrani(metin_uret(SEVIYELER[seviye_idx]) if seviye_idx is not None else random.choice(OZEL_METINLER or CUMLELER_TR), mod=mod, seviye_idx=seviye_idx), accent=True).pack(side="left", padx=6)
        if mod == "alistirma" and gec_bilgi and seviye_idx + 1 < len(SEVIYELER):
            self._btn(btn_row, "Sonraki Seviye →", lambda: self._baslat_alistirma(seviye_idx + 1)).pack(side="left", padx=6)
        self._btn(btn_row, "Ana Menü", self._menu).pack(side="left", padx=6)


if __name__ == "__main__":
    App()

import tkinter as tk
from tkinter import font as tkfont
import time, random, sys, os, winsound

BG, PANEL, BORDER = "#0a0a0f", "#13131a", "#1e1e2e"
ACCENT, ACCENT2 = "#64c8ff", "#a78bfa"
TEXT_DIM, TEXT_MID, TEXT_BRIGHT = "#4a4a6a", "#8888aa", "#e2e8f0"
GREEN, RED, YELLOW = "#4ade80", "#f87171", "#fbbf24"

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
    {"ad": "15 — Meydan Okuma", "tip": "cumle",   "uzunluk": 100},
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
        self.fm = tkfont.Font(family="Consolas", size=15)
        self.fm_lg = tkfont.Font(family="Consolas", size=17, weight="bold")
        self.fu = tkfont.Font(family="Segoe UI", size=11)
        self.fu_sm = tkfont.Font(family="Segoe UI", size=9)
        self.fu_lg = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.f_title = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.f_stat = tkfont.Font(family="Consolas", size=24, weight="bold")

    def _temizle(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _btn(self, parent, text, cmd, accent=False, sm=False):
        bg = ACCENT if accent else PANEL
        fg = "#0a0a0f" if accent else TEXT_MID
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

    # ── MENÜ ──────────────────────────────────────────────────────────────
    def _menu(self):
        self._temizle()

        nav = tk.Frame(self.root, bg=PANEL, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        tk.Label(nav, text=" HızlıYaz", font=self.fu_lg, bg=PANEL, fg=ACCENT).pack(side="left", padx=20, pady=12)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=40, pady=24)

        # Sol — seviyeler
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

            ikon = "✓" if tamamlandi else ("▶" if aktif else ("○" if kilidi_acik else "🔒"))
            ikon_fg = GREEN if tamamlandi else (ACCENT if aktif else fg)

            tk.Label(satir, text=ikon, font=self.fu, bg=satirbg, fg=ikon_fg, width=2).pack(side="left", padx=(8, 4))
            tk.Label(satir, text=sev["ad"], font=self.fu_sm, bg=satirbg, fg=fg).pack(side="left", padx=4)

            if kilidi_acik:
                idx = i
                satir.bind("<Button-1>", lambda e, x=idx: self._baslat_alistirma(x))
                for child in satir.winfo_children():
                    child.bind("<Button-1>", lambda e, x=idx: self._baslat_alistirma(x))
                satir.config(cursor="hand2")

        liste.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # ayrac
        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y", padx=24)

        # Sağ — hızlı test + özel
        sag = tk.Frame(body, bg=BG)
        sag.pack(side="left", fill="both", expand=True)

        tk.Label(sag, text="Hızlı Test", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 8))
        tk.Label(sag, text="Tüm seviyeleri tamamlayınca aktif olur", font=self.fu_sm, bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 12))

        hizli_fg = TEXT_MID if len(self.tamamlanan) == 15 else TEXT_DIM
        hizli_f = self._btn(sag, " Testi Başlat",
                            self._hizli_test if len(self.tamamlanan) == 15 else lambda: None,
                            accent=len(self.tamamlanan) == 15)
        hizli_f.pack(anchor="w")

        tk.Frame(sag, bg=BORDER, height=1).pack(fill="x", pady=20)

        tk.Label(sag, text="Kendi Metinlerin", font=self.fu_lg, bg=BG, fg=TEXT_BRIGHT).pack(anchor="w", pady=(0, 8))
        tk.Label(sag, text="Her satıra bir metin boş bırakırsan hazır metinler kullanılır", font=self.fu_sm, bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 8))

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

    # ── ALISTIRMA ─────────────────────────────────────────────────────────
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

        # Nav
        nav = tk.Frame(self.root, bg=PANEL, height=48)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        geri = tk.Label(nav, text="← Geri", font=self.fu_sm, bg=PANEL, fg=TEXT_DIM, cursor="hand2")
        geri.pack(side="left", padx=16, pady=14)
        geri.bind("<Button-1>", lambda e: self._menu())

        baslik = SEVIYELER[seviye_idx]["ad"] if seviye_idx is not None else "Hızlı Test"
        tk.Label(nav, text=baslik, font=self.fu_lg, bg=PANEL, fg=TEXT_BRIGHT).pack(side="left", padx=8)

        # Stats
        stat_f = tk.Frame(self.root, bg=BG)
        stat_f.pack(fill="x", padx=40, pady=(20, 0))

        self.hiz_lbl = self._stat(stat_f, "DAK/KW", "—")
        self.dogru_lbl = self._stat(stat_f, "DOĞRULUK", "—")
        self.sure_lbl = self._stat(stat_f, "SÜRE", "0s")
        self.hata_lbl = self._stat(stat_f, "HATA", "0")

        # Hedef metin
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

        # Giriş
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

        # Ses
        if n > self.son_uzunluk:
            if n - 1 < len(self.hedef) and yazilan[-1] != self.hedef[n - 1]:
                self._hata_sayisi += 1
                self.root.after(0, ses_yanlis)
            else:
                self.root.after(0, ses_dogru)
        self.son_uzunluk = n

        self._renkle(n, yanlis)

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

        if mod == "alistirma" and seviye_idx is not None and oran >= 80:
            self.tamamlanan.add(seviye_idx)
            if seviye_idx + 1 < len(SEVIYELER):
                self.mevcut_seviye = seviye_idx + 1

        overlay = tk.Frame(self.root, bg=BG)
        overlay.pack(pady=20, padx=40, fill="x")
        tk.Frame(overlay, bg=BORDER, height=1).pack(fill="x", pady=(0, 16))

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
                msg = "✓ Seviye Geçildi!" if seviye_idx + 1 < len(SEVIYELER) else "🏆 Tüm Seviyeler Tamamlandı!"
                tk.Label(overlay, text=msg, font=self.fu_lg, bg=BG, fg=GREEN).pack(pady=(12, 0))
            else:
                tk.Label(overlay, text="Geçmek için %80 doğruluk gerekli", font=self.fu_sm, bg=BG, fg=YELLOW).pack(pady=(12, 0))

        btn_row = tk.Frame(overlay, bg=BG)
        btn_row.pack(pady=(14, 0))
        self._btn(btn_row, "⚡ Tekrar", lambda: self._yazma_ekrani(metin_uret(SEVIYELER[seviye_idx]) if seviye_idx is not None else random.choice(OZEL_METINLER or CUMLELER_TR), mod=mod, seviye_idx=seviye_idx), accent=True).pack(side="left", padx=6)
        if mod == "alistirma" and gec_bilgi and seviye_idx + 1 < len(SEVIYELER):
            self._btn(btn_row, "Sonraki Seviye →", lambda: self._baslat_alistirma(seviye_idx + 1)).pack(side="left", padx=6)
        self._btn(btn_row, "Ana Menü", self._menu).pack(side="left", padx=6)


if __name__ == "__main__":
    App()

import tkinter as tk
from tkinter import font as tkfont
import time
import random
import sys
import os

METINLER = [
    "Hız ve doğruluk birlikte gelişir, biri olmadan diğeri eksik kalır.",
    "Klavye bir enstrümandır, onu çalmayı öğrenmek zaman alır.",
    "Her gün biraz daha hızlı yazmak, büyük bir fark yaratır.",
    "Parmaklarını doğru konumlandır, geri kalanı kendiliğinden gelir.",
    "Hata yapmaktan korkma, önemli olan devam etmektir.",
    "Yazma hızı sabırla değil, tekrarla artar.",
    "On parmak yazma tekniğini öğrenen kimse pişman olmaz.",
    "Gözlerin klavyeden değil ekrandan ayrılmamalı.",
    "Ritim bulmak hız kazanmaktan daha önemlidir.",
    "Doğruluk yüzde doksanın altına düştüğünde yavaşla.",
    "Teknoloji değişir ama klavye kullanımı hep gerekli kalır.",
    "Sabah on dakika pratik, akşam fark edilir ilerleme demektir.",
    "Yazarken nefes al, kasılmış eller yavaş hareket eder.",
    "En iyi yazıcılar en çok hata yapanlardır başlangıçta.",
    "Kelimeyi değil hareketi öğren, parmaklar kendiliğinden bulur.",
]

BG = "#0a0a0f"
PANEL = "#13131a"
BORDER = "#1e1e2e"
ACCENT = "#64c8ff"
ACCENT2 = "#a78bfa"
TEXT_DIM = "#4a4a6a"
TEXT_MID = "#8888aa"
TEXT_BRIGHT = "#e2e8f0"
GREEN = "#4ade80"
RED = "#f87171"
YELLOW = "#fbbf24"


class HizliYaz:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HızlıYaz")
        self.root.configure(bg=BG)
        self.root.geometry("900x620")
        self.root.minsize(760, 520)

        icon_path = self._resource("icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self._fonts()
        self._state()
        self._build_ui()
        self.root.mainloop()

    def _resource(self, name):
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, name)

    def _fonts(self):
        self.f_mono = tkfont.Font(family="Consolas", size=15)
        self.f_mono_lg = tkfont.Font(family="Consolas", size=18, weight="bold")
        self.f_ui = tkfont.Font(family="Segoe UI", size=11)
        self.f_ui_sm = tkfont.Font(family="Segoe UI", size=9)
        self.f_title = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.f_stat = tkfont.Font(family="Consolas", size=26, weight="bold")
        self.f_stat_lbl = tkfont.Font(family="Segoe UI", size=9)

    def _state(self):
        self.mode = "menu"
        self.ozel_metinler = []
        self.hedef_metin = ""
        self.baslangic = None
        self.bitti = False
        self.yanlis_pos = set()

    def _build_ui(self):
        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill="both", expand=True)
        self._goster_menu()

    def _temizle(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _goster_menu(self):
        self._temizle()
        self.mode = "menu"

        header = tk.Frame(self.container, bg=BG)
        header.pack(pady=(48, 0))

        tk.Label(header, text="⚡", font=tkfont.Font(size=36), bg=BG, fg=ACCENT).pack()
        tk.Label(header, text="HızlıYaz", font=self.f_title, bg=BG, fg=TEXT_BRIGHT).pack(pady=(4, 2))
        tk.Label(header, text="Yazma hızını ve doğruluğunu geliştir", font=self.f_ui_sm, bg=BG, fg=TEXT_DIM).pack()

        sep = tk.Frame(self.container, bg=BORDER, height=1)
        sep.pack(fill="x", padx=60, pady=32)

        ozel_frame = tk.Frame(self.container, bg=PANEL, bd=0, highlightthickness=1, highlightbackground=BORDER)
        ozel_frame.pack(padx=60, fill="x")

        header_f = tk.Frame(ozel_frame, bg=PANEL)
        header_f.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(header_f, text="Yeni hızlı yazma yeri", font=self.f_ui, bg=PANEL, fg=TEXT_MID).pack(anchor="w")
        tk.Label(header_f, text="Buraya kendi metinlerini gir veya hazır listeden başla", font=self.f_ui_sm, bg=PANEL, fg=TEXT_DIM).pack(anchor="w")

        text_wrap = tk.Frame(ozel_frame, bg=PANEL)
        text_wrap.pack(fill="x", padx=20, pady=(0, 8))

        self.ozel_text = tk.Text(
            text_wrap, height=5, font=self.f_mono,
            bg="#0d0d14", fg=TEXT_BRIGHT,
            insertbackground=ACCENT,
            relief="flat", bd=0,
            padx=12, pady=10,
            wrap="word",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self.ozel_text.pack(fill="x")
        self.ozel_text.insert("1.0", "\n".join(self.ozel_metinler) if self.ozel_metinler else "")

        placeholder = "Her satıra bir metin gir. Boş bırakırsan hazır metinler kullanılır."
        if not self.ozel_metinler:
            self.ozel_text.insert("1.0", placeholder)
            self.ozel_text.config(fg=TEXT_DIM)

            def on_focus_in(e):
                if self.ozel_text.get("1.0", "end-1c") == placeholder:
                    self.ozel_text.delete("1.0", "end")
                    self.ozel_text.config(fg=TEXT_BRIGHT)

            def on_focus_out(e):
                if not self.ozel_text.get("1.0", "end-1c").strip():
                    self.ozel_text.insert("1.0", placeholder)
                    self.ozel_text.config(fg=TEXT_DIM)

            self.ozel_text.bind("<FocusIn>", on_focus_in)
            self.ozel_text.bind("<FocusOut>", on_focus_out)

        btn_frame = tk.Frame(ozel_frame, bg=PANEL)
        btn_frame.pack(fill="x", padx=20, pady=(4, 20))

        self._btn(btn_frame, "⚡  Eğitimi Başlat", self._baslat, accent=True).pack(side="left")
        tk.Label(btn_frame, text="veya", font=self.f_ui_sm, bg=PANEL, fg=TEXT_DIM).pack(side="left", padx=12)
        self._btn(btn_frame, "Hazır metinler", lambda: self._baslat(hazir=True)).pack(side="left")

    def _btn(self, parent, text, cmd, accent=False):
        bg = ACCENT if accent else PANEL
        fg = "#0a0a0f" if accent else TEXT_MID
        hover_bg = "#7dd3fc" if accent else BORDER

        b = tk.Label(
            parent, text=text, font=self.f_ui,
            bg=bg, fg=fg,
            padx=18, pady=8,
            cursor="hand2",
            relief="flat",
            bd=0,
            highlightthickness=1 if not accent else 0,
            highlightbackground=BORDER,
        )
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(bg=hover_bg))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _baslat(self, hazir=False):
        raw = self.ozel_text.get("1.0", "end-1c").strip()
        placeholder = "Her satıra bir metin gir. Boş bırakırsan hazır metinler kullanılır."

        if raw and raw != placeholder and not hazir:
            self.ozel_metinler = [l.strip() for l in raw.splitlines() if l.strip()]
            havuz = self.ozel_metinler
        else:
            havuz = METINLER

        self.hedef_metin = random.choice(havuz)
        self._goster_yaz()

    def _goster_yaz(self):
        self._temizle()
        self.mode = "yaz"
        self.baslangic = None
        self.bitti = False
        self.yanlis_pos = set()

        top = tk.Frame(self.container, bg=BG)
        top.pack(fill="x", padx=40, pady=(28, 0))

        self._stat_blok(top, "DAK/KW", "—", "hiz_lbl").pack(side="left", padx=(0, 24))
        self._stat_blok(top, "DOĞRULUK", "—", "dogru_lbl").pack(side="left", padx=(0, 24))
        self._stat_blok(top, "SÜRE", "0s", "sure_lbl").pack(side="left")

        geri = tk.Label(top, text="← Geri", font=self.f_ui_sm, bg=BG, fg=TEXT_DIM, cursor="hand2")
        geri.pack(side="right")
        geri.bind("<Button-1>", lambda e: self._goster_menu())
        geri.bind("<Enter>", lambda e: geri.config(fg=TEXT_MID))
        geri.bind("<Leave>", lambda e: geri.config(fg=TEXT_DIM))

        sep = tk.Frame(self.container, bg=BORDER, height=1)
        sep.pack(fill="x", padx=40, pady=20)

        metin_wrap = tk.Frame(self.container, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        metin_wrap.pack(fill="x", padx=40)

        self.metin_canvas = tk.Text(
            metin_wrap,
            font=self.f_mono_lg,
            bg=PANEL, fg=TEXT_DIM,
            relief="flat", bd=0,
            padx=24, pady=20,
            wrap="word",
            cursor="arrow",
            state="normal",
            height=4,
        )
        self.metin_canvas.pack(fill="x")
        self.metin_canvas.insert("1.0", self.hedef_metin)
        self.metin_canvas.tag_config("done", fg=TEXT_BRIGHT)
        self.metin_canvas.tag_config("current", fg=ACCENT, underline=True)
        self.metin_canvas.tag_config("wrong", fg=RED, background="#2d0f0f")
        self.metin_canvas.tag_config("pending", fg=TEXT_DIM)
        self.metin_canvas.config(state="disabled")

        self._renkle_metin(0)

        giris_frame = tk.Frame(self.container, bg=BG)
        giris_frame.pack(fill="x", padx=40, pady=(16, 0))

        tk.Label(giris_frame, text="Yazmaya başla →", font=self.f_ui_sm, bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 6))

        self.giris = tk.Text(
            giris_frame, height=3, font=self.f_mono,
            bg=PANEL, fg=TEXT_BRIGHT,
            insertbackground=ACCENT,
            relief="flat", bd=0,
            padx=16, pady=12,
            wrap="word",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self.giris.pack(fill="x")
        self.giris.bind("<KeyRelease>", self._kontrol)
        self.giris.focus_set()

        self._sure_timer()

    def _stat_blok(self, parent, baslik, deger, attr):
        f = tk.Frame(parent, bg=BG)
        lbl_d = tk.Label(f, text=deger, font=self.f_stat, bg=BG, fg=ACCENT)
        lbl_d.pack(anchor="w")
        tk.Label(f, text=baslik, font=self.f_stat_lbl, bg=BG, fg=TEXT_DIM).pack(anchor="w")
        setattr(self, attr, lbl_d)
        return f

    def _renkle_metin(self, yazilan_len):
        self.metin_canvas.config(state="normal")
        self.metin_canvas.tag_remove("done", "1.0", "end")
        self.metin_canvas.tag_remove("current", "1.0", "end")
        self.metin_canvas.tag_remove("wrong", "1.0", "end")
        self.metin_canvas.tag_remove("pending", "1.0", "end")

        for i in range(len(self.hedef_metin)):
            start = f"1.{i}"
            end = f"1.{i+1}"
            if i < yazilan_len:
                if i in self.yanlis_pos:
                    self.metin_canvas.tag_add("wrong", start, end)
                else:
                    self.metin_canvas.tag_add("done", start, end)
            elif i == yazilan_len:
                self.metin_canvas.tag_add("current", start, end)
            else:
                self.metin_canvas.tag_add("pending", start, end)

        self.metin_canvas.config(state="disabled")

    def _kontrol(self, event=None):
        if self.bitti:
            return

        yazilan = self.giris.get("1.0", "end-1c")

        if yazilan and self.baslangic is None:
            self.baslangic = time.time()

        n = len(yazilan)
        self.yanlis_pos = set()

        for i, ch in enumerate(yazilan):
            if i < len(self.hedef_metin) and ch != self.hedef_metin[i]:
                self.yanlis_pos.add(i)

        self._renkle_metin(n)

        if n > 0 and self.baslangic:
            gecen = time.time() - self.baslangic
            kelime = len(yazilan.split())
            dak = gecen / 60
            hiz = int(kelime / dak) if dak > 0 else 0
            self.hiz_lbl.config(text=str(hiz))

            dogru = sum(1 for i, c in enumerate(yazilan) if i < len(self.hedef_metin) and c == self.hedef_metin[i])
            oran = int(dogru / max(n, 1) * 100)
            renk = GREEN if oran >= 90 else YELLOW if oran >= 70 else RED
            self.dogru_lbl.config(text=f"%{oran}", fg=renk)

        if yazilan == self.hedef_metin:
            self.bitti = True
            self._bitis()

    def _sure_timer(self):
        if self.bitti:
            return
        if self.baslangic:
            gecen = int(time.time() - self.baslangic)
            self.sure_lbl.config(text=f"{gecen}s")
        self.root.after(500, self._sure_timer)

    def _bitis(self):
        self.giris.config(state="disabled")
        gecen = time.time() - self.baslangic
        yazilan = self.giris.get("1.0", "end-1c")
        kelime = len(yazilan.split())
        dak = gecen / 60
        hiz = int(kelime / dak) if dak > 0 else 0
        dogru = sum(1 for i, c in enumerate(yazilan) if i < len(self.hedef_metin) and c == self.hedef_metin[i])
        oran = int(dogru / len(self.hedef_metin) * 100)

        overlay = tk.Frame(self.container, bg=BG)
        overlay.pack(pady=24, padx=40, fill="x")

        tk.Frame(overlay, bg=BORDER, height=1).pack(fill="x", pady=(0, 20))

        row = tk.Frame(overlay, bg=BG)
        row.pack()

        for val, lbl, renk in [(f"{hiz}", "DAK/KW", ACCENT), (f"%{oran}", "DOĞRULUK", GREEN if oran >= 90 else YELLOW), (f"{gecen:.1f}s", "SÜRE", ACCENT2)]:
            blk = tk.Frame(row, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
            blk.pack(side="left", padx=12, ipadx=24, ipady=12)
            tk.Label(blk, text=val, font=self.f_stat, bg=PANEL, fg=renk).pack()
            tk.Label(blk, text=lbl, font=self.f_stat_lbl, bg=PANEL, fg=TEXT_DIM).pack()

        btn_row = tk.Frame(overlay, bg=BG)
        btn_row.pack(pady=(20, 0))
        self._btn(btn_row, "⚡  Tekrar Dene", lambda: self._goster_yaz(), accent=True).pack(side="left", padx=8)
        self._btn(btn_row, "Yeni Metin", lambda: self._baslat()).pack(side="left", padx=8)
        self._btn(btn_row, "Ana Menü", lambda: self._goster_menu()).pack(side="left", padx=8)


if __name__ == "__main__":
    HizliYaz()

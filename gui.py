import math
import sys
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from models import Kategori
from reports import LaporanBulanan
from reports.laporan_bulanan import format_rupiah
from services import KeuanganService

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BULAN_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]
BULAN_PENDEK = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

if sys.platform.startswith("win"):
    FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    FAMILY = "Helvetica Neue"
else:
    FAMILY = "DejaVu Sans"

# Palet gelap ala dashboard fintech
PALET = {
    "bg": "#090d18",
    "sidebar": "#0d1322",
    "card": "#111a2e",
    "card_alt": "#16213a",
    "border": "#1e2b48",
    "text": "#e8edf7",
    "muted": "#7f8ea8",
    "primary": "#4f7cff",
    "primary_hover": "#3d68e6",
    "primary_soft": "#16264f",
    "emerald": "#2dd4a8",
    "emerald_hover": "#22b890",
    "emerald_soft": "#0e3a37",
    "rose": "#ff6b81",
    "rose_hover": "#e8566c",
    "rose_soft": "#43182a",
    "amber": "#f5b942",
    "chip": "#1c2a47",
    "chip_hover": "#27395e",
    "nav_hover": "#131d35",
}

# Warna seri untuk donut chart
SERI = ["#4f7cff", "#2dd4a8", "#f5b942", "#ff6b81", "#9b7bff", "#38bdf8", "#64748b"]


# ----------------------------------------------------------------- helper
def font(ukuran: int = 13, tebal: bool = False) -> ctk.CTkFont:
    return ctk.CTkFont(family=FAMILY, size=ukuran, weight="bold" if tebal else "normal")


def ringkas_rupiah(n: float) -> str:
    """Label sumbu grafik yang singkat: 1,5jt / 500rb."""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}M".replace(".0", "").replace(".", ",")
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}jt".replace(".0", "").replace(".", ",")
    if n >= 1_000:
        return f"{n / 1_000:.0f}rb"
    return f"{n:.0f}"


def skala_cantik(maks: float, garis: int = 4):
    """Batas atas sumbu Y yang 'bulat' agar garis bantu rapi."""
    if maks <= 0:
        return 100_000, garis
    mentah = maks / garis
    pangkat = 10 ** math.floor(math.log10(mentah))
    langkah = pangkat
    for m in (1, 2, 2.5, 5, 10):
        langkah = m * pangkat
        if langkah * garis >= maks:
            break
    return langkah * garis, garis


def parse_rupiah(teks: str, minimum: int = 1) -> int:
    """'1.500.000' / '1500000' -> int. Error jika bukan angka atau < minimum."""
    bersih = teks.strip().replace(".", "").replace(",", "")
    if not bersih.isdigit() or int(bersih) < minimum:
        if minimum > 0:
            raise ValueError("Jumlah harus berupa angka lebih dari 0.")
        raise ValueError("Anggaran harus berupa angka (0 atau lebih).")
    return int(bersih)


def parse_tanggal(teks: str) -> date:
    try:
        return datetime.strptime(teks.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Format tanggal harus YYYY-MM-DD, contoh 2026-11-26.")


def terapkan_gaya_tabel() -> None:
    gaya = ttk.Style()
    gaya.theme_use("default")
    gaya.configure(
        "Treeview",
        background=PALET["card"], foreground=PALET["text"], fieldbackground=PALET["card"],
        rowheight=40, borderwidth=0, relief="flat", font=(FAMILY, 10),
    )
    gaya.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    gaya.map(
        "Treeview",
        background=[("selected", PALET["primary_soft"])],
        foreground=[("selected", "#ffffff")],
    )
    gaya.configure(
        "Treeview.Heading",
        background=PALET["card_alt"], foreground=PALET["muted"], relief="flat",
        borderwidth=0, padding=(10, 10), font=(FAMILY, 9, "bold"),
    )
    gaya.map("Treeview.Heading", background=[("active", PALET["card_alt"])])


# --------------------------------------------------- pabrik widget bergaya
def entry(master, **kw) -> ctk.CTkEntry:
    opsi = dict(
        height=40, font=font(12), fg_color=PALET["card_alt"], border_color=PALET["border"],
        border_width=1, text_color=PALET["text"], placeholder_text_color=PALET["muted"],
        corner_radius=10,
    )
    opsi.update(kw)
    return ctk.CTkEntry(master, **opsi)


def option(master, **kw) -> ctk.CTkOptionMenu:
    opsi = dict(
        height=40, font=font(12), dropdown_font=font(12), corner_radius=10,
        fg_color=PALET["card_alt"], button_color=PALET["chip"], button_hover_color=PALET["chip_hover"],
        text_color=PALET["text"], dropdown_fg_color=PALET["card"],
        dropdown_hover_color=PALET["chip"], dropdown_text_color=PALET["text"],
    )
    opsi.update(kw)
    return ctk.CTkOptionMenu(master, **opsi)


def segmen(master, **kw) -> ctk.CTkSegmentedButton:
    opsi = dict(
        height=38, font=font(12, True), fg_color=PALET["card_alt"],
        selected_color=PALET["primary"], selected_hover_color=PALET["primary_hover"],
        unselected_color=PALET["card_alt"], unselected_hover_color=PALET["chip"],
        text_color=PALET["text"],
    )
    opsi.update(kw)
    return ctk.CTkSegmentedButton(master, **opsi)


def tombol_chip(master, teks, perintah, lebar=66) -> ctk.CTkButton:
    return ctk.CTkButton(
        master, text=teks, width=lebar, height=30, corner_radius=15, font=font(11, True),
        fg_color=PALET["chip"], hover_color=PALET["chip_hover"], text_color=PALET["text"],
        command=perintah,
    )


# ------------------------------------------------------------ komponen UI
class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        defaults = dict(
            fg_color=PALET["card"], border_width=1, border_color=PALET["border"], corner_radius=16,
        )
        defaults.update(kwargs)
        super().__init__(master, **defaults)


def buat_header(master, judul: str, sub: str, aksi=None):
    h = ctk.CTkFrame(master, fg_color="transparent")
    h.grid_columnconfigure(0, weight=1)
    kiri = ctk.CTkFrame(h, fg_color="transparent")
    kiri.grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(kiri, text=judul, font=font(26, True), text_color=PALET["text"]).pack(anchor="w")
    ctk.CTkLabel(kiri, text=sub, font=font(12), text_color=PALET["muted"]).pack(anchor="w", pady=(2, 0))
    if aksi:
        ctk.CTkButton(
            h, text=aksi[0], height=42, corner_radius=12, font=font(13, True),
            fg_color=PALET["primary"], hover_color=PALET["primary_hover"], command=aksi[1],
        ).grid(row=0, column=1, sticky="e", padx=(12, 0))
    return h


class KpiCard(Card):
    """Kartu metrik: garis aksen kecil, judul, nilai besar, keterangan berwarna."""

    def __init__(self, master, judul: str, aksen):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(self, width=28, height=3, corner_radius=2, fg_color=aksen).grid(
            row=0, column=0, sticky="w", padx=20, pady=(18, 10)
        )
        ctk.CTkLabel(self, text=judul.upper(), font=font(10, True), text_color=PALET["muted"]).grid(
            row=1, column=0, sticky="w", padx=20
        )
        self.label_nilai = ctk.CTkLabel(self, text="Rp0", font=font(24, True), text_color=PALET["text"])
        self.label_nilai.grid(row=2, column=0, sticky="w", padx=20, pady=(2, 0))
        self.label_sub = ctk.CTkLabel(self, text="", font=font(11), text_color=PALET["muted"])
        self.label_sub.grid(row=3, column=0, sticky="w", padx=20, pady=(0, 16))

    def set(self, nilai: str, sub: str = "", warna_sub=None, warna_nilai=None) -> None:
        self.label_nilai.configure(text=nilai, text_color=warna_nilai or PALET["text"])
        self.label_sub.configure(text=sub, text_color=warna_sub or PALET["muted"])


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, wrap: int = 380):
        super().__init__(master, fg_color="transparent", corner_radius=10)
        self.label = ctk.CTkLabel(self, text="", wraplength=wrap, justify="left", font=font(12))
        self.label.pack(anchor="w", padx=12, pady=8)

    def tampil(self, teks: str, error: bool = False) -> None:
        if not teks:
            self.configure(fg_color="transparent")
            self.label.configure(text="")
            return
        self.configure(fg_color=PALET["rose_soft"] if error else PALET["emerald_soft"])
        self.label.configure(text=teks, text_color=PALET["rose"] if error else PALET["emerald"])


class Tabel(ctk.CTkFrame):
    """ttk.Treeview + scrollbar + baris belang + empty state."""

    def __init__(self, master, kolom, teks_kosong: str = "Belum ada data untuk ditampilkan."):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ids = [f"c{i}" for i in range(len(kolom))]
        self.tree = ttk.Treeview(self, columns=ids, show="headings", height=6, selectmode="browse")
        for cid, (judul, lebar, rata) in zip(ids, kolom):
            self.tree.heading(cid, text=judul.upper(), anchor=rata)
            self.tree.column(cid, width=lebar, minwidth=max(40, lebar // 2), anchor=rata, stretch=True)

        bar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=bar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        bar.grid(row=0, column=1, sticky="ns", padx=(6, 0))

        self.label_kosong = ctk.CTkLabel(
            self, text=teks_kosong, font=font(12), text_color=PALET["muted"], justify="center"
        )
        self.tree.tag_configure("even", background=PALET["card"])
        self.tree.tag_configure("odd", background="#141f36")
        self.tree.tag_configure("pemasukan", foreground=PALET["emerald"])
        self.tree.tag_configure("pengeluaran", foreground=PALET["rose"])

    def isi(self, baris, tags_per_baris=None) -> None:
        self.tree.delete(*self.tree.get_children())
        if not baris:
            self.label_kosong.place(relx=0.5, rely=0.5, anchor="center")
            return
        self.label_kosong.place_forget()
        for idx, b in enumerate(baris):
            stripe = "even" if idx % 2 == 0 else "odd"
            extra = tags_per_baris[idx] if tags_per_baris and idx < len(tags_per_baris) else ()
            if isinstance(extra, str):
                extra = (extra,)
            self.tree.insert("", "end", values=b, tags=(stripe, *extra))


# ------------------------------------------------------------------ grafik
class BarChart(tk.Canvas):
    """Grafik batang berkelompok (pemasukan vs pengeluaran per bulan). Responsif."""

    def __init__(self, master, tinggi: int = 250):
        super().__init__(master, height=tinggi, highlightthickness=0, bd=0, bg=PALET["card"])
        self.data = ([], [], [])
        self.bind("<Configure>", lambda _e: self.gambar())

    def set_data(self, labels, masuk, keluar) -> None:
        self.data = (labels, masuk, keluar)
        self.gambar()

    def gambar(self) -> None:
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 80 or h < 80:
            return
        labels, masuk, keluar = self.data
        kiri, kanan, atas, bawah = 50, 8, 12, 28
        area_w, area_h = w - kiri - kanan, h - atas - bawah

        maks, garis = skala_cantik(max(list(masuk) + list(keluar) + [0]))
        for i in range(garis + 1):
            y = atas + area_h - (i / garis) * area_h
            self.create_line(kiri, y, w - kanan, y, fill=PALET["border"], dash=(2, 4) if i else ())
            self.create_text(kiri - 8, y, text=ringkas_rupiah(maks * i / garis), anchor="e",
                             fill=PALET["muted"], font=(FAMILY, 8))

        n = len(labels)
        if n == 0:
            return
        lebar_grup = area_w / n
        lebar_bar = max(6, min(26, lebar_grup * 0.26))
        for i, label in enumerate(labels):
            cx = kiri + lebar_grup * (i + 0.5)
            for nilai, warna, geser in ((masuk[i], PALET["emerald"], -1), (keluar[i], PALET["rose"], 1)):
                if nilai <= 0:
                    continue
                tinggi_bar = max(3, nilai / maks * area_h)
                x0 = cx + 2 if geser > 0 else cx - lebar_bar - 2
                self.create_rectangle(x0, atas + area_h - tinggi_bar, x0 + lebar_bar, atas + area_h,
                                      fill=warna, width=0)
            terakhir = i == n - 1
            self.create_text(cx, h - bawah / 2 + 2, text=label,
                             fill=PALET["text"] if terakhir else PALET["muted"],
                             font=(FAMILY, 9, "bold" if terakhir else "normal"))


class DonutChart(ctk.CTkFrame):
    """Donut chart (tk.Canvas) + legenda."""

    def __init__(self, master, ukuran: int = 190):
        super().__init__(master, fg_color="transparent")
        self.ukuran = ukuran
        self.grid_columnconfigure(1, weight=1)
        self.canvas = tk.Canvas(self, width=ukuran, height=ukuran, highlightthickness=0, bd=0,
                                bg=PALET["card"])
        self.canvas.grid(row=0, column=0, padx=(4, 18), pady=4)
        self.legend = ctk.CTkFrame(self, fg_color="transparent")
        self.legend.grid(row=0, column=1, sticky="w")

    def gambar(self, data, judul_tengah: str = "Total") -> None:
        c = self.canvas
        c.delete("all")
        for w in self.legend.winfo_children():
            w.destroy()

        u, tebal = self.ukuran, 24
        pad = 8 + tebal // 2
        kotak = (pad, pad, u - pad, u - pad)

        data = [(n, v) for n, v in sorted(data, key=lambda x: -x[1]) if v > 0]
        if len(data) > 6:
            sisa = sum(v for _, v in data[5:])
            data = data[:5] + [("Lainnya", sisa)]
        total = sum(v for _, v in data)

        if total <= 0:
            c.create_oval(*kotak, outline=PALET["border"], width=tebal)
            c.create_text(u / 2, u / 2, text="Belum ada\npengeluaran", justify="center",
                          fill=PALET["muted"], font=(FAMILY, 10))
            return

        mulai = 90.0
        for i, (nama, nilai) in enumerate(data):
            warna = SERI[i % len(SERI)]
            sudut = min(nilai / total * 360, 359.9)
            c.create_arc(*kotak, start=mulai, extent=-sudut, style="arc", outline=warna, width=tebal)
            mulai -= sudut

            baris = ctk.CTkFrame(self.legend, fg_color="transparent")
            baris.pack(anchor="w", pady=3)
            ctk.CTkFrame(baris, width=10, height=10, corner_radius=5, fg_color=warna).pack(
                side="left", padx=(0, 8)
            )
            ctk.CTkLabel(baris, text=nama, font=font(12, True), text_color=PALET["text"]).pack(side="left")
            ctk.CTkLabel(baris, text=f"  {nilai / total * 100:.0f}%", font=font(11),
                         text_color=PALET["muted"]).pack(side="left")

        c.create_text(u / 2, u / 2 - 11, text=judul_tengah.upper(), fill=PALET["muted"],
                      font=(FAMILY, 8, "bold"))
        c.create_text(u / 2, u / 2 + 9, text=format_rupiah(total), fill=PALET["text"],
                      font=(FAMILY, 12, "bold"))


# ---------------------------------------------------- render bersama
def render_progres(box, kategori: dict, terpakai_map: dict,
                   kosong: str = "Belum ada kategori dengan batas anggaran.") -> None:
    for w in box.winfo_children():
        w.destroy()
    daftar = [k for k in kategori.values() if k.anggaran > 0]
    if not daftar:
        ctk.CTkLabel(box, text=kosong, font=font(12), text_color=PALET["muted"],
                     justify="center").pack(pady=24)
        return
    for kat in daftar:
        terpakai = terpakai_map.get(kat.nama, 0)
        rasio = terpakai / kat.anggaran
        persen = int(round(rasio * 100))
        if terpakai > kat.anggaran:
            warna, status = PALET["rose"], "Melebihi batas"
        elif persen >= 75:
            warna, status = PALET["amber"], "Hampir habis"
        else:
            warna, status = PALET["emerald"], "Aman"

        baris = ctk.CTkFrame(box, fg_color="transparent")
        baris.pack(fill="x", pady=(0, 14))
        atas = ctk.CTkFrame(baris, fg_color="transparent")
        atas.pack(fill="x")
        ctk.CTkLabel(atas, text=kat.nama, font=font(12, True), text_color=PALET["text"]).pack(side="left")
        ctk.CTkLabel(atas, text=f"{persen}%", font=font(12, True), text_color=warna).pack(side="right")
        prog = ctk.CTkProgressBar(baris, height=6, corner_radius=3, progress_color=warna,
                                  fg_color=PALET["chip"])
        prog.set(min(rasio, 1.0))
        prog.pack(fill="x", pady=(6, 4))
        ctk.CTkLabel(
            baris, text=f"{format_rupiah(terpakai)} dari {format_rupiah(kat.anggaran)}  ·  {status}",
            font=font(11), text_color=PALET["muted"],
        ).pack(anchor="w")


def render_transaksi_terakhir(box, items) -> None:
    for w in box.winfo_children():
        w.destroy()
    if not items:
        ctk.CTkLabel(
            box, text="Belum ada transaksi.\nKlik \"+ Transaksi Baru\" untuk mulai mencatat.",
            font=font(12), text_color=PALET["muted"], justify="center",
        ).pack(pady=28)
        return
    for i, t in enumerate(items):
        masuk = t.jenis() == "Pemasukan"
        baris = ctk.CTkFrame(box, fg_color="transparent")
        baris.pack(fill="x")
        baris.grid_columnconfigure(1, weight=1)
        ctk.CTkFrame(
            baris, width=4, height=30, corner_radius=2,
            fg_color=PALET["emerald"] if masuk else PALET["rose"],
        ).grid(row=0, column=0, rowspan=2, padx=(0, 12), pady=10)
        ctk.CTkLabel(baris, text=t.kategori.nama, font=font(12, True), text_color=PALET["text"]).grid(
            row=0, column=1, sticky="w", pady=(8, 0)
        )
        ctk.CTkLabel(baris, text=f"{t.tanggal:%d %b %Y}  ·  {t.jenis()}", font=font(10),
                     text_color=PALET["muted"]).grid(row=1, column=1, sticky="w", pady=(0, 8))
        ctk.CTkLabel(
            baris, text=f"{'+' if masuk else '-'}{format_rupiah(t.jumlah)}", font=font(13, True),
            text_color=PALET["emerald"] if masuk else PALET["rose"],
        ).grid(row=0, column=2, rowspan=2, sticky="e")
        if i < len(items) - 1:
            ctk.CTkFrame(box, height=1, fg_color=PALET["border"]).pack(fill="x")


# ---------------------------------------------------------------- aplikasi
class App(ctk.CTk):
    NAV = [("Dashboard", "dashboard"), ("Transaksi", "transaksi"),
           ("Kategori", "kategori"), ("Laporan", "laporan")]

    def __init__(self):
        super().__init__()
        self.title("DompetKu — Dashboard Keuangan")
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self.configure(fg_color=PALET["bg"])
        terapkan_gaya_tabel()

        # Objek inti dari layanan OOP
        self.service = KeuanganService()
        self.kategori: dict[str, Kategori] = {
            "Gaji": Kategori("Gaji"),
            "Makan": Kategori("Makan", 500_000),
            "Transport": Kategori("Transport", 200_000),
        }
        self.dialog = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._buat_sidebar()

        self.halaman = {
            "dashboard": DashboardPage(self),
            "transaksi": TransaksiPage(self),
            "kategori": KategoriPage(self),
            "laporan": LaporanPage(self),
        }
        for frame in self.halaman.values():
            frame.grid(row=0, column=1, sticky="nsew", padx=(28, 20), pady=(24, 16))
        self.buka("dashboard")

    # ---- data bantu untuk grafik & KPI
    def total_bulan(self, tahun: int, bulan: int):
        masuk = keluar = 0
        for t in self.service.tampilkan_semua():
            if t.tanggal.year == tahun and t.tanggal.month == bulan:
                if t.jenis() == "Pemasukan":
                    masuk += t.jumlah
                else:
                    keluar += t.jumlah
        return masuk, keluar

    def pengeluaran_per_kategori(self, tahun: int, bulan: int) -> dict:
        hasil: dict[str, int] = {}
        for t in self.service.tampilkan_semua():
            if t.tanggal.year == tahun and t.tanggal.month == bulan and t.jenis() == "Pengeluaran":
                hasil[t.kategori.nama] = hasil.get(t.kategori.nama, 0) + t.jumlah
        return hasil

    @staticmethod
    def bulan_mundur(n: int):
        """n bulan terakhir (termasuk bulan ini), urut dari yang paling lama."""
        hari = date.today()
        idx = hari.year * 12 + (hari.month - 1)
        return [((i // 12), (i % 12) + 1) for i in range(idx - n + 1, idx + 1)]

    # ---- sidebar
    def _buat_sidebar(self):
        bar = ctk.CTkFrame(self, width=232, corner_radius=0, fg_color=PALET["sidebar"],
                           border_width=1, border_color=PALET["border"])
        bar.grid(row=0, column=0, sticky="nsew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)
        bar.grid_rowconfigure(6, weight=1)

        brand = ctk.CTkFrame(bar, fg_color="transparent")
        brand.grid(row=0, column=0, padx=20, pady=(28, 28), sticky="ew")
        logo = ctk.CTkFrame(brand, width=40, height=40, corner_radius=12, fg_color=PALET["primary"])
        logo.pack(side="left", padx=(0, 12))
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="D", font=font(18, True), text_color="#ffffff").place(
            relx=0.5, rely=0.5, anchor="center"
        )
        teks = ctk.CTkFrame(brand, fg_color="transparent")
        teks.pack(side="left")
        ctk.CTkLabel(teks, text="DompetKu", font=font(18, True), text_color=PALET["text"]).pack(anchor="w")
        ctk.CTkLabel(teks, text="Keuangan Pribadi", font=font(11), text_color=PALET["muted"]).pack(anchor="w")

        ctk.CTkLabel(bar, text="MENU", font=font(10, True), text_color=PALET["muted"]).grid(
            row=1, column=0, padx=26, pady=(0, 8), sticky="w"
        )

        self.tombol_menu, self.indikator = {}, {}
        for i, (teks_menu, kunci) in enumerate(self.NAV, start=2):
            baris = ctk.CTkFrame(bar, fg_color="transparent")
            baris.grid(row=i, column=0, padx=(0, 14), pady=2, sticky="ew")
            baris.grid_columnconfigure(1, weight=1)
            ind = ctk.CTkFrame(baris, width=4, height=22, corner_radius=2, fg_color="transparent")
            ind.grid(row=0, column=0, padx=(6, 8))
            tombol = ctk.CTkButton(
                baris, text=teks_menu, height=42, corner_radius=10, anchor="w", font=font(13, True),
                fg_color="transparent", text_color=PALET["muted"], hover_color=PALET["nav_hover"],
                command=lambda k=kunci: self.buka(k),
            )
            tombol.grid(row=0, column=1, sticky="ew")
            self.tombol_menu[kunci] = tombol
            self.indikator[kunci] = ind

        hari = date.today()
        bawah = ctk.CTkFrame(bar, fg_color=PALET["card_alt"], corner_radius=12, border_width=1,
                             border_color=PALET["border"])
        bawah.grid(row=7, column=0, padx=16, pady=(8, 20), sticky="ew")
        ctk.CTkLabel(bawah, text="HARI INI", font=font(10, True), text_color=PALET["muted"]).pack(
            anchor="w", padx=14, pady=(10, 0)
        )
        ctk.CTkLabel(
            bawah, text=f"{hari.day} {BULAN_ID[hari.month - 1]} {hari.year}", font=font(12, True),
            text_color=PALET["text"],
        ).pack(anchor="w", padx=14, pady=(2, 10))

    def buka(self, kunci: str):
        for k, tombol in self.tombol_menu.items():
            aktif = k == kunci
            tombol.configure(
                fg_color=PALET["card_alt"] if aktif else "transparent",
                text_color=PALET["text"] if aktif else PALET["muted"],
            )
            self.indikator[k].configure(fg_color=PALET["primary"] if aktif else "transparent")
        self.halaman[kunci].tkraise()
        self.refresh_semua()

    def buka_dialog(self):
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.lift()
            self.dialog.focus()
            return
        self.dialog = TransaksiDialog(self)

    def refresh_semua(self):
        for frame in self.halaman.values():
            frame.refresh()


# ------------------------------------------------------- dialog transaksi
class TransaksiDialog(ctk.CTkToplevel):
    def __init__(self, app: App):
        super().__init__(app)
        self.app = app
        self.title("Transaksi Baru")
        self.configure(fg_color=PALET["bg"])
        lebar, tinggi = 480, 640
        x = app.winfo_rootx() + (app.winfo_width() - lebar) // 2
        y = app.winfo_rooty() + (app.winfo_height() - tinggi) // 2
        self.geometry(f"{lebar}x{tinggi}+{max(x, 0)}+{max(y, 0)}")
        self.resizable(False, False)
        self.transient(app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = Card(self)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Transaksi Baru", font=font(18, True), text_color=PALET["text"]).grid(
            row=0, column=0, sticky="w", padx=24, pady=(22, 14)
        )
        self.jenis = segmen(card, values=["Pemasukan", "Pengeluaran"], height=42,
                            command=self._on_jenis_ubah)
        self.jenis.set("Pemasukan")
        self.jenis.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 18))

        ctk.CTkLabel(card, text="JUMLAH", font=font(10, True), text_color=PALET["muted"]).grid(
            row=2, column=0, sticky="w", padx=24, pady=(0, 4)
        )
        wrap = ctk.CTkFrame(card, fg_color=PALET["card_alt"], border_width=1,
                            border_color=PALET["border"], corner_radius=12)
        wrap.grid(row=3, column=0, sticky="ew", padx=24)
        wrap.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(wrap, text="Rp", font=font(18, True), text_color=PALET["muted"]).grid(
            row=0, column=0, padx=(16, 4), pady=8
        )
        self.entry_jumlah = ctk.CTkEntry(wrap, height=44, border_width=0, fg_color="transparent",
                                         placeholder_text="0", font=font(24, True),
                                         text_color=PALET["text"], placeholder_text_color=PALET["muted"])
        self.entry_jumlah.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        chips = ctk.CTkFrame(card, fg_color="transparent")
        chips.grid(row=4, column=0, sticky="ew", padx=24, pady=(10, 18))
        for label, nominal in [("+25rb", 25_000), ("+50rb", 50_000), ("+100rb", 100_000), ("+500rb", 500_000)]:
            tombol_chip(chips, label, lambda n=nominal: self._tambah_nominal(n)).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            chips, text="Reset", width=58, height=30, corner_radius=15, font=font(11),
            fg_color="transparent", border_width=1, border_color=PALET["border"],
            hover_color=PALET["nav_hover"], text_color=PALET["muted"],
            command=lambda: self.entry_jumlah.delete(0, "end"),
        ).pack(side="left")

        ctk.CTkLabel(card, text="KATEGORI", font=font(10, True), text_color=PALET["muted"]).grid(
            row=5, column=0, sticky="w", padx=24, pady=(0, 4)
        )
        self.menu_kategori = option(card, values=list(app.kategori))
        self.menu_kategori.set(list(app.kategori)[0])
        self.menu_kategori.grid(row=6, column=0, sticky="ew", padx=24, pady=(0, 16))

        ctk.CTkLabel(card, text="TANGGAL (YYYY-MM-DD)", font=font(10, True), text_color=PALET["muted"]).grid(
            row=7, column=0, sticky="w", padx=24, pady=(0, 4)
        )
        tgl = ctk.CTkFrame(card, fg_color="transparent")
        tgl.grid(row=8, column=0, sticky="ew", padx=24, pady=(0, 20))
        tgl.grid_columnconfigure(0, weight=1)
        self.entry_tanggal = entry(tgl)
        self.entry_tanggal.insert(0, date.today().isoformat())
        self.entry_tanggal.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(
            tgl, text="Hari Ini", width=84, height=40, corner_radius=10, font=font(11, True),
            fg_color=PALET["chip"], hover_color=PALET["chip_hover"], text_color=PALET["text"],
            command=self._set_hari_ini,
        ).grid(row=0, column=1)

        self.btn_simpan = ctk.CTkButton(card, text="Simpan Pemasukan", height=48, corner_radius=12,
                                        font=font(14, True), command=self.simpan)
        self.btn_simpan.grid(row=9, column=0, sticky="ew", padx=24, pady=(0, 10))

        self.status = StatusBar(card, wrap=400)
        self.status.grid(row=10, column=0, sticky="ew", padx=24, pady=(0, 18))

        self._on_jenis_ubah("Pemasukan")
        self.bind("<Return>", lambda _e: self.simpan())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.after(200, self._fokus)

    def _fokus(self):
        try:
            self.grab_set()
            self.entry_jumlah.focus()
        except tk.TclError:
            pass

    def _on_jenis_ubah(self, nilai: str):
        if nilai == "Pemasukan":
            self.btn_simpan.configure(text="Simpan Pemasukan", fg_color=PALET["emerald"],
                                      hover_color=PALET["emerald_hover"], text_color="#06231c")
            self.jenis.configure(selected_color=PALET["emerald"], selected_hover_color=PALET["emerald_hover"])
        else:
            self.btn_simpan.configure(text="Simpan Pengeluaran", fg_color=PALET["rose"],
                                      hover_color=PALET["rose_hover"], text_color="#2b0610")
            self.jenis.configure(selected_color=PALET["rose"], selected_hover_color=PALET["rose_hover"])

    def _tambah_nominal(self, tambahan: int):
        teks = self.entry_jumlah.get().strip()
        try:
            sekarang = parse_rupiah(teks, minimum=0) if teks else 0
        except ValueError:
            sekarang = 0
        self.entry_jumlah.delete(0, "end")
        self.entry_jumlah.insert(0, str(sekarang + tambahan))

    def _set_hari_ini(self):
        self.entry_tanggal.delete(0, "end")
        self.entry_tanggal.insert(0, date.today().isoformat())

    def simpan(self):
        try:
            jumlah = parse_rupiah(self.entry_jumlah.get())
            tanggal = parse_tanggal(self.entry_tanggal.get())
            kategori = self.app.kategori[self.menu_kategori.get()]
            if self.jenis.get() == "Pemasukan":
                transaksi = self.app.service.catat_pemasukan(jumlah, kategori, tanggal)
            else:
                transaksi = self.app.service.catat_pengeluaran(jumlah, kategori, tanggal)
        except (ValueError, TypeError) as e:  # termasuk "Saldo tidak cukup" dari service
            self.status.tampil(f"Gagal: {e}", error=True)
            return
        self.status.tampil(f"Tersimpan: {transaksi}")
        self.entry_jumlah.delete(0, "end")
        self.app.refresh_semua()


# ------------------------------------------------------------- dashboard
class DashboardPage(ctk.CTkFrame):
    def __init__(self, app: App):
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        isi = ctk.CTkScrollableFrame(self, fg_color="transparent")
        isi.grid(row=0, column=0, sticky="nsew")
        isi.grid_columnconfigure(0, weight=1)

        buat_header(
            isi, "Dashboard", "Gambaran keuanganmu bulan ini dalam satu layar.",
            aksi=("+  Transaksi Baru", app.buka_dialog),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 18))

        # --- baris KPI
        kpi = ctk.CTkFrame(isi, fg_color="transparent")
        kpi.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        kpi.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")
        self.kpi_saldo = KpiCard(kpi, "Total Saldo", PALET["primary"])
        self.kpi_masuk = KpiCard(kpi, "Pemasukan Bulan Ini", PALET["emerald"])
        self.kpi_keluar = KpiCard(kpi, "Pengeluaran Bulan Ini", PALET["rose"])
        self.kpi_arus = KpiCard(kpi, "Arus Kas Bulan Ini", PALET["amber"])
        for i, k in enumerate((self.kpi_saldo, self.kpi_masuk, self.kpi_keluar, self.kpi_arus)):
            k.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 12, 0))

        # --- baris grafik
        grafik = ctk.CTkFrame(isi, fg_color="transparent")
        grafik.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        grafik.grid_columnconfigure(0, weight=3, uniform="g")
        grafik.grid_columnconfigure(1, weight=2, uniform="g")

        card_bar = Card(grafik)
        card_bar.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        card_bar.grid_columnconfigure(0, weight=1)
        kepala = ctk.CTkFrame(card_bar, fg_color="transparent")
        kepala.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 6))
        kepala.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(kepala, text="Arus Kas 6 Bulan Terakhir", font=font(14, True),
                     text_color=PALET["text"]).grid(row=0, column=0, sticky="w")
        legenda = ctk.CTkFrame(kepala, fg_color="transparent")
        legenda.grid(row=0, column=1, sticky="e")
        for teks, warna in (("Pemasukan", PALET["emerald"]), ("Pengeluaran", PALET["rose"])):
            ctk.CTkFrame(legenda, width=10, height=10, corner_radius=5, fg_color=warna).pack(
                side="left", padx=(10, 6)
            )
            ctk.CTkLabel(legenda, text=teks, font=font(11), text_color=PALET["muted"]).pack(side="left")
        self.bar = BarChart(card_bar, tinggi=250)
        self.bar.grid(row=1, column=0, sticky="ew", padx=(12, 16), pady=(0, 16))

        card_donut = Card(grafik)
        card_donut.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        ctk.CTkLabel(card_donut, text="Pengeluaran per Kategori", font=font(14, True),
                     text_color=PALET["text"]).pack(anchor="w", padx=20, pady=(18, 6))
        self.donut = DonutChart(card_donut, ukuran=190)
        self.donut.pack(anchor="w", padx=16, pady=(8, 18))

        # --- baris bawah
        bawah = ctk.CTkFrame(isi, fg_color="transparent")
        bawah.grid(row=3, column=0, sticky="ew")
        bawah.grid_columnconfigure(0, weight=3, uniform="b")
        bawah.grid_columnconfigure(1, weight=2, uniform="b")

        card_recent = Card(bawah)
        card_recent.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        ctk.CTkLabel(card_recent, text="Transaksi Terbaru", font=font(14, True),
                     text_color=PALET["text"]).pack(anchor="w", padx=20, pady=(18, 6))
        self.box_recent = ctk.CTkFrame(card_recent, fg_color="transparent")
        self.box_recent.pack(fill="x", padx=20, pady=(0, 14))

        card_ang = Card(bawah)
        card_ang.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        ctk.CTkLabel(card_ang, text="Anggaran Bulan Ini", font=font(14, True),
                     text_color=PALET["text"]).pack(anchor="w", padx=20, pady=(18, 12))
        self.box_anggaran = ctk.CTkFrame(card_ang, fg_color="transparent")
        self.box_anggaran.pack(fill="x", padx=20, pady=(0, 6))

    @staticmethod
    def _delta(sekarang: int, lalu: int, naik_baik: bool):
        if lalu == 0:
            return ("Belum ada data bulan lalu" if sekarang else "Belum ada data"), PALET["muted"]
        pct = (sekarang - lalu) / lalu * 100
        if round(pct) == 0:
            return "Sama dengan bulan lalu", PALET["muted"]
        arah = "lebih tinggi" if pct > 0 else "lebih rendah"
        baik = (pct > 0) == naik_baik
        return f"{abs(pct):.0f}% {arah} dari bulan lalu", PALET["emerald"] if baik else PALET["rose"]

    def refresh(self):
        app = self.app
        hari = date.today()
        th, bl = hari.year, hari.month
        pth, pbl = (th, bl - 1) if bl > 1 else (th - 1, 12)
        masuk, keluar = app.total_bulan(th, bl)
        pmasuk, pkeluar = app.total_bulan(pth, pbl)
        saldo = app.service.hitung_saldo()
        arus = masuk - keluar

        self.kpi_saldo.set(
            format_rupiah(saldo), f"{len(app.service)} transaksi tercatat",
            warna_nilai=PALET["rose"] if saldo < 0 else None,
        )
        teks, warna = self._delta(masuk, pmasuk, naik_baik=True)
        self.kpi_masuk.set(format_rupiah(masuk), teks, warna)
        teks, warna = self._delta(keluar, pkeluar, naik_baik=False)
        self.kpi_keluar.set(format_rupiah(keluar), teks, warna)
        if masuk > 0:
            sub = f"{arus / masuk * 100:.0f}% dari pemasukan"
        else:
            sub = "Surplus" if arus >= 0 else "Defisit"
        self.kpi_arus.set(
            format_rupiah(arus), sub,
            PALET["emerald"] if arus > 0 else (PALET["rose"] if arus < 0 else PALET["muted"]),
            PALET["emerald"] if arus > 0 else (PALET["rose"] if arus < 0 else None),
        )

        bulan_list = app.bulan_mundur(6)
        totals = [app.total_bulan(t, b) for t, b in bulan_list]
        self.bar.set_data(
            [BULAN_PENDEK[b - 1] for _, b in bulan_list],
            [m for m, _ in totals], [k for _, k in totals],
        )

        per_kat = app.pengeluaran_per_kategori(th, bl)
        self.donut.gambar(list(per_kat.items()), judul_tengah=BULAN_PENDEK[bl - 1])
        render_transaksi_terakhir(self.box_recent, list(reversed(app.service.tampilkan_semua()))[:6])
        render_progres(self.box_anggaran, app.kategori, per_kat)


# ------------------------------------------------------------- transaksi
class TransaksiPage(ctk.CTkFrame):
    def __init__(self, app: App):
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        buat_header(
            self, "Transaksi", "Seluruh riwayat pemasukan dan pengeluaran yang sudah tercatat.",
            aksi=("+  Transaksi Baru", app.buka_dialog),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 16))

        toolbar = Card(self)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        toolbar.grid_columnconfigure(2, weight=1)
        self.filter = segmen(toolbar, values=["Semua", "Pemasukan", "Pengeluaran"],
                             command=lambda _: self.refresh())
        self.filter.set("Semua")
        self.filter.grid(row=0, column=0, padx=(16, 10), pady=14)
        self.filter_kat = option(toolbar, values=["Semua Kategori"], width=170, height=38,
                                 command=lambda _: self.refresh())
        self.filter_kat.set("Semua Kategori")
        self.filter_kat.grid(row=0, column=1, padx=(0, 10), pady=14)
        self.entry_cari = entry(toolbar, height=38, placeholder_text="Cari kategori, tanggal, atau nominal...")
        self.entry_cari.grid(row=0, column=2, sticky="ew", padx=(0, 16), pady=14)
        self.entry_cari.bind("<KeyRelease>", lambda _: self.refresh())

        tabel_card = Card(self)
        tabel_card.grid(row=2, column=0, sticky="nsew")
        tabel_card.grid_columnconfigure(0, weight=1)
        tabel_card.grid_rowconfigure(1, weight=1)
        self.judul_tabel = ctk.CTkLabel(tabel_card, text="Riwayat Transaksi", font=font(14, True),
                                        text_color=PALET["text"])
        self.judul_tabel.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        self.tabel = Tabel(
            tabel_card,
            [("ID", 60, "center"), ("Tanggal", 120, "center"), ("Jenis", 120, "center"),
             ("Kategori", 180, "w"), ("Jumlah", 160, "e")],
            teks_kosong="Tidak ada transaksi yang cocok dengan filter.",
        )
        self.tabel.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

    def refresh(self):
        semua = self.app.service.tampilkan_semua()
        opsi_kat = ["Semua Kategori"] + list(self.app.kategori)
        self.filter_kat.configure(values=opsi_kat)
        if self.filter_kat.get() not in opsi_kat:
            self.filter_kat.set("Semua Kategori")

        pilihan = self.filter.get()
        kat_pilihan = self.filter_kat.get()
        kata = self.entry_cari.get().strip().lower()

        baris, tags = [], []
        for t in reversed(semua):
            if pilihan != "Semua" and t.jenis() != pilihan:
                continue
            if kat_pilihan != "Semua Kategori" and t.kategori.nama != kat_pilihan:
                continue
            tgl_str = f"{t.tanggal:%d-%m-%Y}"
            nominal_str = format_rupiah(t.jumlah)
            if kata and kata not in t.kategori.nama.lower() and kata not in tgl_str and kata not in nominal_str.lower():
                continue
            masuk = t.jenis() == "Pemasukan"
            baris.append((t.id, tgl_str, t.jenis(), t.kategori.nama, f"{'+' if masuk else '-'}{nominal_str}"))
            tags.append("pemasukan" if masuk else "pengeluaran")
        self.judul_tabel.configure(text=f"Riwayat Transaksi  ·  {len(baris)} data")
        self.tabel.isi(baris, tags)


# -------------------------------------------------------------- kategori
class KategoriPage(ctk.CTkFrame):
    def __init__(self, app: App):
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=2, uniform="k")
        self.grid_columnconfigure(1, weight=3, uniform="k")
        self.grid_rowconfigure(1, weight=1)

        buat_header(
            self, "Kategori & Anggaran", "Atur kategori dan batas anggaran bulanan."
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        kiri = Card(self)
        kiri.grid(row=1, column=0, sticky="nsew", padx=(0, 7))
        kiri.grid_columnconfigure(0, weight=1)
        kiri.grid_rowconfigure(5, weight=1)
        ctk.CTkLabel(kiri, text="Kategori Baru", font=font(15, True), text_color=PALET["text"]).grid(
            row=0, column=0, sticky="w", padx=22, pady=(20, 12)
        )
        self.entry_nama = entry(kiri, placeholder_text="Nama kategori")
        self.entry_nama.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 8))
        self.entry_anggaran = entry(kiri, placeholder_text="Anggaran bulanan (opsional)")
        self.entry_anggaran.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 12))
        ctk.CTkButton(
            kiri, text="Tambah Kategori", height=42, corner_radius=10, font=font(13, True),
            fg_color=PALET["primary"], hover_color=PALET["primary_hover"], command=self.tambah,
        ).grid(row=3, column=0, sticky="ew", padx=22, pady=(0, 8))
        self.status = StatusBar(kiri, wrap=300)
        self.status.grid(row=4, column=0, sticky="ew", padx=22, pady=(0, 8))
        self.daftar_box = ctk.CTkScrollableFrame(kiri, fg_color=PALET["card_alt"], corner_radius=12)
        self.daftar_box.grid(row=5, column=0, sticky="nsew", padx=22, pady=(0, 20))
        self.daftar_box.grid_columnconfigure(0, weight=1)

        kanan = Card(self)
        kanan.grid(row=1, column=1, sticky="nsew", padx=(7, 0))
        kanan.grid_columnconfigure(0, weight=1)
        kanan.grid_rowconfigure(1, weight=1)
        self.judul_ang = ctk.CTkLabel(kanan, text="Penggunaan Anggaran", font=font(15, True),
                                      text_color=PALET["text"])
        self.judul_ang.grid(row=0, column=0, sticky="w", padx=22, pady=(20, 12))
        self.box_ang = ctk.CTkScrollableFrame(kanan, fg_color="transparent")
        self.box_ang.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

    def tambah(self):
        nama = self.entry_nama.get().strip()
        if any(k.lower() == nama.lower() for k in self.app.kategori):
            self.status.tampil("Gagal: kategori sudah ada.", error=True)
            return
        try:
            teks = self.entry_anggaran.get().strip()
            anggaran = parse_rupiah(teks, minimum=0) if teks else 0
            baru = Kategori(nama, anggaran)  # validasi nama kosong ada di class Kategori
        except ValueError as e:
            self.status.tampil(f"Gagal: {e}", error=True)
            return
        self.app.kategori[baru.nama] = baru
        self.entry_nama.delete(0, "end")
        self.entry_anggaran.delete(0, "end")
        self.status.tampil(f"Kategori ditambahkan: {baru}")
        self.app.refresh_semua()

    def refresh(self):
        for w in self.daftar_box.winfo_children():
            w.destroy()
        for idx, kat in enumerate(self.app.kategori.values()):
            baris = ctk.CTkFrame(self.daftar_box, fg_color="transparent")
            baris.grid(row=idx, column=0, sticky="ew", padx=6, pady=4)
            baris.grid_columnconfigure(1, weight=1)
            ctk.CTkFrame(baris, width=10, height=10, corner_radius=5,
                         fg_color=SERI[idx % len(SERI)]).grid(row=0, column=0, padx=(0, 10))
            ctk.CTkLabel(baris, text=kat.nama, font=font(12, True), text_color=PALET["text"]).grid(
                row=0, column=1, sticky="w"
            )
            teks_ang = format_rupiah(kat.anggaran) if kat.anggaran > 0 else "Tanpa batas"
            ctk.CTkLabel(baris, text=teks_ang, font=font(11), text_color=PALET["muted"]).grid(
                row=0, column=2, sticky="e"
            )

        hari = date.today()
        self.judul_ang.configure(text=f"Penggunaan Anggaran  ·  {BULAN_ID[hari.month - 1]} {hari.year}")
        render_progres(
            self.box_ang, self.app.kategori,
            self.app.pengeluaran_per_kategori(hari.year, hari.month),
            kosong="Belum ada kategori dengan batas anggaran.\nIsi kolom anggaran saat menambah kategori.",
        )


# --------------------------------------------------------------- laporan
class LaporanPage(ctk.CTkFrame):
    TAB = ["Ringkasan", "Rekap Kategori", "Transaksi"]

    def __init__(self, app: App):
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        buat_header(
            self, "Laporan Bulanan",
            "Ringkasan arus kas, progres anggaran, dan rincian transaksi per bulan.",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 14))

        kontrol_card = Card(self)
        kontrol_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        kontrol = ctk.CTkFrame(kontrol_card, fg_color="transparent")
        kontrol.pack(fill="x", padx=16, pady=12)

        hari = date.today()
        nav = dict(width=36, height=38, corner_radius=10, fg_color=PALET["chip"],
                   hover_color=PALET["chip_hover"], text_color=PALET["text"])
        ctk.CTkButton(kontrol, text="<", command=lambda: self._geser_bulan(-1), font=font(14, True), **nav).pack(
            side="left", padx=(0, 4)
        )
        self.menu_bulan = option(kontrol, values=BULAN_ID, width=130, height=38,
                                 command=lambda _: self.tampilkan(diam=True))
        self.menu_bulan.set(BULAN_ID[hari.month - 1])
        self.menu_bulan.pack(side="left", padx=(0, 4))
        ctk.CTkButton(kontrol, text=">", command=lambda: self._geser_bulan(1), font=font(14, True), **nav).pack(
            side="left", padx=(0, 16)
        )
        ctk.CTkLabel(kontrol, text="TAHUN", font=font(10, True), text_color=PALET["muted"]).pack(
            side="left", padx=(0, 6)
        )
        self.entry_tahun = entry(kontrol, width=80, height=38)
        self.entry_tahun.insert(0, str(hari.year))
        self.entry_tahun.pack(side="left", padx=(0, 16))
        ctk.CTkLabel(kontrol, text="KATEGORI", font=font(10, True), text_color=PALET["muted"]).pack(
            side="left", padx=(0, 6)
        )
        self.menu_kategori = option(kontrol, values=["(semua)"], width=150, height=38,
                                    command=lambda _: self.tampilkan(diam=True))
        self.menu_kategori.pack(side="left", padx=(0, 12))
        ctk.CTkButton(
            kontrol, text="Tampilkan", width=108, height=38, corner_radius=10, font=font(12, True),
            fg_color=PALET["primary"], hover_color=PALET["primary_hover"],
            command=lambda: self.tampilkan(diam=False),
        ).pack(side="right")

        ringkasan = ctk.CTkFrame(self, fg_color="transparent")
        ringkasan.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        ringkasan.grid_columnconfigure((0, 1, 2), weight=1, uniform="k")
        self.kpi_masuk = KpiCard(ringkasan, "Total Pemasukan", PALET["emerald"])
        self.kpi_keluar = KpiCard(ringkasan, "Total Pengeluaran", PALET["rose"])
        self.kpi_saldo = KpiCard(ringkasan, "Arus Kas", PALET["primary"])
        for i, k in enumerate((self.kpi_masuk, self.kpi_keluar, self.kpi_saldo)):
            k.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 12, 0))

        area = ctk.CTkFrame(self, fg_color="transparent")
        area.grid(row=3, column=0, sticky="nsew")
        area.grid_columnconfigure(0, weight=1)
        area.grid_rowconfigure(1, weight=1)
        self.seg = segmen(area, values=self.TAB, command=self._ganti_tab)
        self.seg.set(self.TAB[0])
        self.seg.grid(row=0, column=0, sticky="w", pady=(0, 10))

        konten = Card(area)
        konten.grid(row=1, column=0, sticky="nsew")
        konten.grid_columnconfigure(0, weight=1)
        konten.grid_rowconfigure(0, weight=1)

        # Tab Ringkasan
        self.tab_ringkasan = ctk.CTkFrame(konten, fg_color="transparent")
        self.tab_ringkasan.grid_columnconfigure((0, 1), weight=1, uniform="r")
        self.tab_ringkasan.grid_rowconfigure(0, weight=1)
        kiri = ctk.CTkFrame(self.tab_ringkasan, fg_color="transparent")
        kiri.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=16)
        ctk.CTkLabel(kiri, text="Komposisi Pengeluaran", font=font(14, True), text_color=PALET["text"]).pack(
            anchor="w", pady=(0, 8)
        )
        self.donut = DonutChart(kiri)
        self.donut.pack(anchor="w", pady=(4, 0))
        kanan = ctk.CTkFrame(self.tab_ringkasan, fg_color="transparent")
        kanan.grid(row=0, column=1, sticky="nsew", padx=(10, 12), pady=16)
        kanan.grid_columnconfigure(0, weight=1)
        kanan.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(kanan, text="Progres Anggaran", font=font(14, True), text_color=PALET["text"]).grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        self.anggaran_box = ctk.CTkScrollableFrame(kanan, fg_color="transparent")
        self.anggaran_box.grid(row=1, column=0, sticky="nsew")

        # Tab Rekap
        self.tab_rekap = ctk.CTkFrame(konten, fg_color="transparent")
        self.tab_rekap.grid_columnconfigure(0, weight=1)
        self.tab_rekap.grid_rowconfigure(0, weight=1)
        self.tabel_rekap = Tabel(
            self.tab_rekap,
            [("Jenis", 95, "center"), ("Kategori", 130, "w"), ("Total", 130, "e"),
             ("Anggaran", 130, "e"), ("Status", 170, "w")],
            teks_kosong="Belum ada rekap pada bulan ini.",
        )
        self.tabel_rekap.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)

        # Tab Transaksi
        self.tab_transaksi = ctk.CTkFrame(konten, fg_color="transparent")
        self.tab_transaksi.grid_columnconfigure(0, weight=1)
        self.tab_transaksi.grid_rowconfigure(1, weight=1)
        self.judul_transaksi = ctk.CTkLabel(self.tab_transaksi, text="Transaksi Bulan Ini",
                                            font=font(14, True), text_color=PALET["text"])
        self.judul_transaksi.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        self.tabel_transaksi = Tabel(
            self.tab_transaksi,
            [("ID", 60, "center"), ("Tanggal", 120, "center"), ("Jenis", 110, "center"),
             ("Kategori", 170, "w"), ("Jumlah", 150, "e")],
            teks_kosong="Tidak ada transaksi pada periode ini.",
        )
        self.tabel_transaksi.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

        self.frames_tab = {
            self.TAB[0]: self.tab_ringkasan, self.TAB[1]: self.tab_rekap, self.TAB[2]: self.tab_transaksi,
        }
        for f in self.frames_tab.values():
            f.grid(row=0, column=0, sticky="nsew")
        self._ganti_tab(self.TAB[0])

    def _ganti_tab(self, nama: str):
        self.frames_tab[nama].tkraise()

    def _geser_bulan(self, delta: int):
        idx = BULAN_ID.index(self.menu_bulan.get()) + delta
        try:
            tahun = int(self.entry_tahun.get())
        except ValueError:
            tahun = date.today().year
        if idx < 0:
            idx, tahun = 11, tahun - 1
        elif idx > 11:
            idx, tahun = 0, tahun + 1
        self.menu_bulan.set(BULAN_ID[idx])
        self.entry_tahun.delete(0, "end")
        self.entry_tahun.insert(0, str(tahun))
        self.tampilkan(diam=True)

    def tampilkan(self, diam: bool = False):
        """diam=True: dipakai saat refresh otomatis, tanpa pop-up error."""
        try:
            bulan = BULAN_ID.index(self.menu_bulan.get()) + 1
            tahun = int(self.entry_tahun.get())
            laporan = LaporanBulanan(self.app.service, bulan, tahun)
        except ValueError:
            if not diam:
                messagebox.showerror("Input salah", "Tahun harus berupa angka yang valid.")
            return

        masuk, keluar = laporan.total_pemasukan(), laporan.total_pengeluaran()
        selisih = masuk - keluar
        periode_str = f"{BULAN_ID[bulan - 1]} {tahun}"
        warna_selisih = PALET["emerald"] if selisih > 0 else (PALET["rose"] if selisih < 0 else None)
        self.kpi_masuk.set(format_rupiah(masuk), f"Periode {periode_str}")
        self.kpi_keluar.set(format_rupiah(keluar), f"Periode {periode_str}")
        self.kpi_saldo.set(format_rupiah(selisih), "Surplus" if selisih >= 0 else "Defisit",
                           warna_selisih, warna_selisih)

        rekap = laporan.rekap_per_kategori()
        baris, tags = [], []
        for r in rekap:
            kat = self.app.kategori.get(r.nama_kategori)
            anggaran = kat.anggaran if kat else 0
            if r.jenis == "pengeluaran" and anggaran > 0:
                if r.total > anggaran:
                    status = f"Melebihi {format_rupiah(r.total - anggaran)}"
                    tags.append("pengeluaran")
                else:
                    status = f"Sisa {format_rupiah(anggaran - r.total)}"
                    tags.append("pemasukan")
                teks_anggaran = format_rupiah(anggaran)
            else:
                status, teks_anggaran = "-", "-"
                tags.append("pemasukan" if r.jenis == "pemasukan" else "pengeluaran")
            baris.append((r.jenis.capitalize(), r.nama_kategori, format_rupiah(r.total), teks_anggaran, status))
        self.tabel_rekap.isi(baris, tags)

        pengeluaran = {r.nama_kategori: r.total for r in rekap if r.jenis == "pengeluaran"}
        self.donut.gambar(list(pengeluaran.items()), judul_tengah=BULAN_PENDEK[bulan - 1])
        render_progres(self.anggaran_box, self.app.kategori, pengeluaran)

        pilihan = self.menu_kategori.get()
        if pilihan == "(semua)":
            daftar = laporan.transaksi_bulan_ini()
            self.judul_transaksi.configure(text=f"Transaksi {periode_str}")
        else:
            daftar = laporan.transaksi_per_kategori(pilihan)
            self.judul_transaksi.configure(text=f"Transaksi {pilihan} ({periode_str})")

        trx_baris = [
            (t.id, f"{t.tanggal:%d-%m-%Y}", t.jenis(), t.kategori.nama, format_rupiah(t.jumlah))
            for t in daftar
        ]
        trx_tags = ["pemasukan" if t.jenis() == "Pemasukan" else "pengeluaran" for t in daftar]
        self.tabel_transaksi.isi(trx_baris, trx_tags)

    def refresh(self):
        nilai = ["(semua)"] + list(self.app.kategori)
        self.menu_kategori.configure(values=nilai)
        if self.menu_kategori.get() not in nilai:
            self.menu_kategori.set("(semua)")
        self.tampilkan(diam=True)


if __name__ == "__main__":
    App().mainloop()
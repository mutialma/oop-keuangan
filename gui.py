from datetime import date, datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from models import Kategori
from reports import LaporanBulanan
from reports.laporan_bulanan import format_rupiah
from services import KeuanganService

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

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
    """Samakan warna ttk.Treeview dengan mode terang/gelap CustomTkinter."""
    gelap = ctk.get_appearance_mode() == "Dark"
    bg = "#2b2b2b" if gelap else "#ffffff"
    fg = "#dce4ee" if gelap else "#1a1a1a"
    head = "#3a3a3a" if gelap else "#e5e5e5"
    gaya = ttk.Style()
    gaya.theme_use("default")
    gaya.configure("Treeview", background=bg, foreground=fg, fieldbackground=bg,
                   rowheight=26, borderwidth=0)
    gaya.map("Treeview", background=[("selected", "#1f6aa5")],
             foreground=[("selected", "#ffffff")])
    gaya.configure("Treeview.Heading", background=head, foreground=fg,
                   relief="flat", font=("Segoe UI", 10, "bold"))
    gaya.map("Treeview.Heading", background=[("active", head)])


class Tabel(ctk.CTkFrame):
    """Tabel (ttk.Treeview) + scrollbar. kolom = [(judul, lebar, rata), ...]"""

    def __init__(self, master, kolom):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        ids = [f"c{i}" for i in range(len(kolom))]
        self.tree = ttk.Treeview(self, columns=ids, show="headings", height=6)
        for cid, (judul, lebar, rata) in zip(ids, kolom):
            self.tree.heading(cid, text=judul)
            self.tree.column(cid, width=lebar, anchor=rata, stretch=True)
        bar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=bar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        bar.grid(row=0, column=1, sticky="ns")

    def isi(self, baris) -> None:
        self.tree.delete(*self.tree.get_children())
        for b in baris:
            self.tree.insert("", "end", values=b)


def kartu(master, judul: str):
    """Kartu ringkasan kecil; return label nilainya."""
    frame = ctk.CTkFrame(master)
    ctk.CTkLabel(frame, text=judul, text_color=("gray30", "gray70")).pack(
        anchor="w", padx=14, pady=(10, 0))
    nilai = ctk.CTkLabel(frame, text="-", font=ctk.CTkFont(size=18, weight="bold"))
    nilai.pack(anchor="w", padx=14, pady=(0, 10))
    return frame, nilai

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Keuangan")
        self.geometry("1000x680")
        self.minsize(900, 600)
        terapkan_gaya_tabel()

        # objek dari tugas OOP sebelumnya
        self.service = KeuanganService()
        self.kategori: dict[str, Kategori] = {
            "Gaji": Kategori("Gaji"),
            "Makan": Kategori("Makan", 500_000),
            "Transport": Kategori("Transport", 200_000),
        }

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._buat_sidebar()

        self.halaman = {
            "catat": CatatPage(self),
            "daftar": DaftarPage(self),
            "laporan": LaporanPage(self),
        }
        for frame in self.halaman.values():
            frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.buka("catat")

    def _buat_sidebar(self):
        bar = ctk.CTkFrame(self, width=190, corner_radius=0)
        bar.grid(row=0, column=0, sticky="nsew")
        bar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(bar, text="Keuangan", font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(20, 15))
        menu = [("Catat Transaksi", "catat"), ("Daftar & Saldo", "daftar"),
                ("Laporan Bulanan", "laporan")]
        self.tombol_menu = {}
        for i, (teks, kunci) in enumerate(menu, start=1):
            tombol = ctk.CTkButton(
                bar, text=teks, anchor="w", fg_color="transparent",
                text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                command=lambda k=kunci: self.buka(k))
            tombol.grid(row=i, column=0, padx=10, pady=4, sticky="ew")
            self.tombol_menu[kunci] = tombol

        ctk.CTkLabel(bar, text="Tema").grid(row=6, column=0, padx=20, sticky="w")
        ctk.CTkOptionMenu(bar, values=["system", "light", "dark"],
                          command=self.ganti_tema).grid(row=7, column=0, padx=20, pady=(0, 20))

    def ganti_tema(self, mode: str):
        ctk.set_appearance_mode(mode)
        self.after(100, terapkan_gaya_tabel)

    def buka(self, kunci: str):
        for k, tombol in self.tombol_menu.items():
            tombol.configure(fg_color=("gray75", "gray25") if k == kunci else "transparent")
        self.halaman[kunci].tkraise()
        self.refresh_semua()

    def refresh_semua(self):
        for frame in self.halaman.values():
            frame.refresh()

class CatatPage(ctk.CTkFrame):
    def __init__(self, app: App):
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Catat Transaksi", font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        self.jenis = ctk.CTkSegmentedButton(self, values=["Pemasukan", "Pengeluaran"])
        self.jenis.set("Pemasukan")
        self.jenis.grid(row=1, column=0, columnspan=2, sticky="w", pady=6)

        ctk.CTkLabel(self, text="Jumlah (Rp)").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_jumlah = ctk.CTkEntry(self, placeholder_text="contoh: 35000")
        self.entry_jumlah.grid(row=2, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(self, text="Kategori").grid(row=3, column=0, sticky="w", pady=6)
        self.menu_kategori = ctk.CTkOptionMenu(self, values=list(app.kategori))
        self.menu_kategori.grid(row=3, column=1, sticky="w", pady=6)

        ctk.CTkLabel(self, text="Tanggal").grid(row=4, column=0, sticky="w", pady=6)
        self.entry_tanggal = ctk.CTkEntry(self)
        self.entry_tanggal.insert(0, date.today().isoformat())
        self.entry_tanggal.grid(row=4, column=1, sticky="ew", pady=6)

        ctk.CTkButton(self, text="Simpan Transaksi", command=self.simpan).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(10, 4))
        self.status = ctk.CTkLabel(self, text="", wraplength=520, justify="left")
        self.status.grid(row=6, column=0, columnspan=2, sticky="w")

        ctk.CTkLabel(self, text="Tambah Kategori", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=7, column=0, columnspan=2, sticky="w", pady=(25, 6))
        ctk.CTkLabel(self, text="Nama").grid(row=8, column=0, sticky="w", pady=6)
        self.entry_nama_kat = ctk.CTkEntry(self)
        self.entry_nama_kat.grid(row=8, column=1, sticky="ew", pady=6)
        ctk.CTkLabel(self, text="Anggaran (opsional)").grid(row=9, column=0, sticky="w", pady=6)
        self.entry_anggaran = ctk.CTkEntry(self, placeholder_text="kosongkan jika tanpa anggaran")
        self.entry_anggaran.grid(row=9, column=1, sticky="ew", pady=6)
        ctk.CTkButton(self, text="Tambah Kategori", command=self.tambah_kategori).grid(
            row=10, column=0, columnspan=2, sticky="w", pady=6)

    def _pesan(self, teks: str, error: bool = False):
        self.status.configure(text=teks, text_color="#d9534f" if error else "#2e8b57")

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
            self._pesan(f"Gagal: {e}", error=True)
            return
        self._pesan(f"Tersimpan: {transaksi}")
        self.entry_jumlah.delete(0, "end")
        self.app.refresh_semua()

    def tambah_kategori(self):
        nama = self.entry_nama_kat.get().strip()
        if any(k.lower() == nama.lower() for k in self.app.kategori):
            self._pesan("Gagal: kategori sudah ada.", error=True)
            return
        try:
            teks = self.entry_anggaran.get().strip()
            anggaran = parse_rupiah(teks, minimum=0) if teks else 0
            baru = Kategori(nama, anggaran)  # validasi nama kosong ada di class Kategori
        except ValueError as e:
            self._pesan(f"Gagal: {e}", error=True)
            return
        self.app.kategori[baru.nama] = baru
        self.entry_nama_kat.delete(0, "end")
        self.entry_anggaran.delete(0, "end")
        self._pesan(f"Kategori ditambahkan: {baru}")
        self.app.refresh_semua()

    def refresh(self):
        nilai = list(self.app.kategori)
        self.menu_kategori.configure(values=nilai)
        if self.menu_kategori.get() not in nilai:
            self.menu_kategori.set(nilai[0])

class DaftarPage(ctk.CTkFrame):
    def __init__(self, app: App):
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self, text="Daftar Transaksi & Saldo",
                     font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w")
        self.label_saldo = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16))
        self.label_saldo.grid(row=1, column=0, sticky="w", pady=(8, 8))

        self.filter = ctk.CTkSegmentedButton(
            self, values=["Semua", "Pemasukan", "Pengeluaran"], command=lambda _: self.refresh())
        self.filter.set("Semua")
        self.filter.grid(row=2, column=0, sticky="w", pady=(0, 8))

        self.tabel = Tabel(self, [("ID", 50, "center"), ("Tanggal", 110, "center"),
                                  ("Jenis", 110, "center"), ("Kategori", 160, "w"),
                                  ("Jumlah", 140, "e")])
        self.tabel.grid(row=3, column=0, sticky="nsew")

    def refresh(self):
        self.label_saldo.configure(text=str(self.app.service))  # "Saldo: Rp... (n transaksi)"
        pilihan = self.filter.get()
        baris = [
            (t.id, f"{t.tanggal:%d-%m-%Y}", t.jenis(), t.kategori.nama, format_rupiah(t.jumlah))
            for t in self.app.service.tampilkan_semua()
            if pilihan == "Semua" or t.jenis() == pilihan
        ]
        self.tabel.isi(baris)

class LaporanPage(ctk.CTkFrame):
    def __init__(self, app: App):
        super().__init__(app, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(6, weight=2)

        ctk.CTkLabel(self, text="Laporan Bulanan", font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8))

        kontrol = ctk.CTkFrame(self, fg_color="transparent")
        kontrol.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        hari_ini = date.today()
        ctk.CTkLabel(kontrol, text="Bulan").pack(side="left")
        self.entry_bulan = ctk.CTkEntry(kontrol, width=50)
        self.entry_bulan.insert(0, str(hari_ini.month))
        self.entry_bulan.pack(side="left", padx=(5, 12))
        ctk.CTkLabel(kontrol, text="Tahun").pack(side="left")
        self.entry_tahun = ctk.CTkEntry(kontrol, width=70)
        self.entry_tahun.insert(0, str(hari_ini.year))
        self.entry_tahun.pack(side="left", padx=(5, 12))
        ctk.CTkLabel(kontrol, text="Kategori").pack(side="left")
        self.menu_kategori = ctk.CTkOptionMenu(kontrol, values=["(semua)"], width=130)
        self.menu_kategori.pack(side="left", padx=(5, 12))
        ctk.CTkButton(kontrol, text="Tampilkan", width=90,
                      command=lambda: self.tampilkan(diam=False)).pack(side="left")

        ringkasan = ctk.CTkFrame(self, fg_color="transparent")
        ringkasan.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ringkasan.grid_columnconfigure((0, 1, 2), weight=1, uniform="k")
        self.kartu_masuk, self.nilai_masuk = kartu(ringkasan, "Total Pemasukan")
        self.kartu_keluar, self.nilai_keluar = kartu(ringkasan, "Total Pengeluaran")
        self.kartu_saldo, self.nilai_saldo = kartu(ringkasan, "Saldo Bulan Ini")
        for i, k in enumerate((self.kartu_masuk, self.kartu_keluar, self.kartu_saldo)):
            k.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0))

        ctk.CTkLabel(self, text="Rekap per Kategori", font=ctk.CTkFont(weight="bold")).grid(
            row=3, column=0, sticky="w")
        self.tabel_rekap = Tabel(self, [("Jenis", 100, "center"), ("Kategori", 150, "w"),
                                        ("Total", 130, "e"), ("Anggaran", 130, "e"),
                                        ("Status", 190, "w")])
        self.tabel_rekap.grid(row=4, column=0, sticky="nsew", pady=(2, 8))

        self.judul_transaksi = ctk.CTkLabel(self, text="Transaksi", font=ctk.CTkFont(weight="bold"))
        self.judul_transaksi.grid(row=5, column=0, sticky="w")
        self.tabel_transaksi = Tabel(self, [("ID", 50, "center"), ("Tanggal", 110, "center"),
                                            ("Jenis", 110, "center"), ("Kategori", 160, "w"),
                                            ("Jumlah", 140, "e")])
        self.tabel_transaksi.grid(row=6, column=0, sticky="nsew", pady=(2, 0))

    def tampilkan(self, diam: bool = False):
        """diam=True: dipakai saat refresh otomatis, tanpa pop-up error."""
        try:
            bulan = int(self.entry_bulan.get())
            tahun = int(self.entry_tahun.get())
            laporan = LaporanBulanan(self.app.service, bulan, tahun)  # validasi bulan 1-12
        except ValueError:
            if not diam:
                messagebox.showerror("Input salah", "Bulan harus 1-12 dan tahun harus berupa angka.")
            return

        masuk, keluar = laporan.total_pemasukan(), laporan.total_pengeluaran()
        self.nilai_masuk.configure(text=format_rupiah(masuk))
        self.nilai_keluar.configure(text=format_rupiah(keluar))
        self.nilai_saldo.configure(text=format_rupiah(masuk - keluar))

        baris = []
        for r in laporan.rekap_per_kategori():
            kat = self.app.kategori.get(r.nama_kategori)
            anggaran = kat.anggaran if kat else 0
            if r.jenis == "pengeluaran" and anggaran > 0:
                if r.total > anggaran:
                    status = f"Melebihi {format_rupiah(r.total - anggaran)}"
                else:
                    status = f"Sisa {format_rupiah(anggaran - r.total)}"
                teks_anggaran = format_rupiah(anggaran)
            else:
                status, teks_anggaran = "-", "-"
            baris.append((r.jenis.capitalize(), r.nama_kategori, format_rupiah(r.total),
                          teks_anggaran, status))
        self.tabel_rekap.isi(baris)

        pilihan = self.menu_kategori.get()
        if pilihan == "(semua)":
            daftar = laporan.transaksi_bulan_ini()
            self.judul_transaksi.configure(text="Transaksi Bulan Ini")
        else:
            daftar = laporan.transaksi_per_kategori(pilihan)
            self.judul_transaksi.configure(text=f"Transaksi Kategori {pilihan}")
        self.tabel_transaksi.isi(
            [(t.id, f"{t.tanggal:%d-%m-%Y}", t.jenis(), t.kategori.nama, format_rupiah(t.jumlah))
             for t in daftar])

    def refresh(self):
        nilai = ["(semua)"] + list(self.app.kategori)
        self.menu_kategori.configure(values=nilai)
        if self.menu_kategori.get() not in nilai:
            self.menu_kategori.set("(semua)")
        self.tampilkan(diam=True)


if __name__ == "__main__":
    App().mainloop()

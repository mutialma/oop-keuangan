from models import Pemasukan, Pengeluaran
from services import KeuanganService


def format_rupiah(angka: float) -> str:
    return "Rp" + f"{angka:,.0f}".replace(",", ".")


class BarisRekap:
    """Satu baris rekap: total per kategori."""

    def __init__(self, nama_kategori: str, jenis: str, total: float):
        self.nama_kategori = nama_kategori
        self.jenis = jenis
        self.total = total

    def __str__(self):
        jenis = self.jenis.upper()
        return f"[{jenis}] {self.nama_kategori} | Total: {format_rupiah(self.total)}"


class LaporanBulanan:
    """Laporan keuangan untuk satu bulan tertentu."""

    def __init__(self, service: KeuanganService, bulan: int, tahun: int):
        if bulan < 1 or bulan > 12:
            raise ValueError(f"Bulan tidak valid: {bulan}")

        self.service = service
        self.bulan = bulan
        self.tahun = tahun

    def transaksi_bulan_ini(self):
        semua = self.service.tampilkan_semua()
        return [
            t for t in semua
            if t.tanggal.month == self.bulan and t.tanggal.year == self.tahun
        ]

    def transaksi_per_kategori(self, nama_kategori: str):
        return [
            t for t in self.transaksi_bulan_ini()
            if t.kategori.nama.lower() == nama_kategori.lower()
        ]

    def total_pemasukan(self):
        semua = self.transaksi_bulan_ini()
        return sum(t.jumlah for t in semua if isinstance(t, Pemasukan))

    def total_pengeluaran(self):
        semua = self.transaksi_bulan_ini()
        return sum(t.jumlah for t in semua if isinstance(t, Pengeluaran))

    def rekap_per_kategori(self):
        rekap = {}
        for t in self.transaksi_bulan_ini():
            jenis = "pemasukan" if isinstance(t, Pemasukan) else "pengeluaran"
            kunci = (jenis, t.kategori.nama)
            rekap[kunci] = rekap.get(kunci, 0) + t.jumlah

        return [
            BarisRekap(nama, jenis, total)
            for (jenis, nama), total in rekap.items()
        ]

    def __str__(self):
        saldo = self.total_pemasukan() - self.total_pengeluaran()
        return (
            f"Laporan {self.bulan}/{self.tahun} | "
            f"Pemasukan: {format_rupiah(self.total_pemasukan())} | "
            f"Pengeluaran: {format_rupiah(self.total_pengeluaran())} | "
            f"Saldo: {format_rupiah(saldo)}"
        )

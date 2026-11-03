from datetime import date

from models import Pemasukan, Pengeluaran


class KeuanganService:
    def __init__(self):
        self._daftar_transaksi = []

    def _id_baru(self):
        return len(self._daftar_transaksi) + 1

    def catat_pemasukan(self, jumlah, kategori, tanggal=None):

        transaksi = Pemasukan(self._id_baru(), jumlah, tanggal or date.today(), kategori)
        self._daftar_transaksi.append(transaksi)
        return transaksi

    def catat_pengeluaran(self, jumlah, kategori, tanggal=None):
        transaksi = Pengeluaran(self._id_baru(), jumlah, tanggal or date.today(), kategori)
        if transaksi.jumlah > self.hitung_saldo():
            raise ValueError("Saldo tidak cukup")
        self._daftar_transaksi.append(transaksi)
        return transaksi

    def hitung_saldo(self):

        return sum(t.nilai_bersih() for t in self._daftar_transaksi)

    def tampilkan_semua(self):

        return list(self._daftar_transaksi)

    def __len__(self):
        return len(self._daftar_transaksi)

    def __iter__(self):
        return iter(self._daftar_transaksi)

    def __str__(self):
        saldo = f"{self.hitung_saldo():,.0f}".replace(",", ".")
        return f"Saldo: Rp{saldo} ({len(self)} transaksi)"


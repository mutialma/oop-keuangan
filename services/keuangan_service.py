from models import Kategori, Pemasukan, Pengeluaran


class KeuanganService:
    def __init__(self):
        self._daftar_transaksi = []

    def _validasi(self, jumlah, kategori):
        if not isinstance(kategori, Kategori):
            raise TypeError("kategori harus berupa objek Kategori")
        if jumlah <= 0:
            raise ValueError("Jumlah harus lebih dari 0")

    def _id_baru(self):
        return len(self._daftar_transaksi) + 1

    def catat_pemasukan(self, jumlah, kategori, keterangan="", tanggal=None):
        self._validasi(jumlah, kategori)
        transaksi = Pemasukan(self._id_baru(), jumlah, kategori, keterangan, tanggal)
        self._daftar_transaksi.append(transaksi)
        return transaksi

    def catat_pengeluaran(self, jumlah, kategori, keterangan="", tanggal=None):
        self._validasi(jumlah, kategori)
        if jumlah > self.hitung_saldo():
            raise ValueError("Saldo tidak cukup")
        transaksi = Pengeluaran(self._id_baru(), jumlah, kategori, keterangan, tanggal)
        self._daftar_transaksi.append(transaksi)
        return transaksi

    def hitung_saldo(self):

        return sum(t.efek_saldo() for t in self._daftar_transaksi)

    def semua_transaksi(self):
        """Dipakai Anggota 3 (reports/) untuk rekap dan filter."""
        return list(self._daftar_transaksi)


    def __len__(self):
        return len(self._daftar_transaksi)

    def __iter__(self):
        return iter(self._daftar_transaksi)

    def __str__(self):
        saldo = f"{self.hitung_saldo():,}".replace(",", ".")
        return f"Saldo: Rp{saldo} ({len(self)} transaksi)"

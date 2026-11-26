from datetime import date

from models import Pemasukan, Pengeluaran


class KeuanganService:
    def __init__(self):
        self._daftar_transaksi = []

    def _id_baru(self) -> int:
        """Menghasilkan ID unik berikutnya (selalu lebih besar dari ID terbesar yang ada)."""
        if not self._daftar_transaksi:
            return 1
        return max(t.id for t in self._daftar_transaksi) + 1

    def catat_pemasukan(self, jumlah: float, kategori, tanggal: date = None) -> Pemasukan:
        transaksi = Pemasukan(self._id_baru(), jumlah, tanggal or date.today(), kategori)
        self._daftar_transaksi.append(transaksi)
        return transaksi

    def catat_pengeluaran(self, jumlah: float, kategori, tanggal: date = None) -> Pengeluaran:
        transaksi = Pengeluaran(self._id_baru(), jumlah, tanggal or date.today(), kategori)
        if transaksi.jumlah > self.hitung_saldo():
            raise ValueError("Saldo tidak cukup")
        self._daftar_transaksi.append(transaksi)
        return transaksi

    def cari_by_id(self, id_transaksi: int):
        """Mengembalikan objek transaksi berdasarkan ID, atau None jika tidak ditemukan."""
        for t in self._daftar_transaksi:
            if t.id == id_transaksi:
                return t
        return None

    def hapus_transaksi(self, id_transaksi: int) -> None:
        """Menghapus transaksi berdasarkan ID.

        Raises:
            ValueError: Jika ID tidak ditemukan, atau jika penghapusan pemasukan
                        menyebabkan saldo menjadi negatif.
        """
        target = self.cari_by_id(id_transaksi)
        if target is None:
            raise ValueError(f"Transaksi dengan ID {id_transaksi} tidak ditemukan.")

        # Simulasikan saldo setelah dihapus
        saldo_setelah = self.hitung_saldo() - target.nilai_bersih()
        if saldo_setelah < 0:
            raise ValueError(
                "Tidak dapat menghapus: saldo akan menjadi negatif setelah penghapusan."
            )

        self._daftar_transaksi = [t for t in self._daftar_transaksi if t.id != id_transaksi]

    def edit_transaksi(self, id_transaksi: int, jumlah: float = None,
                       kategori=None, tanggal: date = None) -> object:
        """Mengedit jumlah, kategori, dan/atau tanggal transaksi berdasarkan ID.

        Transaksi yang sudah ada diganti dengan objek baru bertipe sama.
        Raises:
            ValueError: Jika ID tidak ditemukan, atau jika hasil edit menyebabkan saldo negatif.
        """
        target = self.cari_by_id(id_transaksi)
        if target is None:
            raise ValueError(f"Transaksi dengan ID {id_transaksi} tidak ditemukan.")

        jumlah_baru = jumlah if jumlah is not None else target.jumlah
        kategori_baru = kategori if kategori is not None else target.kategori
        tanggal_baru = tanggal if tanggal is not None else target.tanggal

        TipeKelas = type(target)
        baru = TipeKelas(id_transaksi, jumlah_baru, tanggal_baru, kategori_baru)

        # Hitung saldo tanpa transaksi lama, lalu terapkan transaksi baru
        saldo_tanpa = self.hitung_saldo() - target.nilai_bersih()
        if saldo_tanpa + baru.nilai_bersih() < 0:
            raise ValueError("Saldo tidak cukup setelah diedit.")

        idx = next(i for i, t in enumerate(self._daftar_transaksi) if t.id == id_transaksi)
        self._daftar_transaksi[idx] = baru
        return baru

    def hitung_saldo(self) -> float:
        return sum(t.nilai_bersih() for t in self._daftar_transaksi)

    def tampilkan_semua(self) -> list:
        return list(self._daftar_transaksi)

    def __len__(self) -> int:
        return len(self._daftar_transaksi)

    def __iter__(self):
        return iter(self._daftar_transaksi)

    def __str__(self) -> str:
        saldo = f"{self.hitung_saldo():,.0f}".replace(",", ".")
        return f"Saldo: Rp{saldo} ({len(self)} transaksi)"


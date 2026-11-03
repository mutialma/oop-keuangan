from abc import ABC, abstractmethod
from datetime import date

from .kategori import Kategori

class Transaksi(ABC):

    def __init__(self, id: int, jumlah: float, tanggal: date, kategori: Kategori):
        if jumlah <= 0:
            raise ValueError("Jumlah transaksi harus lebih besar dari nol.")
        if not isinstance(kategori, Kategori):
            raise TypeError("Kategori harus berupa objek Kategori.")

        self.id = id
        self.jumlah = float(jumlah)
        self.tanggal = tanggal
        self.kategori = kategori

    @abstractmethod
    def nilai_bersih(self) -> float:
        pass

    @abstractmethod
    def jenis(self) -> str:
        pass

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.tanggal:%d-%m-%Y} | {self.jenis()} | "
            f"{self.kategori.nama} | Rp{self.jumlah:,.0f}"
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(id={self.id}, jumlah={self.jumlah}, "
            f"tanggal={self.tanggal!r}, kategori={self.kategori.nama!r})"
        )


class Pemasukan(Transaksi):

    def nilai_bersih(self) -> float:
        return self.jumlah

    def jenis(self) -> str:
        return "Pemasukan"


class Pengeluaran(Transaksi):

    def nilai_bersih(self) -> float:
        return -self.jumlah

    def jenis(self) -> str:
        return "Pengeluaran"

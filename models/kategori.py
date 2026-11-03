class Kategori:

    def __init__(self, nama: str, anggaran: float = 0.0):
        self.nama = nama
        self.anggaran = anggaran

    @property
    def nama(self) -> str:
        return self._nama

    @nama.setter
    def nama(self, nilai: str) -> None:
        if not isinstance(nilai, str) or not nilai.strip():
            raise ValueError("Nama kategori tidak boleh kosong.")
        self._nama = nilai.strip()

    @property
    def anggaran(self) -> float:
        return self._anggaran

    @anggaran.setter
    def anggaran(self, nilai: float) -> None:
        if nilai < 0:
            raise ValueError("Anggaran tidak boleh negatif.")
        self._anggaran = float(nilai)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Kategori):
            return NotImplemented
        return self.nama.lower() == other.nama.lower()

    def __hash__(self) -> int:
        return hash(self.nama.lower())

    def __str__(self) -> str:
        return f"{self.nama} (anggaran: Rp{self.anggaran:,.0f})"

    def __repr__(self) -> str:
        return f"Kategori(nama={self.nama!r}, anggaran={self.anggaran})"

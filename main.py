from datetime import date

from models import Kategori
from reports import LaporanBulanan
from services import KeuanganService


gaji = Kategori("Gaji")
makan = Kategori("Makan", 500_000)
transport = Kategori("Transport", 200_000)


service = KeuanganService()
service.catat_pemasukan(5_000_000, gaji, date(2026, 11, 1))
service.catat_pengeluaran(35_000, makan, date(2026, 11, 2))
service.catat_pengeluaran(20_000, transport, date(2026, 11, 3))

print("=== Daftar Transaksi ===")
for transaksi in service:
    print(transaksi)

print("\n=== Saldo ===")
print(service)


print("\n=== Contoh Error ===")
try:
    service.catat_pengeluaran(10_000_000, makan)
except ValueError as e:
    print("Gagal:", e)


laporan = LaporanBulanan(service, 11, 2026)

print("\n=== Laporan Bulanan ===")
print(laporan)

print("\n=== Rekap per Kategori ===")
for baris in laporan.rekap_per_kategori():
    print(baris)

print("\n=== Transaksi Kategori Makan ===")
for transaksi in laporan.transaksi_per_kategori("Makan"):
    print(transaksi)

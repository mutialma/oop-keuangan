import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Kategori, Pemasukan, Pengeluaran
from reports import LaporanBulanan
from services import KeuanganService


class TestKeuanganService(unittest.TestCase):
    def setUp(self):
        self.service = KeuanganService()
        self.gaji = Kategori("Gaji")
        self.makan = Kategori("Makan")

    def test_awal_kosong(self):
        self.assertEqual(self.service.hitung_saldo(), 0)
        self.assertEqual(len(self.service), 0)

    def test_catat_pemasukan(self):
        t = self.service.catat_pemasukan(5_000_000, self.gaji)
        self.assertIsInstance(t, Pemasukan)
        self.assertEqual(self.service.hitung_saldo(), 5_000_000)

    def test_catat_pengeluaran(self):
        self.service.catat_pemasukan(100_000, self.gaji)
        t = self.service.catat_pengeluaran(30_000, self.makan)
        self.assertIsInstance(t, Pengeluaran)
        self.assertEqual(self.service.hitung_saldo(), 70_000)

    def test_id_bertambah(self):
        t1 = self.service.catat_pemasukan(100, self.gaji)
        t2 = self.service.catat_pemasukan(100, self.gaji)
        self.assertEqual((t1.id, t2.id), (1, 2))

    def test_tanggal_default_hari_ini(self):
        t = self.service.catat_pemasukan(100, self.gaji)
        self.assertEqual(t.tanggal, date.today())

    def test_pengeluaran_melebihi_saldo(self):
        self.service.catat_pemasukan(10_000, self.gaji)
        with self.assertRaises(ValueError):
            self.service.catat_pengeluaran(20_000, self.makan)
        self.assertEqual(self.service.hitung_saldo(), 10_000)
        self.assertEqual(len(self.service), 1)

    def test_jumlah_tidak_valid(self):
        with self.assertRaises(ValueError):
            self.service.catat_pemasukan(0, self.gaji)
        with self.assertRaises(ValueError):
            self.service.catat_pemasukan(-5, self.gaji)
        self.assertEqual(len(self.service), 0)

    def test_kategori_bukan_objek_kategori(self):
        with self.assertRaises(TypeError):
            self.service.catat_pemasukan(1000, "Gaji")

    def test_tampilkan_semua_dan_iterasi(self):
        self.service.catat_pemasukan(100_000, self.gaji)
        self.service.catat_pengeluaran(10_000, self.makan)
        self.assertEqual(len(self.service.tampilkan_semua()), 2)
        self.assertEqual([type(t) for t in self.service], [Pemasukan, Pengeluaran])

    def test_tampilkan_semua_mengembalikan_salinan(self):
        self.service.catat_pemasukan(1000, self.gaji)
        self.service.tampilkan_semua().clear()
        self.assertEqual(len(self.service), 1)

    def test_str(self):
        self.service.catat_pemasukan(1_500_000, self.gaji)
        self.assertEqual(str(self.service), "Saldo: Rp1.500.000 (1 transaksi)")

    def test_cocok_dengan_laporan_bulanan(self):
        self.service.catat_pemasukan(500_000, self.gaji, date(2026, 11, 1))
        self.service.catat_pengeluaran(40_000, self.makan, date(2026, 11, 2))
        laporan = LaporanBulanan(self.service, 11, 2026)
        self.assertEqual(laporan.total_pemasukan(), 500_000)
        self.assertEqual(laporan.total_pengeluaran(), 40_000)
        self.assertEqual(len(laporan.rekap_per_kategori()), 2)


if __name__ == "__main__":
    unittest.main()

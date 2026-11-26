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

    # ---------------------------------------------------------------- hapus
    def test_hapus_transaksi(self):
        t = self.service.catat_pemasukan(500_000, self.gaji)
        self.service.hapus_transaksi(t.id)
        self.assertEqual(len(self.service), 0)
        self.assertEqual(self.service.hitung_saldo(), 0)

    def test_hapus_id_tidak_ada(self):
        with self.assertRaises(ValueError):
            self.service.hapus_transaksi(999)

    def test_hapus_pemasukan_saldo_cukup(self):
        t1 = self.service.catat_pemasukan(1_000_000, self.gaji)
        t2 = self.service.catat_pemasukan(500_000, self.gaji)
        self.service.catat_pengeluaran(300_000, self.makan)
        # Hapus t2 (500rb): saldo jadi 1jt - 300rb = 700rb >= 0 → boleh
        self.service.hapus_transaksi(t2.id)
        self.assertEqual(self.service.hitung_saldo(), 700_000)

    def test_hapus_pemasukan_saldo_negatif_dicegah(self):
        t = self.service.catat_pemasukan(100_000, self.gaji)
        self.service.catat_pengeluaran(80_000, self.makan)
        # Hapus pemasukan 100rb: saldo jadi -80rb → harus dicegah
        with self.assertRaises(ValueError):
            self.service.hapus_transaksi(t.id)
        self.assertEqual(len(self.service), 2)

    def test_hapus_lalu_id_baru_tidak_bentrok(self):
        t1 = self.service.catat_pemasukan(100, self.gaji)
        t2 = self.service.catat_pemasukan(100, self.gaji)
        self.service.hapus_transaksi(t1.id)
        t3 = self.service.catat_pemasukan(100, self.gaji)
        ids = [t.id for t in self.service]
        self.assertEqual(len(ids), len(set(ids)), "ID harus unik setelah hapus")
        self.assertNotIn(t1.id, [t.id for t in self.service])
        self.assertIn(t2.id, [t.id for t in self.service])
        self.assertIn(t3.id, [t.id for t in self.service])

    def test_cari_by_id(self):
        t = self.service.catat_pemasukan(999, self.gaji)
        ditemukan = self.service.cari_by_id(t.id)
        self.assertIs(ditemukan, t)
        self.assertIsNone(self.service.cari_by_id(999))

    # ----------------------------------------------------------------- edit
    def test_edit_jumlah(self):
        t = self.service.catat_pemasukan(100_000, self.gaji)
        hasil = self.service.edit_transaksi(t.id, jumlah=200_000)
        self.assertIsInstance(hasil, Pemasukan)
        self.assertEqual(hasil.jumlah, 200_000)
        self.assertEqual(self.service.hitung_saldo(), 200_000)

    def test_edit_kategori(self):
        t = self.service.catat_pemasukan(100_000, self.gaji)
        hasil = self.service.edit_transaksi(t.id, kategori=self.makan)
        self.assertEqual(hasil.kategori.nama, "Makan")

    def test_edit_tanggal(self):
        t = self.service.catat_pemasukan(100_000, self.gaji)
        tgl_baru = date(2025, 1, 15)
        hasil = self.service.edit_transaksi(t.id, tanggal=tgl_baru)
        self.assertEqual(hasil.tanggal, tgl_baru)

    def test_edit_id_tidak_ada(self):
        with self.assertRaises(ValueError):
            self.service.edit_transaksi(999, jumlah=1000)

    def test_edit_pengeluaran_melebihi_saldo(self):
        self.service.catat_pemasukan(100_000, self.gaji)
        t = self.service.catat_pengeluaran(50_000, self.makan)
        with self.assertRaises(ValueError):
            self.service.edit_transaksi(t.id, jumlah=150_000)
        # Pastikan nilai lama tetap terjaga
        self.assertEqual(self.service.hitung_saldo(), 50_000)

    def test_edit_mempertahankan_posisi_urutan(self):
        t1 = self.service.catat_pemasukan(100, self.gaji)
        t2 = self.service.catat_pemasukan(200, self.gaji)
        t3 = self.service.catat_pemasukan(300, self.gaji)
        self.service.edit_transaksi(t2.id, jumlah=999)
        semua = self.service.tampilkan_semua()
        self.assertEqual([t.id for t in semua], [t1.id, t2.id, t3.id])
        self.assertEqual(semua[1].jumlah, 999)

    def test_edit_jenis_tidak_berubah(self):
        t = self.service.catat_pengeluaran.__func__  # pastikan jenis tetap Pengeluaran
        self.service.catat_pemasukan(500_000, self.gaji)
        p = self.service.catat_pengeluaran(100_000, self.makan)
        hasil = self.service.edit_transaksi(p.id, jumlah=200_000)
        self.assertIsInstance(hasil, Pengeluaran)


if __name__ == "__main__":
    unittest.main()

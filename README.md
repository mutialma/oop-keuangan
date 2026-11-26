# 💰 DompetKu — Aplikasi Keuangan Pribadi

Aplikasi keuangan pribadi berbasis Python yang dibangun dengan prinsip **Object-Oriented Programming (OOP)**. Tersedia dalam dua mode: antarmuka grafis (GUI) dan antarmuka terminal (CLI).

---

## 📸 Fitur Utama

| Fitur | Keterangan |
|---|---|
| ➕ Catat Transaksi | Tambah pemasukan & pengeluaran dengan kategori dan tanggal |
| 📋 Daftar & Saldo | Lihat semua transaksi dengan filter jenis, kategori, dan pencarian |
| 📊 Laporan Bulanan | Rekap per kategori, monitoring progres anggaran, dan arus kas bulanan |
| 🏷️ Manajemen Kategori | Buat kategori kustom dengan batas anggaran opsional |
| 🌙 Tema Terang/Gelap | Dukungan mode System, Light, dan Dark |

---

## 🗂️ Struktur Proyek

```
oop-keuangan/
│
├── gui.py                  # Antarmuka grafis (CustomTkinter)
├── main.py                 # Demo CLI / entry point terminal
├── requirements.txt        # Dependensi Python
│
├── models/                 # Layer model (entitas data)
│   ├── __init__.py
│   ├── kategori.py         # Class Kategori (nama + anggaran)
│   └── transaksi.py        # Abstract class Transaksi, Pemasukan, Pengeluaran
│
├── services/               # Layer service (logika bisnis)
│   ├── __init__.py
│   └── keuangan_service.py # KeuanganService: catat, hitung saldo, tampilkan
│
├── reports/                # Layer laporan
│   ├── __init__.py
│   └── laporan_bulanan.py  # LaporanBulanan, BarisRekap, format_rupiah
│
└── tests/                  # Unit test
    └── test_keuangan_service.py
```

---

## ⚙️ Prasyarat

- **Python 3.10+** (direkomendasikan Python 3.13)
- **customtkinter ≥ 5.2** (hanya untuk GUI)

---

## 🚀 Cara Menjalankan

### 1. Install Dependensi

```bash
pip install -r requirements.txt
```

> Jika perintah `python` tidak ditemukan, gunakan path lengkap:
> ```powershell
> & "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -m pip install -r requirements.txt
> ```

### 2. Jalankan GUI (Antarmuka Grafis)

```bash
python gui.py
```

### 3. Jalankan Demo CLI (Terminal)

```bash
python main.py
```

Contoh output:

```
=== Daftar Transaksi ===
[1] 01-11-2026 | Pemasukan | Gaji | Rp5,000,000
[2] 02-11-2026 | Pengeluaran | Makan | Rp35,000
[3] 03-11-2026 | Pengeluaran | Transport | Rp20,000

=== Saldo ===
Saldo: Rp4.945.000 (3 transaksi)

=== Laporan Bulanan ===
Laporan 11/2026 | Pemasukan: Rp5.000.000 | Pengeluaran: Rp55.000 | Saldo: Rp4.945.000
```

### 4. Jalankan Unit Test

```bash
python -m unittest discover -s tests
```

Ekspektasi output:

```
............
----------------------------------------------------------------------
Ran 12 tests in 0.001s

OK
```

---

## 🏗️ Desain OOP

### Hierarki Class

```
Transaksi (ABC)
├── Pemasukan
└── Pengeluaran

Kategori
KeuanganService
LaporanBulanan
└── BarisRekap
```

### Konsep OOP yang Diterapkan

| Konsep | Implementasi |
|---|---|
| **Abstraksi** | `Transaksi` sebagai abstract base class dengan method `nilai_bersih()` dan `jenis()` |
| **Inheritance** | `Pemasukan` dan `Pengeluaran` mewarisi `Transaksi` |
| **Enkapsulasi** | Property dengan getter/setter dan validasi di `Kategori` dan `Transaksi` |
| **Polimorfisme** | `nilai_bersih()` mengembalikan `+jumlah` untuk pemasukan dan `-jumlah` untuk pengeluaran |
| **Dunder Methods** | `__len__`, `__iter__`, `__str__`, `__repr__`, `__eq__`, `__hash__` |

---

## 🧪 Cakupan Unit Test

File [`tests/test_keuangan_service.py`](tests/test_keuangan_service.py) mencakup 12 test case:

- Saldo awal kosong
- Catat pemasukan dan pengeluaran
- ID transaksi bertambah secara berurutan
- Tanggal default adalah hari ini
- Pengeluaran melebihi saldo → `ValueError`
- Jumlah transaksi tidak valid (nol / negatif) → `ValueError`
- Kategori bukan objek `Kategori` → `TypeError`
- Filter transaksi per jenis
- Laporan bulanan (pemasukan, pengeluaran, rekap per kategori)

---

## 📦 Dependensi

| Package | Versi Minimum | Kegunaan |
|---|---|---|
| `customtkinter` | 5.2 | Komponen UI modern berbasis Tkinter |

Tkinter sudah tersedia bawaan di instalasi Python standar (tidak perlu install terpisah).

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan tugas akademis mata kuliah **Pemrograman Berorientasi Objek**.

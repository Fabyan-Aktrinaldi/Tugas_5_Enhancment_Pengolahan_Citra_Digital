"""
Tugas 5 - Enhancement untuk OCR (filtering, noise reduction, sharpening)

Alur program:
1. Baca citra ijazah, putar 90 derajat searah jarum jam, crop area nomor ijazah
2. Perkecil resolusi, lalu tambah noise salt-and-pepper (6%)
3. Terapkan 4 metode: mean filter, median filter, Gaussian filter, sharpening
4. Perbesar tiap hasil, jalankan OCR (Tesseract), ambil angkanya saja
5. Hitung akurasi terhadap ground truth, tampilkan tabel, simpan hasil ke folder output

Syarat: Tesseract sudah terpasang dan bisa dipanggil dari terminal (tesseract --version).
"""

import difflib
import os

import cv2
import numpy as np
import pytesseract

# ---------- Lokasi folder (dihitung dari lokasi file ini) ----------
FOLDER_INI = os.path.dirname(os.path.abspath(__file__))
FOLDER_INPUT = os.path.join(FOLDER_INI, "input")
FOLDER_OUTPUT = os.path.join(FOLDER_INI, "output")

# ---------- Pengaturan ----------
NAMA_CITRA = "01_HighQuality_Enhanced.jpg"   # citra yang diproses (ada di folder input)
GROUND_TRUTH = "571012022000056"             # nomor ijazah yang benar

# Area crop (setelah citra diputar): citra[atas:bawah, kiri:kanan]
CROP_ATAS, CROP_BAWAH = 2180, 2430
CROP_KIRI, CROP_KANAN = 100, 1500

UKURAN_KECIL = (350, 62)    # (lebar, tinggi) untuk mensimulasikan kualitas rendah
KEPADATAN_NOISE = 0.06      # 6% piksel kena noise
SEED = 42                   # supaya noise sama persis setiap kali dijalankan
FAKTOR_PERBESAR = 6         # hasil diperbesar 6x sebelum dibaca OCR

# Isi kalau Tesseract belum masuk PATH, contoh:
# TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_CMD = None
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def baca_dan_crop(nama_file):
    """Baca citra, putar 90 derajat searah jarum jam, lalu crop area nomor ijazah.
    nama_file: nama file citra di folder input."""
    lokasi = os.path.join(FOLDER_INPUT, nama_file)
    citra = cv2.imread(lokasi)
    if citra is None:
        raise FileNotFoundError("Citra tidak ditemukan: " + lokasi)

    citra = cv2.rotate(citra, cv2.ROTATE_90_CLOCKWISE)
    crop = citra[CROP_ATAS:CROP_BAWAH, CROP_KIRI:CROP_KANAN]
    if crop.size == 0:
        raise ValueError("Ukuran citra tidak cocok dengan koordinat crop. "
                         "Koordinat ini dibuat untuk citra 2481 x 3506 piksel (lebar x tinggi, sebelum diputar).")
    return crop


def perkecil(citra):
    """Perkecil citra untuk mensimulasikan hasil scan/foto kualitas rendah.
    cv2.resize(sumber, ukuran_baru, interpolation=...):
    - ukuran_baru   : (lebar, tinggi)
    - INTER_AREA    : metode interpolasi yang bagus untuk memperkecil."""
    return cv2.resize(citra, UKURAN_KECIL, interpolation=cv2.INTER_AREA)


def tambah_noise(citra, kepadatan):
    """Tambah noise salt-and-pepper: sebagian piksel jadi putih (salt),
    sebagian lagi jadi hitam (pepper).
    kepadatan: persen piksel yang kena noise (0.06 = 6%)."""
    hasil = citra.copy()
    tinggi, lebar = hasil.shape[:2]
    jumlah = int(kepadatan * tinggi * lebar)

    # setengah jumlahnya jadi putih (255), pada posisi acak
    baris = np.random.randint(0, tinggi, jumlah // 2)
    kolom = np.random.randint(0, lebar, jumlah // 2)
    hasil[baris, kolom] = 255

    # setengah lagi jadi hitam (0), pada posisi acak
    baris = np.random.randint(0, tinggi, jumlah // 2)
    kolom = np.random.randint(0, lebar, jumlah // 2)
    hasil[baris, kolom] = 0
    return hasil


def filter_mean(citra):
    """Mean filter: tiap piksel diganti rata-rata piksel di sekitarnya.
    cv2.blur(sumber, (lebar_kernel, tinggi_kernel))."""
    return cv2.blur(citra, (3, 3))


def filter_median(citra):
    """Median filter: tiap piksel diganti nilai tengah piksel di sekitarnya.
    cv2.medianBlur(sumber, ukuran_kernel): ukuran kernel harus ganjil.
    Piksel noise yang ekstrem (0 atau 255) hampir tidak pernah jadi nilai tengah,
    jadi noise terbuang tanpa mengaburkan tepi huruf."""
    return cv2.medianBlur(citra, 3)


def filter_gaussian(citra):
    """Gaussian filter: seperti mean filter, tapi piksel yang lebih dekat
    diberi bobot lebih besar.
    cv2.GaussianBlur(sumber, (lebar_kernel, tinggi_kernel), sigmaX):
    sigmaX=0 artinya sigma dihitung otomatis dari ukuran kernel."""
    return cv2.GaussianBlur(citra, (3, 3), 0)


def sharpening(citra):
    """Sharpening dengan unsharp masking: hasil = 1.5 * asli - 0.5 * blur.
    - GaussianBlur((0, 0), sigmaX=3): kernel (0, 0) artinya ukuran kernel
      dihitung otomatis dari sigma
    - addWeighted(citra1, bobot1, citra2, bobot2, tambahan): bobot1*citra1 + bobot2*citra2 + tambahan
    Selisih (asli - blur) adalah detail tepi, lalu ditambahkan lagi ke citra asli."""
    blur = cv2.GaussianBlur(citra, (0, 0), 3)
    return cv2.addWeighted(citra, 1.5, blur, -0.5, 0)


def baca_angka_ocr(citra):
    """Perbesar citra, jalankan OCR, lalu ambil angkanya saja.
    config="--psm 7": Tesseract menganggap gambar berisi satu baris teks.
    INTER_CUBIC: metode interpolasi yang bagus untuk memperbesar."""
    besar = cv2.resize(citra, None, fx=FAKTOR_PERBESAR, fy=FAKTOR_PERBESAR,
                       interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(besar, cv2.COLOR_BGR2GRAY)
    teks = pytesseract.image_to_string(gray, config="--psm 7")
    return "".join(huruf for huruf in teks if huruf.isdigit())


def hitung_akurasi(hasil_ocr, benar):
    """Hitung jumlah karakter benar dan akurasinya (persen).
    SequenceMatcher menyejajarkan dua teks (character alignment), jadi kalau OCR
    melewatkan satu karakter, karakter berikutnya tidak otomatis dianggap salah.
    get_matching_blocks(): potongan teks yang sama pada kedua teks."""
    pencocok = difflib.SequenceMatcher(None, hasil_ocr, benar)
    jumlah_benar = sum(blok.size for blok in pencocok.get_matching_blocks())
    akurasi = round(jumlah_benar / len(benar) * 100, 2)
    return jumlah_benar, akurasi


def main():
    np.random.seed(SEED)
    os.makedirs(FOLDER_OUTPUT, exist_ok=True)

    # 1-2. Crop, perkecil, tambah noise
    crop = baca_dan_crop(NAMA_CITRA)
    noisy = tambah_noise(perkecil(crop), KEPADATAN_NOISE)

    # 3. Empat metode (sharpening diterapkan di atas hasil median filter)
    hasil_median = filter_median(noisy)
    daftar_hasil = {
        "Original (noisy)": noisy,
        "Mean Filter": filter_mean(noisy),
        "Median Filter": hasil_median,
        "Gaussian Filter": filter_gaussian(noisy),
        "Sharpening (median + sharpen)": sharpening(hasil_median),
    }

    # Simpan citra hasil tiap metode
    nama_file = ["00_original_noisy.jpg", "01_mean_filter.jpg", "02_median_filter.jpg",
                 "03_gaussian_filter.jpg", "04_sharpen.jpg"]
    for nama, citra in zip(nama_file, daftar_hasil.values()):
        cv2.imwrite(os.path.join(FOLDER_OUTPUT, nama), citra)

    # 4-5. OCR dan akurasi, lalu tabel
    baris = ["%-30s %-20s %-16s %s" % ("Metode", "Hasil OCR", "Karakter Benar", "Akurasi"),
             "-" * 80]
    for metode, citra in daftar_hasil.items():
        angka = baca_angka_ocr(citra)
        jumlah_benar, akurasi = hitung_akurasi(angka, GROUND_TRUTH)
        baris.append("%-30s %-20s %-16s %s%%" % (
            metode, angka if angka else "(gagal terbaca)",
            "%d / %d" % (jumlah_benar, len(GROUND_TRUTH)), akurasi))

    tabel = "\n".join(baris)
    print(tabel)
    print("Ground truth:", GROUND_TRUTH)
    with open(os.path.join(FOLDER_OUTPUT, "hasil_ocr.txt"), "w", encoding="utf-8") as f:
        f.write(tabel + "\n")
    print("Selesai. Hasil tersimpan di folder:", FOLDER_OUTPUT)


if __name__ == "__main__":
    main()
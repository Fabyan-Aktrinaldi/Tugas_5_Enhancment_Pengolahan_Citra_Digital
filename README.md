# Tugas 5: Enhancement untuk OCR (Filtering, Noise Reduction, dan Sharpening)

Mata kuliah Pengolahan Citra Digital
- Nama : Fabyan Aktrinaldi 
- NIM  : F1G124029 
- Kelas: A

## Catatan penting

Kode di repo ini adalah kode asli yang dibuat saat Tugas 5 dikerjakan. Setelah dosen meminta semua tugas disertai kode dan repo GitHub, kode **disederhanakan** (nama fungsi dan komentar dalam bahasa Indonesia, parameter dijelaskan). Logika pemrosesan citra tidak diubah: gambar hasil dari kode asli dan kode sederhana sudah dibandingkan dan identik. Versi asli ada di commit pertama repo ini.

## Soal

Dari citra nomor ijazah yang berkualitas rendah atau ber-noise, terapkan mean filter, median filter, Gaussian filter, dan sharpening. Bandingkan hasilnya, gunakan hasilnya sebagai input OCR, lalu bandingkan hasil OCR tiap metode dalam tabel (Metode, Hasil OCR, Karakter Benar, Akurasi). Jawab juga dua pertanyaan analisis di bawah.

## Isi repo

- `enhancement_ocr.py`: program utama
- `requirements.txt`: daftar library
- `input/`: tempat citra ijazah (citra tidak ikut di-push)
- `output/`: hasil program (tidak ikut di-push)

## Cara menjalankan

1. Install library: `pip install -r requirements.txt`
2. Pasang Tesseract OCR dan pastikan `tesseract --version` bisa dijalankan di terminal. Kalau belum masuk PATH, isi `TESSERACT_CMD` di bagian atas `enhancement_ocr.py`.
3. Taruh citra dari folder "Praktikum citra" milik dosen di folder `input/` dengan nama aslinya. Koordinat crop dibuat untuk citra berukuran 2481 x 3506 piksel (lebar x tinggi, sebelum diputar). Citra dengan ukuran lain akan menghasilkan pesan error.
4. Jalankan: `python enhancement_ocr.py`. Citra yang diproses diatur lewat `NAMA_CITRA` di bagian atas file (bawaan: `01_HighQuality_Enhanced.jpg`).
5. Hasil: tabel tercetak di terminal. Di `output/` tersimpan citra hasil tiap metode (`00_original_noisy.jpg` sampai `04_sharpen.jpg`) dan `hasil_ocr.txt`.

## Alur kode

1. `baca_dan_crop`: membaca citra, memutar 90 derajat searah jarum jam, lalu crop area nomor ijazah
2. `perkecil` dan `tambah_noise`: memperkecil resolusi (350 x 62) lalu menambah noise salt-and-pepper 6% (seed 42, supaya hasilnya sama setiap kali dijalankan)
3. `filter_mean`, `filter_median`, `filter_gaussian` (kernel 3x3), dan `sharpening` (unsharp masking di atas hasil median filter)
4. `baca_angka_ocr`: memperbesar 6x lalu OCR dengan Tesseract (`--psm 7`), diambil angkanya saja
5. `hitung_akurasi`: akurasi dengan character alignment (`SequenceMatcher`) terhadap ground truth `571012022000056`

## Hasil (sesuai laporan)

Ground truth: 571012022000056

| Metode | Hasil OCR | Karakter Benar | Akurasi |
|---|---|---|---|
| Original (noisy) | (gagal terbaca) | 0 / 15 | 0% |
| Mean Filter | (gagal terbaca) | 0 / 15 | 0% |
| Median Filter | 7102022700005 | 12 / 15 | 80% |
| Gaussian Filter | (gagal terbaca) | 0 / 15 | 0% |
| Sharpening (median + sharpen) | 7105202200005 | 12 / 15 | 80% |

## Perbandingan dengan laporan

[ISI: tempel tabel hasil menjalankan kode ini, lalu tulis apakah sama dengan tabel laporan di atas. Kalau ada perbedaan, tulis metode yang berbeda, angka di laporan, angka dari kode ini, dan dugaan penyebabnya (misalnya versi Tesseract).]

## Mengapa median filter memberi hasil OCR lebih baik pada salt-and-pepper noise?

Salt-and-pepper noise berupa piksel acak yang nilainya melompat ekstrem ke putih (salt) atau hitam (pepper), terpisah dari piksel tetangganya. Mean dan Gaussian filter merata-ratakan nilai piksel di sekitarnya, sehingga piksel noise yang ekstrem ikut dirata-ratakan dan piksel tetangga yang bersih justru ikut berubah, membuat area di sekitar noise menjadi kabur. Median filter mengambil nilai tengah dari piksel di jendela filter. Karena piksel salt-and-pepper adalah outlier ekstrem, ia hampir tidak pernah menjadi nilai tengah sehingga terbuang tanpa memengaruhi piksel bersih di sekitarnya. Akibatnya tepi huruf tetap tajam dan tidak ikut kabur, yang menguntungkan OCR karena OCR sangat bergantung pada kejelasan tepi karakter.

## Apakah citra yang paling bagus secara visual selalu menghasilkan OCR dengan akurasi tertinggi?

Tidak selalu. Pada eksperimen ini hasil sharpening di atas median filter terlihat sedikit lebih tajam secara visual dibanding median filter saja, tetapi akurasi OCR keduanya sama (80%). Sharpening juga menonjolkan tepi noise sisa dan tekstur kertas yang belum sepenuhnya hilang, sehingga bisa menambahkan artefak yang tidak membantu OCR. Persepsi visual manusia menilai ketajaman, kontras, dan estetika, sedangkan OCR sensitif terhadap bentuk geometris tepi karakter secara presisi piksel. Karena itu kualitas enhancement untuk OCR sebaiknya diukur langsung dari akurasi OCR, bukan hanya dari penilaian visual.
# CCTV Monitor V2

Aplikasi pemantauan CCTV ringan dan paralel menggunakan Python. Mengecek 100+ IP secara bersamaan, sumber data diambil otomatis (Publish to Web) dari Google Sheets, mendukung retry pintar, serta kompatibel dengan Windows, Linux, dan Android (Termux).

## Fitur Unggulan
- **Single Source of Truth**: Mengambil URL CSV Google Sheet. Tidak butuh file `.xlsx` lokal.
- **Multithreading Cepat**: Mengecek 105+ IP secara serentak, bukan satu-per-satu.
- **Auto Retry**: Mencoba 5x dengan delay 0.3s jika CCTV mengalami Timeout.
- **Modular & Clean Code**: Mudah dirawat dan dikembangkan.
- **Cross-Platform**: Berjalan mulus di Windows, distro Linux, dan Termux Android.

---

## Prasyarat
- Python 3.8 ke atas.
- Koneksi Internet.
- Command ping bawaan OS (`iputils` untuk Termux).

---

## Instalasi di Laptop (Windows / Linux)

1. Buka Terminal / Command Prompt (CMD).
2. Clone atau download repository ini, lalu masuk ke foldernya:
   ```bash
   cd CCTV-Monitor-V

1. Install dependencies menggunakan pip:

Bash
pip install -r requirements.txt

2. Jalankan program utama:

Bash
python cek_cctv.py


## Instalasi di Android (Termux)
Termux membutuhkan beberapa package dasar agar Python dan perintah system ping bisa bekerja secara efisien.

1. Buka aplikasi Termux.

2. Update repo dan upgrade package Termux:

Bash
pkg update && pkg upgrade -y
Install Python, Git, dan iputils (menyediakan command ping standar Linux):

Bash
pkg install python git iputils -y

3. Clone / download project ini dan masuk ke foldernya:

Bash
git clone <URL_REPO>
cd CCTV-Monitor

4. Install Python dependencies:

Bash
pip install -r requirements.txt

5. Jalankan script:

Bash
python cek_cctv.py
# ==============================================================
# analisis_foto.py
# Tujuan : Membuktikan bahwa sebuah foto sebenarnya adalah angka.
# Cara   : python analisis_foto.py
# ==============================================================

import os                              # untuk mengambil nama file dari path
from PIL import Image, ExifTags        # Pillow: membaca gambar + metadata EXIF
import numpy as np                     # NumPy: mengubah gambar menjadi array angka
import matplotlib.pyplot as plt        # Matplotlib: menampilkan visualisasi

# --------------------------------------------------------------
# INPUT: ganti "foto.jpg" sesuai nama file foto Anda.
# Taruh foto di folder yang sama dengan file .py ini.
# --------------------------------------------------------------
image_path = "assets/foto.jpg"


# ==============================================================
# BAGIAN 1 - MEMBUKA FOTO & INFORMASI DASAR
# ==============================================================
image = Image.open(image_path)         # membuka file foto (belum jadi angka)

width, height = image.size             # PIL menyimpan ukuran sebagai (lebar, tinggi)
jumlah_channel = len(image.getbands()) # getbands() -> ('R','G','B') => 3 channel

print("=== INFORMASI GAMBAR ===")
print("Nama file       :", os.path.basename(image_path))
print("Format          :", image.format)    # JPEG / PNG / dll (cara file disimpan)
print("Resolusi        :", width, "x", height)
print("Width (lebar)   :", width, "pixel")  # jumlah kolom pixel
print("Height (tinggi) :", height, "pixel") # jumlah baris pixel
print("Mode            :", image.mode)      # RGB = Red, Green, Blue
print("Jumlah channel  :", jumlah_channel)  # banyaknya angka per pixel
print("Total pixel     :", width * height)
print()


# ==============================================================
# BAGIAN 2 - METADATA (EXIF)
# Metadata = DATA TENTANG foto (kapan, pakai kamera apa).
# Metadata BUKAN pixel. Pixel adalah isi gambarnya.
# ==============================================================
print("=== METADATA EXIF ===")

exif = image.getexif()                 # bisa kosong jika foto tidak punya EXIF

# Sebagian metadata kamera (ISO, aperture, dll) ada di "sub-bagian" EXIF.
# 0x8769 = kode untuk bagian Exif, 0x8825 = kode untuk bagian GPS.
exif_detail = exif.get_ifd(0x8769)
gps_info = exif.get_ifd(0x8825)

# Gabungkan semua metadata ke satu dictionary: {nama_tag: nilai}
metadata = {}
for tag_id, nilai in exif.items():
    nama_tag = ExifTags.TAGS.get(tag_id, tag_id)   # ubah kode angka jadi nama
    metadata[nama_tag] = nilai
for tag_id, nilai in exif_detail.items():
    nama_tag = ExifTags.TAGS.get(tag_id, tag_id)
    metadata[nama_tag] = nilai

if len(metadata) == 0:
    print("Metadata EXIF tidak tersedia.")
else:
    # Daftar metadata yang ingin ditampilkan: (nama di EXIF, label tampilan)
    daftar_metadata = [
        ("DateTimeOriginal", "Tanggal pengambilan"),
        ("Make",             "Merek kamera"),
        ("Model",            "Model kamera"),
        ("Software",         "Software"),
        ("Orientation",      "Orientasi"),
        ("FocalLength",      "Focal length"),
        ("ISOSpeedRatings",  "ISO"),
        ("ExposureTime",     "Exposure time"),
        ("FNumber",          "Aperture (F)"),
    ]
    for nama_exif, label in daftar_metadata:
        if nama_exif in metadata:       # tampilkan HANYA jika memang ada
            print(f"{label:<20}: {metadata[nama_exif]}")

        # Tag GPS: 1 = LatitudeRef (N/S), 2 = Latitude, 3 = LongitudeRef (E/W), 4 = Longitude
    lat_ref = gps_info.get(1, "")
    lon_ref = gps_info.get(3, "")

    if lat_ref in ("N", "S") and lon_ref in ("E", "W"):
        lat = gps_info.get(2)    # (derajat, menit, detik)
        lon = gps_info.get(4)

        # Ubah derajat-menit-detik menjadi desimal
        lat_desimal = float(lat[0]) + float(lat[1]) / 60 + float(lat[2]) / 3600
        lon_desimal = float(lon[0]) + float(lon[1]) / 60 + float(lon[2]) / 3600

        # Selatan dan Barat bernilai negatif
        if lat_ref == "S":
            lat_desimal = -lat_desimal
        if lon_ref == "W":
            lon_desimal = -lon_desimal

        print("GPS Latitude        :", lat_ref, lat, "->", round(lat_desimal, 6))
        print("GPS Longitude       :", lon_ref, lon, "->", round(lon_desimal, 6))
        
         # Format siap copy-paste ke kolom pencarian Google Maps
        print("Koordinat (Maps)    :", f"{lat_desimal:.6f}, {lon_desimal:.6f}")
        print("Link Google Maps    :", f"https://www.google.com/maps?q={lat_desimal:.6f},{lon_desimal:.6f}")
    else:
        print("GPS                 : tidak tersedia (lokasi tidak direkam saat foto diambil)")
print()


# ==============================================================
# BAGIAN 3 - MENGUBAH FOTO MENJADI ANGKA (BAGIAN TERPENTING)
# ==============================================================
# Pastikan gambar berformat RGB (3 channel). Ini penting karena PNG
# bisa berformat RGBA (4 channel) atau grayscale (1 channel).
image_rgb = image.convert("RGB")

# INILAH MOMEN FOTO MENJADI ANGKA:
image_array = np.array(image_rgb)

print("=== REPRESENTASI ANGKA ===")
print("Shape array :", image_array.shape)   # (height, width, channel)
print("Data type   :", image_array.dtype)   # uint8 = bilangan bulat 0-255
print()
print("Arti shape (height, width, channel):")
print("  height  =", image_array.shape[0], "-> jumlah BARIS pixel")
print("  width   =", image_array.shape[1], "-> jumlah KOLOM pixel")
print("  channel =", image_array.shape[2], "-> jumlah angka warna tiap pixel [R, G, B]")
print()
print("Contoh arti warna (rentang 0 - 255):")
print("  [255,   0,   0] = merah")
print("  [  0, 255,   0] = hijau")
print("  [  0,   0, 255] = biru")
print("  [  0,   0,   0] = hitam")
print("  [255, 255, 255] = putih")
print()


# ==============================================================
# BAGIAN 4 - CONTOH NILAI PIXEL
# Koordinat ditulis (y, x) = (baris, kolom), karena array NumPy
# diakses dengan array[baris, kolom]. Baris (y) dulu, baru kolom (x).
# ==============================================================
print("=== CONTOH NILAI PIXEL ===")

koordinat_contoh = [
    (0, 0), (0, 1), (1, 0),
    (100, 100), (200, 200), (300, 300),
    (height // 2, width // 2),          # pixel di tengah gambar
    (height - 1, width - 1),            # pixel paling pojok kanan bawah
]

for y, x in koordinat_contoh:
    if y < height and x < width:        # lewati jika gambar terlalu kecil
        pixel = image_array[y, x]       # hasilnya [R G B]
        print(f"Pixel ({y}, {x})".ljust(22), ":", pixel,
              f"-> R={pixel[0]}, G={pixel[1]}, B={pixel[2]}")
print()


# ==============================================================
# BAGIAN 5 - POTONGAN MATRIX
# Hanya 5 baris x 5 kolom pertama (bukan seluruh gambar!).
# ==============================================================
print("=== POTONGAN MATRIX PIXEL (5 baris x 5 kolom pertama) ===")
potongan = image_array[:5, :5]
print(potongan)
print()
print("Shape potongan:", potongan.shape, "-> 5 baris, 5 kolom, 3 angka (RGB)")
print("Setiap [R G B] di atas adalah SATU pixel.")
print()


# ==============================================================
# BAGIAN 6 - STATISTIK PIXEL
# Bisa dihitung karena gambar sudah menjadi angka.
# ==============================================================
print("=== STATISTIK PIXEL (semua channel) ===")
print("Nilai minimum   :", image_array.min())
print("Nilai maksimum  :", image_array.max())
print("Nilai rata-rata :", round(image_array.mean(), 2))
print()

# Pisahkan per channel: [:, :, 0] artinya semua baris, semua kolom, channel ke-0
red_channel = image_array[:, :, 0]
green_channel = image_array[:, :, 1]
blue_channel = image_array[:, :, 2]

print("=== STATISTIK PER CHANNEL ===")
print(f"Red   -> min {red_channel.min()}, max {red_channel.max()}, rata-rata {red_channel.mean():.2f}")
print(f"Green -> min {green_channel.min()}, max {green_channel.max()}, rata-rata {green_channel.mean():.2f}")
print(f"Blue  -> min {blue_channel.min()}, max {blue_channel.max()}, rata-rata {blue_channel.mean():.2f}")
print()


# ==============================================================
# BAGIAN 7 - VISUALISASI
# Foto -> array -> channel -> angka -> gambar kembali
# ==============================================================
# Ambil area kecil 8x8 pixel dari tengah gambar untuk diperlihatkan angkanya
ukuran_zoom = min(8, height, width)
y_awal = height // 2
x_awal = width // 2
if y_awal + ukuran_zoom > height:
    y_awal = height - ukuran_zoom
if x_awal + ukuran_zoom > width:
    x_awal = width - ukuran_zoom
area_zoom = red_channel[y_awal:y_awal + ukuran_zoom, x_awal:x_awal + ukuran_zoom]

plt.figure(figsize=(15, 5))

# Panel 1: foto asli (dibuat dari array angka)
plt.subplot(1, 3, 1)
plt.imshow(image_array)
plt.title("1. Foto asli (dari array)")
plt.axis("off")
# Kotak merah menandai area yang diperbesar di panel 3
kotak = plt.Rectangle((x_awal, y_awal), ukuran_zoom, ukuran_zoom,
                      edgecolor="red", facecolor="none", linewidth=2)
plt.gca().add_patch(kotak)

# Panel 2: channel merah saja (grayscale: gelap = angka kecil, terang = angka besar)
plt.subplot(1, 3, 2)
plt.imshow(red_channel, cmap="gray", vmin=0, vmax=255)
plt.title("2. Channel Red (0 = hitam, 255 = putih)")
plt.axis("off")

# Panel 3: zoom 8x8 pixel channel merah + angkanya ditulis langsung
plt.subplot(1, 3, 3)
plt.imshow(area_zoom, cmap="gray", vmin=0, vmax=255)
plt.title(f"3. Zoom {ukuran_zoom}x{ukuran_zoom} pixel (kotak merah)")
for baris in range(ukuran_zoom):
    for kolom in range(ukuran_zoom):
        nilai = area_zoom[baris, kolom]
        warna_teks = "black" if nilai > 128 else "white"   # agar angka terbaca
        plt.text(kolom, baris, str(nilai), ha="center", va="center",
                 color=warna_teks, fontsize=8)
plt.axis("off")

plt.tight_layout()
plt.show()


# ==============================================================
# BAGIAN 8 - KESIMPULAN
# ==============================================================
print("=== KESIMPULAN ===")
print("Foto yang kita lihat sebenarnya tersusun dari pixel.")
print("Setiap pixel direpresentasikan oleh angka.")
print("Pada gambar RGB, setiap pixel memiliki 3 nilai:")
print("R (Red), G (Green), dan B (Blue).")
print()
print("Jadi secara sederhana:")
print("Foto -> Pixel -> RGB -> Angka (0-255) -> Array NumPy")

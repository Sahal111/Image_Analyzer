# ==============================================================
# Judul : Image Analyzer (Python)
# TUJUAN : Membuktikan bahwa foto (citra digital) adalah susunan angka.
# ==============================================================

import os
import numpy as np  
import matplotlib.pyplot as plt  
from PIL import Image, ImageOps, ExifTags  

folder_script = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(folder_script, "assets", "IMG_20261008_142514_031.jpg")
folder_hasil = os.path.join(folder_script, "hasil")
os.makedirs(folder_hasil, exist_ok=True)

# ==============================================================
# BAGIAN 1 - BUKA FOTO & INFORMASI DASAR
# ==============================================================
print("=== 1. INFORMASI DASAR ===")

image = Image.open(image_path)  
format_asli = image.format  
exif = image.getexif()
image = ImageOps.exif_transpose(image)
width, height = image.size  

print("Nama file      :", os.path.basename(image_path))
print("Format         :", format_asli)
print("Resolusi       :", width, "x", height)
print("Mode warna     :", image.mode) 
print("Total pixel    :", width * height)
print()

# ==============================================================
# BAGIAN 2 - METADATA (EXIF)
# ==============================================================
print("=== 2. METADATA EXIF ===")

metadata = {}
for kode, nilai in exif.items():
    metadata[ExifTags.TAGS.get(kode, kode)] = nilai
for kode, nilai in exif.get_ifd(0x8769).items():  # 0x8769 = bagian detail kamera
    metadata[ExifTags.TAGS.get(kode, kode)] = nilai
    
yang_ditampilkan = [
    ("DateTimeOriginal", "Tanggal pengambilan"),
    ("Make", "Merek kamera"),
    ("Model", "Model kamera"),
    ("ISOSpeedRatings", "ISO"),
    ("ExposureTime", "Exposure time"),
    ("FNumber", "Aperture (F)"),
    ("FocalLength", "Focal length"),
]
ada_metadata = False
for nama_exif, label in yang_ditampilkan:
    if nama_exif in metadata:
        print(f"{label:<20}: {metadata[nama_exif]}")
        ada_metadata = True
if not ada_metadata:
    print("Metadata kamera tidak tersedia.")

gps = exif.get_ifd(0x8825)  # 0x8825 = bagian GPS
if 2 in gps and 4 in gps:  # 2 = latitude, 4 = longitude
    lat, lon = gps[2], gps[4]  # bentuknya (derajat, menit, detik)

    # derajat-menit-detik -> desimal
    lat_desimal = float(lat[0]) + float(lat[1]) / 60 + float(lat[2]) / 3600
    lon_desimal = float(lon[0]) + float(lon[1]) / 60 + float(lon[2]) / 3600

    # Selatan (S) dan Barat (W) bernilai negatif
    if gps.get(1) == "S":
        lat_desimal = -lat_desimal
    if gps.get(3) == "W":
        lon_desimal = -lon_desimal

    print(f"Koordinat GPS       : {lat_desimal:.6f}, {lon_desimal:.6f}")
    print(
        f"Link Google Maps    : https://www.google.com/maps?q={lat_desimal:.6f},{lon_desimal:.6f}"
    )
    print("(!) Catatan privasi : foto bisa membocorkan lokasi lewat metadata.")
else:
    print("GPS                 : tidak tersedia")
print()

# ==============================================================
# BAGIAN 3 - FOTO MENJADI ANGKA  
# ==============================================================
print("=== 3. FOTO MENJADI ANGKA ===")

image_rgb = image.convert("RGB")  
image_array = np.array(image_rgb)  # <-- DI SINILAH FOTO JADI ANGKA

print("Shape array :", image_array.shape, "-> (tinggi, lebar, channel)")
print("Tipe data   :", image_array.dtype, "-> bilangan bulat 0 sampai 255")
print()
print("Artinya:")
print("  tinggi  =", image_array.shape[0], "-> jumlah BARIS pixel")
print("  lebar   =", image_array.shape[1], "-> jumlah KOLOM pixel")
print("  channel =", image_array.shape[2], "-> angka per pixel [R, G, B]")
print()
print("Contoh arti warna:")
print("  [255,   0,   0] = merah")
print("  [  0, 255,   0] = hijau")
print("  [  0,   0, 255] = biru")
print("  [  0,   0,   0] = hitam")
print("  [255, 255, 255] = putih")
print()

# ==============================================================
# BAGIAN 4 - NILAI SATU PIXEL
# ==============================================================
print("=== 4. NILAI PIXEL ===")

titik_sampel = [
    (0, 0),  # pojok kiri atas
    (height // 2, width // 2),  # tengah gambar
    (height - 1, width - 1),  # pojok kanan bawah
]
for y, x in titik_sampel:
    r, g, b = image_array[y, x]
    print(f"Pixel (baris={y}, kolom={x}) -> R={r}, G={g}, B={b}")
print()

# ==============================================================
# BAGIAN 5 - POTONGAN MATRIX
# ==============================================================
print("=== 5. POTONGAN MATRIX (5x5 pixel pertama) ===")

potongan = image_array[:5, :5]
print(potongan)
print("Shape:", potongan.shape, "-> 5 baris, 5 kolom, 3 angka (RGB)")
print("Setiap [R G B] di atas = SATU pixel.")
print()


# ==============================================================
# BAGIAN 6 - STATISTIK, UKURAN DATA, JUMLAH WARNA
# ==============================================================
print("=== 6. STATISTIK ===")

red = image_array[:, :, 0]
green = image_array[:, :, 1]
blue = image_array[:, :, 2]

print(f"Red   -> min {red.min()}, max {red.max()}, rata-rata {red.mean():.2f}")
print(f"Green -> min {green.min()}, max {green.max()}, rata-rata {green.mean():.2f}")
print(f"Blue  -> min {blue.min()}, max {blue.max()}, rata-rata {blue.mean():.2f}")
print()

ukuran_array = image_array.nbytes  # tinggi x lebar x 3 byte
ukuran_file = os.path.getsize(image_path)
print(f"Ukuran array (mentah)  : {ukuran_array:,} byte")
print(f"Ukuran file di disk    : {ukuran_file:,} byte")
print("File lebih kecil karena JPEG dikompresi; array adalah hasil decode.")
print()

print("Satu channel : 256 kemungkinan (0-255) = 8 bit")
print("Tiga channel : 256 x 256 x 256 =", f"{256 ** 3:,}", "warna (24 bit)")
print()

# ==============================================================
# BAGIAN 7 - GRAYSCALE: 3 ANGKA JADI 1 ANGKA PER PIXEL
# ==============================================================
print("=== 7. GRAYSCALE ===")

gray = 0.299 * red + 0.587 * green + 0.114 * blue  # dihitung untuk SEMUA pixel
gray = gray.astype(np.uint8)  # kembali ke bilangan bulat 0-255

print("Shape gray :", gray.shape, "-> tidak ada dimensi channel lagi")
print(
    "Pixel tengah: RGB =",
    image_array[height // 2, width // 2],
    "-> gray =",
    gray[height // 2, width // 2],
)
print()

# ==============================================================
# BAGIAN 8 - BYTE MENTAH FILE
# ==============================================================
print("=== 8. BYTE MENTAH FILE ===")

with open(image_path, "rb") as f:
    awal_file = f.read(16)  # baca 16 byte pertama

print("16 byte pertama (desimal)    :", list(awal_file))
print("16 byte pertama (heksadesimal):", awal_file.hex(" ").upper())
print("JPEG selalu diawali FF D8 -> itu 'tanda tangan' file JPEG.")
print()

# ==============================================================
# BAGIAN 9 - ANGKA MENJADI FOTO 
# ==============================================================
print("=== 9. ANGKA MENJADI FOTO ===")

# --- 9a. Simpan array jadi foto, baca lagi, bandingkan ---
# PNG bersifat lossless (tidak mengubah angka), jadi hasilnya harus identik.
path_rekonstruksi = os.path.join(folder_hasil, "hasil_rekonstruksi.png")
Image.fromarray(image_array).save(path_rekonstruksi)
baca_ulang = np.array(Image.open(path_rekonstruksi))
print(
    "9a. Array -> PNG -> array identik dengan aslinya?",
    np.array_equal(baca_ulang, image_array),
)

# --- 9b. Ubah angkanya -> gambarnya ikut berubah ---
# Negatif: setiap angka dibalik (0 jadi 255, 255 jadi 0)
negatif = 255 - image_array

# Kotak merah: 100x100 pixel dipaksa bernilai [255, 0, 0]
modifikasi = image_array.copy()  # .copy() agar array asli tidak rusak
modifikasi[50:150, 50:150] = [255, 0, 0]

Image.fromarray(negatif).save(os.path.join(folder_hasil, "hasil_negatif.png"))
Image.fromarray(modifikasi).save(os.path.join(folder_hasil, "hasil_kotak_merah.png"))
print("9b. Angka diubah -> gambar berubah (negatif & kotak merah disimpan).")

# --- 9c. Gambar dari NOL: hanya dari angka yang kita tulis sendiri ---
# Ukuran 2 baris x 3 kolom = 6 pixel. Tanpa kamera sama sekali.
buatan_sendiri = np.array(
    [
        [[255, 0, 0], [0, 255, 0], [0, 0, 255]],  # baris 1: merah, hijau, biru
        [[255, 255, 0], [255, 255, 255], [0, 0, 0]],  # baris 2: kuning, putih, hitam
    ],
    dtype=np.uint8,
)

print("9c. Gambar buatan sendiri, shape:", buatan_sendiri.shape, "= 6 pixel")

# Diperbesar dengan NEAREST agar tiap pixel terlihat jelas sebagai kotak
Image.fromarray(buatan_sendiri).resize((300, 200), Image.NEAREST).save(
    os.path.join(folder_hasil, "hasil_buatan_sendiri.png")
)
print()

# ==============================================================
# BAGIAN 10 - VISUALISASI
# ==============================================================

# ---------- Figure 1: dari foto sampai angka ----------
ukuran_zoom = min(8, height, width)
y0 = min(height // 2, height - ukuran_zoom)
x0 = min(width // 2, width - ukuran_zoom)
area_zoom = red[y0 : y0 + ukuran_zoom, x0 : x0 + ukuran_zoom]

plt.figure(figsize=(15, 5))

# Panel 1: foto asli, kotak merah menandai area yang di-zoom
plt.subplot(1, 3, 1)
plt.imshow(image_array)
plt.title("1. Foto (dari array)")
plt.gca().add_patch(
    plt.Rectangle(
        (x0, y0),
        ukuran_zoom,
        ukuran_zoom,
        edgecolor="red",
        facecolor="none",
        linewidth=2,
    )
)
plt.axis("off")

# Panel 2: channel Red saja (gelap = angka kecil, terang = angka besar)
plt.subplot(1, 3, 2)
plt.imshow(red, cmap="gray", vmin=0, vmax=255)
plt.title("2. Channel Red (0=hitam, 255=putih)")
plt.axis("off")

# Panel 3: zoom 8x8 pixel channel Red, angkanya ditulis langsung
plt.subplot(1, 3, 3)
plt.imshow(area_zoom, cmap="gray", vmin=0, vmax=255)
plt.title(f"3. Angka channel Red, area {ukuran_zoom}x{ukuran_zoom}")
for baris in range(ukuran_zoom):
    for kolom in range(ukuran_zoom):
        nilai = area_zoom[baris, kolom]
        warna_teks = "black" if nilai > 128 else "white"
        plt.text(
            kolom,
            baris,
            str(nilai),
            ha="center",
            va="center",
            color=warna_teks,
            fontsize=8,
        )
plt.axis("off")

plt.tight_layout()
plt.show()

# ---------- Figure 2: channel berwarna + histogram + grayscale ----------
# Channel berwarna: nol-kan dua channel lain, sisakan satu
hanya_red = np.zeros_like(image_array)
hanya_red[:, :, 0] = red
hanya_green = np.zeros_like(image_array)
hanya_green[:, :, 1] = green
hanya_blue = np.zeros_like(image_array)
hanya_blue[:, :, 2] = blue

plt.figure(figsize=(15, 8))

plt.subplot(2, 4, 1)
plt.imshow(hanya_red)
plt.title("Channel R (berwarna)")
plt.axis("off")

plt.subplot(2, 4, 2)
plt.imshow(hanya_green)
plt.title("Channel G (berwarna)")
plt.axis("off")

plt.subplot(2, 4, 3)
plt.imshow(hanya_blue)
plt.title("Channel B (berwarna)")
plt.axis("off")

plt.subplot(2, 4, 4)
plt.imshow(gray, cmap="gray", vmin=0, vmax=255)
plt.title("Grayscale (1 angka/pixel)")
plt.axis("off")

# Histogram: berapa banyak pixel untuk setiap nilai 0-255
plt.subplot(2, 1, 2)
plt.hist(red.ravel(), bins=256, range=(0, 255), color="red", alpha=0.5, label="Red")
plt.hist(
    green.ravel(), bins=256, range=(0, 255), color="green", alpha=0.5, label="Green"
)
plt.hist(blue.ravel(), bins=256, range=(0, 255), color="blue", alpha=0.5, label="Blue")
plt.title("Histogram: sebaran angka tiap channel")
plt.xlabel("Nilai pixel (0-255)")
plt.ylabel("Jumlah pixel")
plt.legend()

plt.tight_layout()
plt.show()

# ---------- Figure 3: bukti angka -> foto ----------
plt.figure(figsize=(15, 4))

plt.subplot(1, 4, 1)
plt.imshow(image_array)
plt.title("Asli")
plt.axis("off")

plt.subplot(1, 4, 2)
plt.imshow(negatif)
plt.title("Angka dibalik (255 - angka)")
plt.axis("off")

plt.subplot(1, 4, 3)
plt.imshow(modifikasi)
plt.title("Angka diubah: kotak merah")
plt.axis("off")

plt.subplot(1, 4, 4)
plt.imshow(buatan_sendiri, interpolation="nearest")
plt.title("6 pixel buatan sendiri")
plt.axis("off")

plt.tight_layout()
plt.show()

# ==============================================================
# BAGIAN 11 - KESIMPULAN
# ==============================================================
print("=== KESIMPULAN ===")
print("1. Foto -> angka : np.array(foto) menghasilkan matrix angka 0-255.")
print("2. Angka -> foto : Image.fromarray(array) mengembalikan foto dari angka.")
print("3. Ubah angka    : gambar ikut berubah (negatif, kotak merah).")
print("4. Dari nol      : 6 angka tulisan tangan menjadi gambar tanpa kamera.")
print()
print("Jadi: Foto = Pixel = Angka RGB (0-255) = Array NumPy")

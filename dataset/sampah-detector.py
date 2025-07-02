# Import library yang diperlukan
import serial  # Untuk komunikasi dengan Arduino via serial
import time    # Untuk mengatur timing dan delay
from ultralytics import YOLO  # Library YOLO untuk object detection
import cv2     # OpenCV untuk pemrosesan gambar dan video

# ========== INISIALISASI MODEL DAN HARDWARE ==========

# Load model YOLO yang sudah di-training
yolo_model = YOLO('D:/Python/uas-pcd/dataset/best.pt') # Ganti dengan path model YOLO hasil training Anda
class_names = yolo_model.model.names  # Ambil nama-nama kelas yang bisa dideteksi model

# Setup komunikasi serial dengan Arduino
ser = serial.Serial('COM9', 9600, timeout=1)  # Port COM9, baud rate 9600, timeout 1 detik

# Setup kamera
cap = cv2.VideoCapture(0)  # Gunakan kamera default (index 0)

# Variabel untuk mengatur cooldown (jeda waktu)
last_sent_time = 0  # Menyimpan waktu terakhir sinyal dikirim ke Arduino
cooldown = 3        # Jeda 3 detik sebelum bisa kirim sinyal lagi (mencegah spam)

# ========== LOOP UTAMA PROGRAM ==========
while True:
    # Baca frame dari kamera
    ret, frame = cap.read()
    if not ret:
        print("Gagal membaca frame dari kamera.")
        break  # Keluar dari loop jika gagal baca kamera
    # Jalankan deteksi objek menggunakan YOLO
    results = yolo_model(frame)  # Deteksi objek pada frame saat ini
    detected = False             # Flag untuk menandai apakah ada objek terdeteksi

    # ========== PEMROSESAN HASIL DETEKSI ==========
    for result in results:
        # Ekstrak data dari hasil deteksiq
        boxes = result.boxes.xyxy.cpu().numpy().astype(int)      # Koordinat bounding box (x1,y1,x2,y2)
        class_ids = result.boxes.cls.cpu().numpy().astype(int)   # ID kelas objek yang terdeteksi
        
        # Loop untuk setiap objek yang terdeteksi
        for box, class_id in zip(boxes, class_ids):
            # Ambil koordinat bounding box
            x1, y1, x2, y2 = box
            # Ambil nama kelas berdasarkan ID
            class_name = class_names[class_id]
            
            # ========== VISUALISASI DETEKSI ==========
            # Gambar kotak hijau di sekitar objek yang terdeteksi
            cv2.rectangle(frame, (x1, y1), (x2, y2), (50,255,50), 1)
            # Tampilkan nama kelas di atas kotak (warna hijau, font Hershey Simplex)
            cv2.putText(frame, class_name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

            # ========== KOMUNIKASI DENGAN ARDUINO ==========
            # Kirim sinyal ke Arduino hanya jika cooldown sudah berlalu
            current_time = time.time()  # Ambil waktu saat ini
            
            # Cek apakah sudah lewat dari waktu cooldown
            if current_time - last_sent_time > cooldown:
                # Kirim sinyal '1' ke Arduino untuk mengaktifkan servo (buka tutup sampah)
                ser.write(b'1')  
                print(f"Deteksi: {class_name} | Servo aktif.")
                last_sent_time = current_time  # Update waktu terakhir pengiriman

                # ========== MENUNGGU KONFIRMASI DARI ARDUINO ==========
                # Tunggu balasan dari Arduino sebelum lanjut deteksi lagi
                print("Menunggu konfirmasi dari Arduino...")
                while True:
                    # Cek apakah ada data masuk dari Arduino
                    if ser.in_waiting:
                        # Baca data dari Arduino dan decode menjadi string
                        data = ser.readline().decode().strip()
                        # Jika Arduino mengirim "DONE", berarti servo sudah selesai bergerak
                        if data == "DONE":
                            print("Tutup sampah sudah menutup, lanjut deteksi.")
                            break  # Keluar dari loop tunggu konfirmasi

            detected = True  # Tandai bahwa ada objek terdeteksi
            break  # Hanya ambil 1 objek saja untuk setiap frame (break dari loop objek)

    # ========== TAMPILKAN HASIL DAN CEK EXIT CONDITION ==========
    # Tampilkan frame dengan hasil deteksi di window
    cv2.imshow('frame', frame)
    
    # Keluar dari program jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ========== CLEANUP / PEMBERSIHAN RESOURCE ==========
# Tutup koneksi serial dengan Arduino
ser.close()
# Lepas resource kamera
cap.release()
# Tutup semua window OpenCV
cv2.destroyAllWindows()
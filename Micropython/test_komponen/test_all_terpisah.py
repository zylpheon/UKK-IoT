from machine import Pin, time_pulse_us
import dht
import time

# ==========================================
# KONFIGURASI PIN SESUAI TABEL
# ==========================================
PIN_DHT   = 4
PIN_TRIG  = 5
PIN_ECHO  = 18
PIN_RELAY = 19
PIN_LED_R = 21  # Merah
PIN_LED_Y = 22  # Kuning
PIN_LED_G = 23  # Hijau

# ==========================================
# INISIALISASI KOMPONEN
# ==========================================
# Sensor
sensor_dht = dht.DHT11(Pin(PIN_DHT))
trig = Pin(PIN_TRIG, Pin.OUT)
echo = Pin(PIN_ECHO, Pin.IN)

# Aktuator (Set semua ke OFF/0 saat awal)
relay      = Pin(PIN_RELAY, Pin.OUT, value=0)
led_merah  = Pin(PIN_LED_R, Pin.OUT, value=0)
led_kuning = Pin(PIN_LED_Y, Pin.OUT, value=0)
led_hijau  = Pin(PIN_LED_G, Pin.OUT, value=0)

# ==========================================
# FUNGSI PENGUJIAN TERPISAH
# ==========================================
def test_dht():
    print("\n[+] Menguji Sensor DHT11 (5x pembacaan)...")
    for i in range(5):
        try:
            sensor_dht.measure()
            suhu = sensor_dht.temperature()
            hum = sensor_dht.humidity()
            print(f"    [{i+1}/5] Suhu: {suhu}°C | Kelembaban: {hum}%")
        except OSError:
            print(f"    [{i+1}/5] ⚠️ Gagal membaca DHT11. Cek kabel SDA di D4!")
        time.sleep(2)  # DHT11 butuh jeda 2 detik antar pembacaan

def test_hcsr04():
    print("\n[+] Menguji Sensor Ultrasonik HC-SR04 (5x pembacaan)...")
    for i in range(5):
        try:
            trig.off()
            time.sleep_us(2)
            trig.on()
            time.sleep_us(10)
            trig.off()
            
            durasi = time_pulse_us(echo, 1, 30000)
            if durasi < 0:
                print(f"    [{i+1}/5] ⚠️ Out of range / Error baca pantulan")
            else:
                jarak_cm = round(durasi / 58.0, 1)
                print(f"    [{i+1}/5] Jarak terukur: {jarak_cm} cm")
        except Exception as e:
            print(f"    [{i+1}/5] ⚠️ Error sistem: {e}")
        time.sleep(1)

def test_relay():
    print("\n[+] Menguji Modul Relay...")
    print("    -> Relay ON (Seharusnya ada bunyi 'KLIK' dan lampu indikator relay nyala)")
    relay.on()
    time.sleep(3) # Tahan 3 detik agar kamu bisa mengecek
    print("    -> Relay OFF (Bunyi 'KLIK' lagi)")
    relay.off()

def test_led():
    print("\n[+] Menguji Indikator LED...")
    
    print("    -> Merah ON (Pin 21)")
    led_merah.on()
    time.sleep(1.5)
    led_merah.off()
    
    print("    -> Kuning ON (Pin 22)")
    led_kuning.on()
    time.sleep(1.5)
    led_kuning.off()
    
    print("    -> Hijau ON (Pin 23)")
    led_hijau.on()
    time.sleep(1.5)
    led_hijau.off()
    print("    Selesai.")

# ==========================================
# MENU INTERAKTIF
# ==========================================
def tampilkan_menu():
    print("\n" + "="*35)
    print(" ALAT UJI HARDWARE - SMART HYDROPONIC")
    print("="*35)
    print("1. Test Sensor Suhu & Kelembaban (DHT11)")
    print("2. Test Sensor Jarak Air (HC-SR04)")
    print("3. Test Modul Pompa (Relay)")
    print("4. Test Indikator Lampu (LED)")
    print("5. Keluar")
    print("="*35)

try:
    while True:
        tampilkan_menu()
        pilihan = input("Pilih nomor komponen yang ingin diuji (1-5): ")
        
        if pilihan == '1':
            test_dht()
        elif pilihan == '2':
            test_hcsr04()
        elif pilihan == '3':
            test_relay()
        elif pilihan == '4':
            test_led()
        elif pilihan == '5':
            print("\n[!] Keluar dari mode pengujian.")
            break
        else:
            print("\n[x] Pilihan tidak valid. Masukkan angka 1 sampai 5.")
            
except KeyboardInterrupt:
    print("\n\n[!] Program dihentikan paksa oleh pengguna.")
finally:
    # Keamanan ekstra: Pastikan relay dan LED mati saat program ditutup
    relay.off()
    led_merah.off()
    led_kuning.off()
    led_hijau.off()
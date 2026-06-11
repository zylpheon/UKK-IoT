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
print("Mempersiapkan pin input/output...")

# Sensor
sensor_dht = dht.DHT11(Pin(PIN_DHT))
trig = Pin(PIN_TRIG, Pin.OUT)
echo = Pin(PIN_ECHO, Pin.IN)

# Aktuator (Set semua ke OFF/0 saat awal)
relay      = Pin(PIN_RELAY, Pin.OUT, value=0)
led_merah  = Pin(PIN_LED_R, Pin.OUT, value=0)
led_kuning = Pin(PIN_LED_Y, Pin.OUT, value=0)
led_hijau  = Pin(PIN_LED_G, Pin.OUT, value=0)

def ukur_jarak():
    """Fungsi ping ultrasonik untuk HC-SR04"""
    try:
        trig.off()
        time.sleep_us(2)
        trig.on()
        time.sleep_us(10)
        trig.off()
        
        # Timeout 30000 us (~5 meter)
        durasi = time_pulse_us(echo, 1, 30000) 
        if durasi < 0:
            return -1.0 # Error / Out of range
            
        jarak_cm = durasi / 58.0
        return round(jarak_cm, 1)
    except Exception as e:
        return -1.0

# ==========================================
# LOOP PENGUJIAN UTAMA
# ==========================================
print("\n" + "="*40)
print(" MULAI TESTING HARDWARE ")
print(" Tekan tombol STOP (Merah) di Thonny")
print(" untuk menghentikan program.")
print("="*40 + "\n")

try:
    while True:
        print("-" * 40)
        
        # 1. BACA DHT11
        try:
            sensor_dht.measure()
            suhu = sensor_dht.temperature()
            hum = sensor_dht.humidity()
            print(f"🌡️  DHT11   : Suhu {suhu}°C | Kelembaban {hum}%")
        except OSError:
            print("⚠️  DHT11   : Gagal! Periksa kabel SDA di D4.")
        
        # 2. BACA HC-SR04
        jarak = ukur_jarak()
        if jarak < 0:
            print("⚠️  HCSR04  : Gagal! Periksa kabel TRIG (D5) & ECHO (D18).")
        else:
            print(f"📏 HCSR04  : Jarak {jarak} cm")
            
        # 3. TEST LED & RELAY
        print("💡 Menguji LED & Relay...")
        
        # LED Merah ON
        led_merah.on()
        time.sleep(0.5)
        
        # LED Kuning ON
        led_merah.off()
        led_kuning.on()
        time.sleep(0.5)
        
        # LED Hijau ON
        led_kuning.off()
        led_hijau.on()
        time.sleep(0.5)
        
        # Matikan LED, Test Relay "Klik"
        led_hijau.off()
        relay.on()
        print("   -> Relay: ON (Bunyi klik?)")
        time.sleep(1) # Tahan relay 1 detik
        
        # Matikan Relay
        relay.off()
        print("   -> Relay: OFF")
        
        print("\n⏳ Menunggu 3 detik...\n")
        time.sleep(3)

except KeyboardInterrupt:
    # Blok ini dieksekusi jika kamu menekan tombol STOP di Thonny
    print("\n\n=== TESTING DIHENTIKAN ===")
    relay.off()
    led_merah.off()
    led_kuning.off()
    led_hijau.off()
    print("Semua pin aktuator telah dikembalikan ke OFF (Aman).")
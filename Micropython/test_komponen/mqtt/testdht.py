from machine import Pin
import dht
import time

# Pin 4 adalah D2 di papan ESP8266
sensor = dht.DHT11(Pin(4))

print("=== MEMULAI TEST DHT11 (ESP8266) ===")
print("Tunggu 2 detik untuk pemanasan sensor...")
time.sleep(2)

while True:
    try:
        sensor.measure()
        suhu = sensor.temperature()
        hum = sensor.humidity()
        print(f"🌡️ Suhu Ruangan: {suhu}°C | 💧 Kelembaban: {hum}%")
    except Exception as e:
        print("❌ Gagal membaca DHT11. Cek kabel datanya!", e)
    
    time.sleep(2)
from machine import Pin
import dht
import time

sensor_dht = dht.DHT11(Pin(4))

print("=== TEST SENSOR DHT11 ===")
while True:
    try:
        sensor_dht.measure()
        suhu = sensor_dht.temperature()
        hum = sensor_dht.humidity()
        print(f"🌡️ Suhu: {suhu}°C | 💧 Kelembaban: {hum}%")
    except OSError:
        print("⚠️ Gagal membaca DHT11. Cek kabel SDA di D4!")
    
    time.sleep(2)
# --- sensor.py ---
from machine import Pin
import dht
import time
import config

# Inisialisasi Hardware Sensor
dht_sensor = dht.DHT11(Pin(config.DHT_PIN))
trigger = Pin(config.TRIG_PIN, Pin.OUT)
echo = Pin(config.ECHO_PIN, Pin.IN)

def time_pulse_us(pin, level, timeout_us=30000):
    start = time.ticks_us()
    while pin.value() != level:
        if time.ticks_diff(time.ticks_us(), start) > timeout_us: return -1
    start = time.ticks_us()
    while pin.value() == level:
        if time.ticks_diff(time.ticks_us(), start) > timeout_us: return -1
    return time.ticks_diff(time.ticks_us(), start)

def ukur_jarak():
    try:
        trigger.off()
        time.sleep_us(2)
        trigger.on()
        time.sleep_us(10)
        trigger.off()
        durasi = time_pulse_us(echo, 1, 30000)
        if durasi < 0: return None
        return durasi / 58.0
    except:
        return None

def ukur_jarak_filtered(samples=3):
    values = []
    for _ in range(samples):
        val = ukur_jarak()
        if val is not None and config.TINGGI_MIN <= val <= config.TINGGI_MAX:
            values.append(val)
        time.sleep_ms(100)
    
    if not values: return None
    values.sort()
    return values[len(values)//2]

def baca_sensor():
    suhu, hum = 0.0, 0.0
    try:
        dht_sensor.measure()
        suhu = max(config.SUHU_MIN, min(config.SUHU_MAX, dht_sensor.temperature()))
        hum = max(config.KELEMBABAN_MIN, min(config.KELEMBABAN_MAX, dht_sensor.humidity()))
    except:
        pass
    
    tinggi = ukur_jarak_filtered(samples=3)
    tinggi = max(config.TINGGI_MIN, min(config.TINGGI_MAX, tinggi)) if tinggi is not None else 0.0
    return round(suhu, 2), round(hum, 1), round(tinggi, 1)

# Cari fungsi ini dan ubah isinya menjadi:
def tentukan_status(tinggi):
    if tinggi <= config.JARAK_PENUH: 
        return "NORMAL"
    elif tinggi >= config.JARAK_KOSONG: 
        return "DARURAT"
    else: 
        return "SIAGA"
from machine import Pin, time_pulse_us
import time

trig = Pin(5, Pin.OUT)
echo = Pin(18, Pin.IN)

print("=== TEST SENSOR ULTRASONIK HC-SR04 ===")
while True:
    try:
        trig.off()
        time.sleep_us(2)
        trig.on()
        time.sleep_us(10)
        trig.off()
        
        durasi = time_pulse_us(echo, 1, 30000)
        
        if durasi < 0:
            print("⚠️ Jarak di luar jangkauan / Error baca pantulan")
        else:
            jarak_cm = round(durasi / 58.0, 1)
            print(f"📏 Jarak terukur: {jarak_cm} cm")
            
    except Exception as e:
        print(f"⚠️ Error sistem: {e}")
        
    time.sleep(1)
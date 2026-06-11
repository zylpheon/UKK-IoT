from machine import Pin
import time

led_merah = Pin(21, Pin.OUT, value=0)
led_kuning = Pin(22, Pin.OUT, value=0)
led_hijau = Pin(23, Pin.OUT, value=0)

print("=== TEST INDIKATOR LED ===")
try:
    while True:
        print("🔴 Merah ON")
        led_merah.on()
        time.sleep(1)
        led_merah.off()
        
        print("🟡 Kuning ON")
        led_kuning.on()
        time.sleep(1)
        led_kuning.off()
        
        print("🟢 Hijau ON")
        led_hijau.on()
        time.sleep(1)
        led_hijau.off()
        
except KeyboardInterrupt:
    # Memastikan semua LED mati saat di-STOP
    led_merah.off()
    led_kuning.off()
    led_hijau.off()
    print("\nTest dihentikan, semua LED dimatikan.")
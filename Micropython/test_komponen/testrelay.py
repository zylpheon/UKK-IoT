from machine import Pin
import time

relay = Pin(19, Pin.OUT, value=0)

print("=== TEST MODUL RELAY ===")
try:
    while True:
        print("-> Relay ON (Bunyi KLIK)")
        relay.on()
        time.sleep(3)
        
        print("-> Relay OFF (Bunyi KLIK)")
        relay.off()
        time.sleep(3)
        
except KeyboardInterrupt:
    # Memastikan relay mati saat kamu menekan tombol STOP di Thonny
    relay.off()
    print("\nTest dihentikan, Relay dipastikan OFF.")
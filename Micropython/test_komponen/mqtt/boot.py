# boot.py - dieksekusi paling pertama oleh MicroPython
# Set pin relay ke HIGH (OFF) sedini mungkin agar pompa tidak nyala saat boot
from machine import Pin
Pin(19, Pin.OUT, value=0)  # Aktif-HIGH: LOW = relay OFF

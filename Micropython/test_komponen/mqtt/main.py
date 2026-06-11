# --- main.py ---
from machine import Pin, reset
import time
import gc

# ══════════════════════════════════════════════════════════════════
# SET PIN RELAY PALING PERTAMA sebelum import apapun
# Selama proses import, GPIO bisa floating → relay aktif terpicu
# Dengan set value=0 di sini, relay langsung OFF sejak awal
_relay_early = Pin(19, Pin.OUT, value=0)
# ══════════════════════════════════════════════════════════════════

import config
import sensor
import wifimanager
import mqtt_client   # ← menggantikan jaringan.py

# ── Inisialisasi pin indikator ────────────────────────────────────
led_power = Pin(config.LED_POWER, Pin.OUT)
led_pompa = Pin(config.LED_POMPA, Pin.OUT, value=0)  # aktif-HIGH
btn_boot  = Pin(0, Pin.IN, Pin.PULL_UP)

led_power.on()

# ── State global ──────────────────────────────────────────────────
MODE_OTOMATIS  = True
pompa_aktif    = False
last_kirim     = 0
wifi_fail_count = 0
WIFI_FAIL_MAX   = 3

# ── Logika kontrol pompa ──────────────────────────────────────────
def proses_perintah(perintah):
    """Terapkan perintah yang datang dari n8n via MQTT."""
    global MODE_OTOMATIS, pompa_aktif
    print(f"\n>> PERINTAH MASUK: {perintah}")
    if perintah == "MODE_AUTO":
        MODE_OTOMATIS = True
        print("   → Mode: OTOMATIS")
    elif perintah == "MODE_MANUAL":
        MODE_OTOMATIS = False
        print("   → Mode: MANUAL")
    elif perintah == "POMPA_ON":
        MODE_OTOMATIS = False
        pompa_aktif   = True
        print("   → Pompa: ON (manual)")
    elif perintah == "POMPA_OFF":
        MODE_OTOMATIS = False
        pompa_aktif   = False
        print("   → Pompa: OFF (manual)")

def logika_pompa_auto(tinggi):
    """Histeresis: nyala saat kosong, mati saat penuh."""
    global pompa_aktif
    if tinggi >= config.JARAK_KOSONG:
        pompa_aktif = True   # tandon kosong → pompa ON
    elif tinggi <= config.JARAK_PENUH:
        pompa_aktif = False  # tandon penuh  → pompa OFF
    # Di antara keduanya: pompa tetap di state sebelumnya (histeresis)

# ── Cek tombol BOOT ───────────────────────────────────────────────
def cek_tombol_boot():
    """Tahan 3 detik → hapus config WiFi → reboot ke portal."""
    if btn_boot.value() == 0:
        hold = 0
        while btn_boot.value() == 0:
            time.sleep(0.1)
            hold += 0.1
            if hold >= 3.0:
                print("\n[!] TOMBOL BOOT → Hapus config WiFi & Reboot...")
                wifimanager.clear_config()
                reset()

# ── Main ──────────────────────────────────────────────────────────
def main():
    global last_kirim, wifi_fail_count

    print("\n" + "=" * 50)
    print("Smart Hydroponic - MQTT Edition")
    print("=" * 50)

    # 1. Koneksi WiFi via WiFiManager
    print("[Boot] Memulai WiFi Manager...")
    if not wifimanager.ensure_connected():
        print("[Boot] WiFi gagal → reboot dalam 5 detik...")
        time.sleep(5)
        reset()

    # 2. Koneksi ke MQTT Broker
    print("[Boot] Menghubungkan ke MQTT Broker...")
    if not mqtt_client.connect():
        print("[Boot] MQTT gagal → reboot dalam 5 detik...")
        time.sleep(5)
        reset()

    loop_count = 0

    while True:
        gc.collect()
        loop_count += 1
        print(f"\n[Loop {loop_count}]", end=" ")

        # ── Cek & jaga koneksi WiFi ──────────────────────────────
        if not wifimanager.is_connected():
            print("WiFi terputus, reconnecting...")
            if not wifimanager.connect():
                wifi_fail_count += 1
                print(f"[!] Gagal koneksi WiFi ({wifi_fail_count}/{WIFI_FAIL_MAX})")
                if wifi_fail_count >= WIFI_FAIL_MAX:
                    print("[!] Terlalu banyak kegagalan → hapus config & reboot")
                    wifimanager.clear_config()
                    time.sleep(3)
                    reset()
                time.sleep(5)
                continue
            wifi_fail_count = 0

        # ── Pastikan MQTT tetap terhubung ────────────────────────
        mqtt_client.pastikan_terhubung()

        # ── Baca sensor ──────────────────────────────────────────
        suhu, hum, tinggi = sensor.baca_sensor()
        status_air = sensor.tentukan_status(tinggi)

        # ── Cek perintah dari n8n via MQTT ──────────────────────
        perintah = mqtt_client.cek_perintah()
        if perintah:
            proses_perintah(perintah)

        # ── Logika pompa ─────────────────────────────────────────
        if MODE_OTOMATIS:
            logika_pompa_auto(tinggi)
            mode_text = "AUTO"
        else:
            mode_text = "MANUAL"

        # Aktif-HIGH: 1 = relay ON (pompa nyala), 0 = relay OFF
        led_pompa.value(1 if pompa_aktif else 0)

        print(
            f"Suhu:{suhu}°C | Hum:{hum}% | Air:{tinggi}cm "
            f"[{status_air}] | Mode:{mode_text} | Pompa:{'ON' if pompa_aktif else 'OFF'}"
        )

        # ── Kirim data ke n8n via MQTT (tiap INTERVAL_KIRIM detik) ──
        now = time.time()
        if now - last_kirim >= config.INTERVAL_KIRIM:
            mqtt_client.kirim_sensor(suhu, hum, tinggi, status_air, pompa_aktif, MODE_OTOMATIS)
            last_kirim = now

        # ── Tunggu ~3 detik sambil pantau tombol BOOT ───────────
        for _ in range(30):
            cek_tombol_boot()
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDihentikan pengguna")
        led_pompa.value(0)
        led_power.off()
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        led_pompa.value(0)
        led_power.off()
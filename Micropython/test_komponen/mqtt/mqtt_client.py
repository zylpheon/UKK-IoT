# --- mqtt_client.py ---
# Menggantikan jaringan.py: komunikasi via MQTT broker (Node-RED)
# Tidak ada lagi urequests / ThingSpeak / TalkBack API

import time
import json
from machine import Pin
from umqtt.simple import MQTTClient
import config

led_wifi = Pin(config.LED_WIFI, Pin.OUT)
led_mqtt = Pin(config.LED_MQTT, Pin.OUT)

# ── State internal ────────────────────────────────────────────────
_client         = None       # objek MQTTClient aktif
_perintah_masuk = None       # perintah terakhir yang diterima via subscribe

# ── Callback subscribe ────────────────────────────────────────────
# ── Callback subscribe ────────────────────────────────────────────
def _on_message(topic, msg):
    """
    Dipanggil otomatis oleh umqtt setiap ada pesan masuk.
    Mendukung DUA format:
    1. JSON dari Node-RED -> {"command": "MODE_MANUAL"}
    2. Teks mentah dari n8n -> MODE_MANUAL
    """
    global _perintah_masuk
    try:
        # 1. Terjemahkan raw bytes menjadi teks biasa
        raw_str = msg.decode('utf-8').strip()
        cmd = ""
        
        # 2. Cek apakah teks ini bentuknya JSON (diawali '{')
        if raw_str.startswith('{'):
            try:
                data = json.loads(raw_str)
                cmd = data.get("command", "").strip().upper()
            except:
                cmd = raw_str.upper() # Fallback jika JSON rusak
        else:
            # 3. Jika bukan JSON, berarti ini teks mentah dari n8n
            cmd = raw_str.upper()
            
        if cmd:
            _perintah_masuk = cmd
            print(f"[MQTT] ← Perintah diterima: {cmd}")
            
    except Exception as e:
        print(f"[MQTT] Gagal parse pesan: {e} | raw: {msg}")

# ── Connect / Reconnect ───────────────────────────────────────────
def connect():
    """
    Buat koneksi baru ke broker MQTT dan subscribe ke topic command.
    Mengembalikan True jika berhasil.
    """
    global _client
    try:
        c = MQTTClient(
            client_id = config.MQTT_CLIENT_ID,
            server    = config.MQTT_BROKER,
            port      = config.MQTT_PORT,
            user      = config.MQTT_USER     or None,
            password  = config.MQTT_PASSWORD or None,
            keepalive = 60
        )
        c.set_callback(_on_message)
        c.connect()
        c.subscribe(config.TOPIC_COMMAND)
        _client = c
        led_mqtt.on()
        print(f"[MQTT] ✓ Terhubung ke {config.MQTT_BROKER}:{config.MQTT_PORT}")
        print(f"[MQTT] ✓ Subscribe → {config.TOPIC_COMMAND}")
        return True
    except Exception as e:
        print(f"[MQTT] ✗ Gagal connect: {e}")
        led_mqtt.off()
        _client = None
        return False

def pastikan_terhubung():
    """Reconnect jika belum / terputus. Dipanggil di awal setiap loop."""
    global _client
    if _client is None:
        return connect()
    # Coba ping ringan; jika gagal, reconnect
    try:
        _client.ping()
        return True
    except:
        print("[MQTT] Koneksi terputus, reconnecting...")
        _client = None
        led_mqtt.off()
        return connect()

# ── Publish sensor ────────────────────────────────────────────────
def kirim_sensor(suhu, hum, tinggi, status, pompa_hidup, mode_auto):
    """
    Publish data sensor ke topic hydroponic/sensor sebagai JSON.
    Payload cocok persis dengan yang diharapkan n8n MQTT workflow.
    """
    global _client
    if _client is None:
        print("[MQTT] Tidak terhubung, skip kirim.")
        return False
    try:
        payload = json.dumps({
            "suhu"      : suhu,
            "kelembaban": hum,
            "tinggi_air": tinggi,
            "status"    : status,
            "pompa"     : pompa_hidup,
            "mode"      : "AUTO" if mode_auto else "MANUAL",
            "timestamp" : time.time()
        })
        _client.publish(config.TOPIC_SENSOR, payload.encode())

        # Kedipkan LED MQTT 3x sebagai indikator berhasil kirim
        for _ in range(3):
            led_mqtt.off()
            time.sleep_ms(120)
            led_mqtt.on()
            time.sleep_ms(120)

        print(f"[MQTT] ↑ Terkirim → {config.TOPIC_SENSOR}: {payload}")
        return True
    except Exception as e:
        print(f"[MQTT] ✗ Gagal kirim: {e}")
        led_mqtt.off()
        _client = None   # tandai putus agar loop berikutnya reconnect
        return False

# ── Cek perintah masuk ───────────────────────────────────────────
def cek_perintah():
    """
    Panggil di setiap loop untuk:
    1. Memeriksa pesan baru dari broker (non-blocking check_msg).
    2. Mengambil perintah yang sudah di-buffer oleh callback.
    Mengembalikan string perintah atau None.
    """
    global _client, _perintah_masuk
    if _client is None:
        return None
    try:
        _client.check_msg()   # non-blocking, langsung return jika tidak ada pesan
    except Exception as e:
        print(f"[MQTT] check_msg error: {e}")
        _client = None
        led_mqtt.off()
        return None

    # Ambil dan reset buffer perintah
    cmd = _perintah_masuk
    _perintah_masuk = None
    return cmd

def is_connected():
    return _client is not None
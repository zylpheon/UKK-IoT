# --- config.py ---

# PIN DEFINITION
DHT_PIN    = 4
TRIG_PIN   = 5
ECHO_PIN   = 18
LED_POWER  = 21
LED_WIFI   = 22
LED_MQTT   = 23
RELAY_POMPA = 19

# KONFIGURASI JARINGAN
WIFI_SSID     = "pova6"
WIFI_PASSWORD = "gungun82"

# KONFIGURASI MQTT BROKER (Node-RED)
MQTT_BROKER   = "10.208.55.177"   # ← ganti dengan IP komputer/server Node-RED kamu
MQTT_PORT     = 1883
MQTT_USER     = ""                # kosongkan jika broker tidak pakai auth
MQTT_PASSWORD = ""                # kosongkan jika broker tidak pakai auth
MQTT_CLIENT_ID = "esp32-hydro-01"

# TOPIC MQTT
TOPIC_SENSOR  = "hydroponic/sensor"    # ESP32 → publish data sensor ke sini
TOPIC_COMMAND = "hydroponic/command"   # ESP32 ← subscribe perintah dari sini

# THRESHOLD & BOUNDARIES
JARAK_PENUH  = 5    # Jarak sensor ke air <= 5 cm  → tandon PENUH  (pompa OFF)
JARAK_KOSONG = 20   # Jarak sensor ke air >= 20 cm → tandon KOSONG (pompa ON)
SUHU_MIN     = -10
SUHU_MAX     = 50
KELEMBABAN_MIN = 0
KELEMBABAN_MAX = 100
TINGGI_MIN   = 0
TINGGI_MAX   = 50

# INTERVAL KIRIM DATA (detik)
INTERVAL_KIRIM = 15
import network
import socket
import json
import machine
import time
import os

try:
    with open("wifi.json") as f:
        wifi = json.load(f)
    ssid = wifi["ssid"]
    password = wifi.get("password", "")
except:
    ssid = password = ""

# --- Konfigurasi ---
AP_SSID = "Setup-WiFi"
AP_PASSWORD = ""  # Kosong = open network

# Pin LED (opsional)
try:
    from config import LED_WIFI
    led = machine.Pin(LED_WIFI, machine.Pin.OUT)
except:
    led = None

def blink_led(n=3, delay=0.2):
    if not led: return
    for _ in range(n):
        led.value(1)
        time.sleep(delay)
        led.value(0)
        time.sleep(delay)
        
def clear_config():
    """Hapus wifi.json untuk reset ke mode setup"""
    try:
        import os
        os.remove("wifi.json")
        print("[WiFi Manager] Config dihapus!")
    except OSError:
        pass

# --- Scan WiFi ---
def scan_networks():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    time.sleep(0.2)
    nets = []
    try:
        for ssid, _, _, _, _, _ in sta.scan():
            ssid_str = ssid.decode().strip()
            if ssid_str:
                nets.append(ssid_str)
    except:
        pass
    sta.active(False)
    return sorted(set(nets))

# --- Buat HTML sederhana ---
def build_page(ssids, error=""):
    opts = "".join(f'<option value="{s}">{s}</option>' for s in ssids)
    err_html = f'<p style="color:red;">{error}</p>' if error else ""
    return f"""<!DOCTYPE html>
<html>
<head><title>WiFi Setup</title></head>
<body>
<h2>Atur WiFi</h2>
<form method="POST">
SSID:<br>
<select name="ssid">{opts}</select><br><br>
Password:<br>
<input type="password" name="pass"><br><br>
<input type="submit" value="Simpan & Restart">
</form>
{err_html}
</body>
</html>"""

# --- Jalankan AP + Web Server Sederhana ---
def run_setup_portal():
    print("➡️  Menjalankan mode setup...")
    
    # Aktifkan AP
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    ip = ap.ifconfig()[0]
    print(f"🌐 Buka http://{ip} di browser")
    blink_led(5, 0.1)

    # Server HTTP mini
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(1)
    s.settimeout(30)  # Timeout 30 detik agar tidak hang selamanya

    ssids = scan_networks()

    while True:
        try:
            conn, addr = s.accept()
            print("📥 Request dari:", addr)
        except:
            print("⏰ Timeout! Portal ditutup.")
            ap.active(False)
            machine.reset()
            return

        try:
            request = conn.recv(1024).decode()
            
            if "POST /" in request:
                # Ambil data form (asumsi format sederhana)
                body = request.split("\r\n\r\n")[-1]
                lines = body.replace('+', ' ').split('&')
                data = {}
                for line in lines:
                    if '=' in line:
                        k, v = line.split('=', 1)
                        # Decode URL manual (minimal)
                        v = v.replace('%20', ' ').replace('%3D', '=')
                        data[k] = v
                
                ssid = data.get('ssid', '').strip()
                pwd = data.get('pass', '')

                if ssid:
                    with open('wifi.json', 'w') as f:
                        json.dump({'ssid': ssid, 'password': pwd}, f)
                    response = """HTTP/1.1 200 OK\nContent-Type: text/html\n\n
                    <h2>Berhasil!</h2><p>Menyimpan dan reboot...</p>
                    <script>setTimeout(() => location.href='/', 2000)</script>"""
                    conn.send(response.encode())
                    conn.close()
                    s.close()
                    ap.active(False)
                    time.sleep(1)
                    machine.reset()
                else:
                    html = build_page(ssids, "SSID wajib diisi!")
            else:
                html = build_page(ssids)

            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html.encode())
        except Exception as e:
            print("❌ Error:", e)
        finally:
            conn.close()

# --- Fungsi Utama ---
def _reset_wifi_driver():
    """
    Reset WiFi driver ESP32 sepenuhnya.
    Diperlukan untuk mengatasi 'Wifi Internal State Error' yang terjadi
    ketika driver crash akibat boot terlalu cepat atau brownout.
    """
    try:
        sta = network.WLAN(network.STA_IF)
        if sta.isconnected():
            sta.disconnect()
            time.sleep_ms(200)
        sta.active(False)
        time.sleep_ms(500)  # Tunggu driver benar-benar berhenti
        sta.active(True)
        time.sleep_ms(300)  # Tunggu driver siap menerima perintah
    except Exception as e:
        print(f"[WiFi Driver Reset] {e}")
        time.sleep_ms(500)

def ensure_connected():
    # Cek apakah sudah ada konfigurasi
    try:
        with open('wifi.json', 'r') as f:
            conf = json.load(f)
            ssid = conf['ssid']
            pwd = conf.get('password', '')
    except:
        print("📁 wifi.json tidak ditemukan → buka portal setup")
        run_setup_portal()
        return False

    # Coba koneksi dengan max 2 percobaan
    # Percobaan ke-2 didahului reset driver untuk tangani Internal State Error
    for attempt in range(2):
        if attempt > 0:
            print(f"[WiFi] Percobaan ke-{attempt + 1}, reset driver dulu...")
            _reset_wifi_driver()

        try:
            print(f"📡 Menghubungkan ke: {ssid}")
            sta = network.WLAN(network.STA_IF)
            sta.active(True)
            time.sleep_ms(200)  # Beri waktu driver siap sebelum connect
            sta.connect(ssid, pwd)

            for i in range(15):
                if sta.isconnected():
                    print("✅ WiFi terhubung! IP:", sta.ifconfig()[0])
                    if led: led.on()
                    return True
                time.sleep(1)
                if led: led.value(not led.value())  # Blink saat loading

        except Exception as e:
            print(f"[WiFi] Exception attempt {attempt + 1}: {e}")
            # Langsung lanjut ke percobaan berikutnya dengan driver reset

    print("❌ Gagal terhubung ke WiFi")
    if led: led.off()
    return False

def is_connected():
    """Periksa status koneksi WiFi"""
    try:
        sta = network.WLAN(network.STA_IF)
        return sta.isconnected()
    except:
        return False

def connect():
    """Coba koneksi ulang dengan driver reset terlebih dahulu"""
    _reset_wifi_driver()
    return ensure_connected()
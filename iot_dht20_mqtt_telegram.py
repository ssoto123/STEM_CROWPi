# === Práctica STEM Avanzada: IoT con DHT20, MQTT y Telegram ===
# Autor: MGTI. Saul Isai Soto Ortiz
# Descripción: Envía lecturas de temperatura y humedad del DHT20
#              a un servidor MQTT y también notifica por Telegram.

import time
import json
import board
import adafruit_ahtx0
import paho.mqtt.client as mqtt
import requests
import datetime

# --- Configuración del sensor DHT20 ---
i2c = board.I2C()
sensor = adafruit_ahtx0.AHTx0(i2c)

# --- Configuración del broker MQTT ---
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "crowpi/dht20/lecturas"
CLIENT_ID = "CrowPi_DHT20_Telegram"

# --- Configuración de Telegram ---
BOT_TOKEN = "AQUI_TU_TOKEN"     # 🔒 Sustituir por el token real de tu bot
CHAT_ID = "AQUI_TU_CHAT_ID"     # 🔒 Sustituir por tu chat_id
URL_TELEGRAM = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# --- Umbrales de alerta ---
TEMP_MAX = 30.0
HUM_MIN = 25.0
HUM_MAX = 75.0

# --- Conexión MQTT ---
client = mqtt.Client(CLIENT_ID)
try:
    print(f"🔌 Conectando al broker MQTT: {BROKER}:{PORT}")
    client.connect(BROKER, PORT, 60)
    print("✅ Conectado correctamente al broker MQTT.\n")
except Exception as e:
    print(f"❌ Error al conectar con el broker MQTT: {e}")
    exit()

# --- Función para enviar mensaje a Telegram ---
def enviar_telegram(mensaje):
    try:
        payload = {"chat_id": CHAT_ID, "text": mensaje}
        requests.post(URL_TELEGRAM, data=payload, timeout=5)
        print(f"📨 Mensaje enviado a Telegram: {mensaje}")
    except Exception as e:
        print(f"⚠️ Error al enviar mensaje a Telegram: {e}")

# --- Inicio del programa ---
print("🌡️ Iniciando monitoreo IoT con CrowPi + DHT20 + MQTT + Telegram")
print("Presiona Ctrl + C para detener.\n")

ultimo_envio = 0
intervalo_telegram = 60  # Enviar lectura cada 60 segundos

while True:
    try:
        # Lectura del sensor
        temp = round(sensor.temperature, 2)
        hum = round(sensor.relative_humidity, 2)
        timestamp = datetime.datetime.now().isoformat()

        # Crear mensaje JSON
        data = {
            "dispositivo": "CrowPi",
            "sensor": "DHT20",
            "temperatura_C": temp,
            "humedad_pct": hum,
            "fecha_hora": timestamp
        }
        payload = json.dumps(data)

        # Publicar en MQTT
        client.publish(TOPIC, payload)
        print(f"📤 MQTT -> {payload}")

        # Verificar si se debe enviar a Telegram
        tiempo_actual = time.time()
        if tiempo_actual - ultimo_envio >= intervalo_telegram:
            mensaje = (f"📡 Lectura IoT CrowPi\n"
                       f"🌡️ Temperatura: {temp} °C\n"
                       f"💧 Humedad: {hum} %\n"
                       f"🕒 {datetime.datetime.now().strftime('%H:%M:%S')}")
            enviar_telegram(mensaje)
            ultimo_envio = tiempo_actual

        # Enviar alertas si hay condiciones fuera de rango
        if temp > TEMP_MAX:
            enviar_telegram(f"⚠️ Alerta: Temperatura alta ({temp} °C)")
        if hum < HUM_MIN:
            enviar_telegram(f"⚠️ Alerta: Humedad muy baja ({hum} %)")
        if hum > HUM_MAX:
            enviar_telegram(f"⚠️ Alerta: Humedad muy alta ({hum} %)")

        time.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 Programa detenido por el usuario.")
        client.disconnect()
        break
    except Exception as e:
        print(f"⚠️ Error durante la lectura o envío: {e}")
        time.sleep(3)

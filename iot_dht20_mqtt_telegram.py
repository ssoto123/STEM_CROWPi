# === Práctica STEM Avanzada IoT con DHT20, MQTT, Telegram y Buzzer ===
# Autor: MGTI. Saul Isai Soto Ortiz
# Descripción: Envía lecturas del sensor DHT20 al servidor MQTT,
#              notifica por Telegram y permite controlar el buzzer remotamente.

import time
import json
import board
import adafruit_ahtx0
import paho.mqtt.client as mqtt
import requests
import datetime
from gpiozero import Buzzer

# --- Configuración del sensor DHT20 ---
i2c = board.I2C()
sensor = adafruit_ahtx0.AHTx0(i2c)

# --- Configuración del buzzer ---
buzzer = Buzzer(18)

# --- Configuración MQTT ---
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "crowpi/dht20/lecturas"
CLIENT_ID = "CrowPi_DHT20_Control"

# --- Configuración Telegram ---
BOT_TOKEN = "AQUI_TU_TOKEN"
CHAT_ID = "AQUI_TU_CHAT_ID"
URL_TELEGRAM = f"https://api.telegram.org/bot{BOT_TOKEN}/"
OFFSET = None  # para evitar leer mensajes viejos

# --- Umbrales ---
TEMP_MAX = 30.0
HUM_MIN = 25.0
HUM_MAX = 75.0

# --- Conexión MQTT ---
client = mqtt.Client(CLIENT_ID)
try:
    client.connect(BROKER, PORT, 60)
    print("✅ Conectado al broker MQTT.")
except Exception as e:
    print(f"❌ Error al conectar MQTT: {e}")
    exit()

# --- Función: enviar mensaje a Telegram ---
def enviar_telegram(mensaje):
    try:
        requests.post(URL_TELEGRAM + "sendMessage",
                      data={"chat_id": CHAT_ID, "text": mensaje},
                      timeout=5)
        print(f"📨 Telegram -> {mensaje}")
    except Exception as e:
        print(f"⚠️ Error al enviar mensaje: {e}")

# --- Función: revisar comandos desde Telegram ---
def leer_comandos():
    global OFFSET
    try:
        params = {"timeout": 5, "offset": OFFSET}
        resp = requests.get(URL_TELEGRAM + "getUpdates", params=params, timeout=5)
        data = resp.json()

        if "result" not in data:
            return

        for update in data["result"]:
            OFFSET = update["update_id"] + 1
            mensaje = update["message"]["text"].strip().lower()

            if mensaje == "/buzzer_on":
                buzzer.on()
                enviar_telegram("🔔 Buzzer activado desde Telegram.")
            elif mensaje == "/buzzer_off":
                buzzer.off()
                enviar_telegram("🔕 Buzzer desactivado desde Telegram.")
            elif mensaje == "/status":
                enviar_telegram("📡 CrowPi operativa. Sensor y MQTT funcionando.")
            elif mensaje == "/help":
                enviar_telegram("🧾 Comandos disponibles:\n"
                                "/buzzer_on - Activa el buzzer\n"
                                "/buzzer_off - Desactiva el buzzer\n"
                                "/status - Estado actual del sistema\n"
                                "/help - Mostrar ayuda")
    except Exception as e:
        print(f"⚠️ Error leyendo comandos: {e}")

# --- Programa principal ---
print("🌡️ Iniciando monitoreo IoT CrowPi DHT20 + MQTT + Telegram + Buzzer")
enviar_telegram("🤖 CrowPi iniciada. Escribe /help para ver los comandos disponibles.")

ultimo_envio = 0
intervalo_telegram = 60

while True:
    try:
        # Leer datos del sensor
        temp = round(sensor.temperature, 2)
        hum = round(sensor.relative_humidity, 2)
        timestamp = datetime.datetime.now().isoformat()

        # Crear paquete JSON
        data = {
            "dispositivo": "CrowPi",
            "sensor": "DHT20",
            "temperatura_C": temp,
            "humedad_pct": hum,
            "fecha_hora": timestamp
        }

        # Publicar en MQTT
        client.publish(TOPIC, json.dumps(data))
        print(f"📤 MQTT -> {data}")

        # Enviar lectura periódica a Telegram
        if time.time() - ultimo_envio > intervalo_telegram:
            mensaje = (f"📊 Lectura actual\n"
                       f"🌡️ Temp: {temp} °C\n"
                       f"💧 Hum: {hum} %")
            enviar_telegram(mensaje)
            ultimo_envio = time.time()

        # Revisar alertas
        if temp > TEMP_MAX:
            enviar_telegram(f"⚠️ Temperatura alta: {temp} °C")
            buzzer.beep(on_time=0.2, off_time=0.1, n=3)
        elif hum < HUM_MIN:
            enviar_telegram(f"⚠️ Humedad baja: {hum} %")
            buzzer.beep(on_time=0.2, off_time=0.1, n=2)
        elif hum > HUM_MAX:
            enviar_telegram(f"⚠️ Humedad alta: {hum} %")
            buzzer.beep(on_time=0.2, off_time=0.1, n=2)

        # Leer comandos de Telegram
        leer_comandos()

        time.sleep(5)

    except KeyboardInterrupt:
        buzzer.off()
        enviar_telegram("🛑 Monitoreo detenido manualmente.")
        client.disconnect()
        print("\nPrograma finalizado.")
        break
    except Exception as e:
        print(f"⚠️ Error en ciclo principal: {e}")
        time.sleep(3)

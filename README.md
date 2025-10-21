# STEM_CROWPi
Desarrollar una práctica de monitoreo IoT con la CrowPi, en la que el sensor DHT20 envíe las lecturas de temperatura y humedad a un servidor MQTT, y además se notifique automáticamente por Telegram cada cierto intervalo o al detectar condiciones de alerta.

# Introducción

En un entorno IoT, los sensores pueden comunicarse entre sí o con aplicaciones mediante protocolos como MQTT, y además generar alertas instantáneas a usuarios humanos a través de plataformas de mensajería como Telegram.

Esta práctica integra:

1. Lectura del sensor DHT20 (temperatura y humedad).

2. Publicación de las lecturas en un broker MQTT público o local.

3. Envío de mensajes automáticos a Telegram con los valores y alertas.

Tabla de Conexiones – DHT20 (I²C)
Conexión	Pin CrowPi (Raspberry Pi)	Descripción
VCC 🔴	    3.3 V	                   Alimentación
GND ⚫	    GND	                     Tierra
SDA 🟢	    GPIO 2 (Pin 3)	         Datos I²C
SCL 🔵	    GPIO 3 (Pin 5)	         Reloj I²C

# Requisitos de Software

Instala las siguientes librerías antes de ejecutar el código:

pip3 install adafruit-circuitpython-ahtx0 paho-mqtt requests

La librería requests permitirá realizar llamadas HTTP a la API de Telegram.

Configuración de Telegram

1.Abre Telegram y busca el bot @BotFather.

2.Crea un nuevo bot con el comando /newbot.

3.Guarda el TOKEN que te proporciona (por ejemplo: 1234567890:ABCDefGhIJKlmNoPQRStuVWxyZ).

4.Abre un chat con tu bot recién creado y envíale cualquier mensaje.

5.Luego, accede a: https://api.telegram.org/bot<TU_TOKEN>/getUpdates

# Código Principal – Envío de datos por MQTT y Telegram

Guarda este código como iot_dht20_mqtt_telegram.py y ejecútalo desde la terminal


# Comandos disponibles desde Telegram

Comandos:	
/buzzer_on	->Activa el buzzer de la CrowPi

/buzzer_off	->Desactiva el buzzer

/status	->Muestra el estado actual del sistema

/help	->Lista los comandos disponibles

# Retos Finales

Reto 1: Agregar un LED que se encienda cuando el buzzer esté activo.

Reto 2: Permitir cambiar el umbral de temperatura desde un comando de Telegram.



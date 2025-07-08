import discord
from discord.ext import commands
import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "10.56.13.11"
MQTT_PORT = 1883
TOPIC = "test/topic"

TOKEN = ""  # Poné acá tu token real de Discord

# Configuración de intents para Discord
intents = discord.Intents.default()
intents.message_content = True

# Crear el bot con intents configurados y prefijo /
bot = commands.Bot(command_prefix="/", intents=intents)

# Funciones callback MQTT
def on_connect(client, userdata, flags, reasonCode, properties=None):
    if reasonCode == mqtt.CONNACK_ACCEPTED:
        print("Conectado al broker MQTT local")
        client.subscribe(TOPIC)
        client.publish(TOPIC, "Hola desde el bot Python al conectar")
    else:
        print(f"Fallo en la conexión, código: {reasonCode}")

def on_message(client, userdata, msg):
    print(f"Mensaje recibido en {msg.topic}: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    print("Desconectado del broker. Código:", rc)
    while rc != 0:
        print("Reconectando...")
        try:
            rc = client.reconnect()
        except Exception as e:
            print("Error al reconectar:", e)
            time.sleep(5)

# Configurar cliente MQTT
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print("Error al conectar MQTT:", e)
    exit(1)

# Iniciar loop MQTT en segundo plano para no bloquear
mqtt_client.loop_start()

# Comandos del bot Discord
@bot.command()
async def encender(ctx):
    mqtt_client.publish(TOPIC, "ON")
    await ctx.send("LED encendido ✅")

@bot.command()
async def apagar(ctx):
    mqtt_client.publish(TOPIC, "OFF")
    await ctx.send("LED apagado ❌")

# Ejecutar bot Discord (esto bloquea la ejecución principal)
bot.run(TOKEN)

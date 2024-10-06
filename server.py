import discord
import os
from discord.ext import commands
from discord import app_commands

# Configurar los intents necesarios
intents = discord.Intents.default()
intents.message_content = True

# Crear una instancia del bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Se han sincronizado {len(synced)} comandos slash.')
    except Exception as e:
        print(f'Error al sincronizar comandos: {e}')

# Crear un comando slash
@bot.tree.command(name="hola", description="Saluda al bot")
async def hola(interaction: discord.Interaction):
    await interaction.response.send_message('¡Hola! Soy un bot de Discord.')

# Iniciar el bot con el token
bot.run(os.getenv('DISCORD_TOKEN'))

import discord
import os
from discord.ext import commands

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Evento: cuando el bot se conecta
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

# Comando simple
@bot.command()
async def hola(ctx):
    await ctx.send('¡Hola! Soy un bot de Discord.')

# Iniciar el bot con el token
bot.run(os.getenv('DISCORD_TOKEN'))

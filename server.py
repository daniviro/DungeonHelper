import discord
import os
from discord.ext import commands
from discord import app_commands

# Configurar los intents necesarios
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Necesario para trabajar con categorías y permisos

# Crear una instancia del bot
bot = commands.Bot(command_prefix="!", intents=intents)

ADMIN_ROLE_ID = 1290057105826644069

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

# Crear un comando slash
@bot.tree.command(name="crear_partida", description="Crea una categoría y canales para una partida de rol.")
async def crear_partida(interaction: discord.Interaction, master: discord.Member, jugadores: app_commands.Greedy[discord.Member]):
    guild = interaction.guild  # Servidor actual

    # Crear la categoría
    categoria = await guild.create_category(
        name=f"Partida de {master.name}",
        overwrites={
            guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Todos los demás no pueden ver
            guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(view_channel=True),  # Admins pueden ver
            master: discord.PermissionOverwrite(view_channel=True, mute_members=True),  # El master puede ver y silenciar
        }
    )

    # Añadir permisos para cada jugador mencionado
    for jugador in jugadores:
        await categoria.set_permissions(jugador, view_channel=True)

    # Crear los canales de texto y voz dentro de la categoría
    canal_texto = await guild.create_text_channel(f"texto-{master.name}", category=categoria)
    canal_voz = await guild.create_voice_channel(f"voz-{master.name}", category=categoria)

    # Responder al comando para confirmar la creación
    await interaction.response.send_message(
        f'Categoría y canales creados para la partida de {master.name}.',
        ephemeral=True  # Solo visible para la persona que ejecutó el comando
    )

# Iniciar el bot con el token
bot.run(os.getenv('DISCORD_TOKEN'))

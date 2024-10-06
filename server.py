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

# Check para verificar si el usuario es un administrador
def is_admin(interaction: discord.Interaction):
    return interaction.user.guild_permissions.administrator

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

# Crear un comando slash para crear partidas
@app_commands.check(is_admin)
@bot.tree.command(name="crear_partida", description="Crea una categoría y canales para una partida de rol.")
async def crear_partida(ctx, master: discord.Member, *, nombre: str = None):
    guild = ctx.guild  # Servidor actual

    # Verificar si el master tiene el rol de "Master verificado"
    master_role = discord.utils.get(guild.roles, name=MASTER_ROLE_NAME)
    if master_role not in master.roles:
        await ctx.send(f'El usuario {master.mention} no tiene el rol de "{MASTER_ROLE_NAME}".')
        return

    # Establecer el nombre de la categoría
    nombre_categoria = f"Sala de partida | {nombre if nombre else master.name}"

    # Comprobar si ya existe una categoría con ese nombre
    if discord.utils.get(guild.categories, name=nombre_categoria):
        await ctx.send(f'Ya existe una partida con el nombre "{nombre_categoria}". Elige otro nombre para la partida.')
        return

    await ctx.send("Por favor, menciona a los jugadores uno por uno. Escribe `done` cuando hayas terminado.")

    # Lista para almacenar los jugadores
    jugadores = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # Iniciar la recolección de jugadores
    while True:
        try:
            # Esperar la respuesta del usuario
            mensaje = await bot.wait_for('message', check=check, timeout=60)  # Timeout de 60 segundos

            # Eliminar el mensaje para que las menciones no lleguen a los jugadores
            await mensaje.delete()

            # Verificar si el mensaje es "done"
            if mensaje.content.lower() == 'done':
                break

            # Obtener el usuario mencionado
            if mensaje.mentions:
                jugador = mensaje.mentions[0]
                jugadores.append(jugador)
                await ctx.send(f'Jugador {jugador.mention} añadido.', delete_after=5)
            else:
                await ctx.send('Por favor, menciona a un usuario válido.', delete_after=5)

        except asyncio.TimeoutError:
            await ctx.send('Tiempo agotado. Operación cancelada.')
            return

    # Crear la categoría
    categoria = await guild.create_category(
        name=nombre_categoria,
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

    # Responder para confirmar la creación
    await ctx.send(f'Categoría y canales creados para la partida "{nombre_categoria}".')

# Crear un comando slash para eliminar una categoría y sus canales
@bot.tree.command(name="eliminar_partida", description="Elimina una partida y todos sus canales.")
@app_commands.check(is_admin)
async def eliminar_partida(ctx, *, nombre: str):
    guild = ctx.guild  # Servidor actual

    # Buscar la categoría que comience con "Sala de partida | "
    nombre_categoria = f"Sala de partida | {nombre}"
    categoria = discord.utils.get(guild.categories, name=nombre_categoria)

    if not categoria:
        # Si no encuentra con el nombre completo, intenta buscar si hay una que contiene el nombre
        for cat in guild.categories:
            if cat.name.startswith("Sala de partida | ") and (nombre in cat.name):
                categoria = cat
                break

    if categoria:
        # Eliminar todos los canales dentro de la categoría
        for canal in categoria.channels:
            await canal.delete()

        # Eliminar la categoría
        await categoria.delete()

        await ctx.send(f'La partida "{categoria.name}" y todos sus canales han sido eliminados.')
    else:
        await ctx.send(f'No se encontró ninguna partida de partida que coincida con "{nombre}".')

# Iniciar el bot con el token
bot.run(os.getenv('DISCORD_TOKEN'))

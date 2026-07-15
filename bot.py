import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from datetime import datetime, timezone
import json
import asyncio
from googleapiclient.discovery import build
import aiohttp
from dotenv import load_dotenv
import feedparser

load_dotenv()

LAST_VIDEO_FILE = "last_video.json"

token = os.getenv("TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

date = datetime.now(timezone.utc)
temp_voice_channels = {}


class MyBot(commands.Bot):
    async def setup_hook(self):
        self.add_view(TicketView())
        self.add_view(CloseTicketView())

        guild = discord.Object(id=1523482176828473414)
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)

        print(f"{len(synced)} commande(s) synchronisée(s)")
        for cmd in synced:
            print("-", cmd.name)

bot = MyBot(command_prefix="!", intents=intents)
cooldowns = {}


#------------------MESSAGES LOG CHANNEL-----------------------------

async def log_message_bot(embed):
    channel = bot.get_channel(1523708958295199884)
    
    if channel is None:
        return

    await channel.send(embed=embed)

async def log_message_tickets(embed):
    channel = bot.get_channel(1523709009964695642)
    
    if channel is None:
        return
        
    await channel.send(embed=embed)

async def log_message_yt_twitch(embed):
    channel = bot.get_channel(1524197585701568542)
    
    if channel is None:
        return
        
    await channel.send(embed=embed)
    


#------------------DEMARRAGE ET ARRETAGE DU BOT-----------------------------

@bot.event
async def on_ready():
    date = datetime.now(timezone.utc)

    if not check_youtube.is_running():
        check_youtube.start()

    if not hasattr(bot, "twitch_task"):
        bot.twitch_task = bot.loop.create_task(twitch_checker())

    embed = discord.Embed(
        title="🤖 BOT CONNECTION",
        description=f"=>{date}\n\n{bot.user} est connecté",
        color=0xFFFFFF
    )
    embed.timestamp = discord.utils.utcnow()

    print(f"\n\n=======================\n{date}\n\n{bot.user} est connecté !\n|||||||||||||||||||||||\n-")
    await log_message_bot(embed=embed)

@bot.event
async def on_disconnect():
    
    date = datetime.now(timezone.utc)

    embed = discord.Embed(
        title="🤖 BOT DISCONNECTED",
        description=f"=> {date}\n\n{bot.user} est déconnecté",
        color=discord.Color.orange()
    )
    embed.timestamp = discord.utils.utcnow()

    print(f"--\n{date}\n>>> {bot.user} est déconnecté\n--")
    await log_message_bot(embed=embed)



#------------------COMMANDES DU BOT-----------------------------

@bot.command()
async def ping(ctx):
    await ctx.send("yhhh im hereee")

@bot.command()
async def reseaux(ctx):

    await ctx.message.delete()

    embed=discord.Embed(title="**📱 MES RESEAUX**", description="Retrouve moi partout !\n", color=0xFF2D95)

    embed.add_field(name="🎥 YouTube", value="https://www.youtube.com/@daaks_s", inline=False)
    embed.add_field(name="🎮 Twitch", value="https://www.twitch.tv/daaks_s", inline=False)
    embed.add_field(name="📱 Tiktok", value="https://www.tiktok.com/@daaks_s\n", inline=False)

    embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/3007305b-acb6-4974-8526-74002dc52910-profile_image-300x300.png")
    embed.set_footer(text="\n\nSi vous êtes pas abonné à tous mes réseaux vous êtes ban (nan jrigole bien sur)\n\nMerci pour votre soutien 🩷\n")
    embed.set_image(url="https://yt3.googleusercontent.com/7Uzgf8Ho4SjM_0_yauJ6maj9sBTCDnr1lxMjD7fAaNzf705YHPq2Kf47ir9gS7ohTkzE6HPfX9c=w1707-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj")

    await ctx.send(embed=embed)

@bot.command()
async def reglement(ctx):

    await ctx.message.delete()
    
    embed=discord.Embed(title="📜 **RÈGLEMENT**", 
                        description="**Bienvenue sur Daaks Central !** \nVoici quelques règles importantes à suivre pour garantir une expérience agréable pour tous :",
                        color=0x34495E
                        )
    
    embed.add_field(name="**🤝 Respect des Membres**",
                    value="• Respectez toujours les autres membres du serveur.\n• Pas de harcèlement, de discours haineux, ou de comportement offensant.",
                    inline=False
    )
    embed.add_field(name="🔞 **Contenu approprié**",
                    value="• Pas de contenu inapproprié, adulte, ou offensant.\n• Évitez les discussions politiques ou religieuses sensibles.",
                    inline=False
    )
    embed.add_field(name="🚫 **Spam et Publicité**",
                    value="• Pas de spam, de flood, ou de messages répétitifs\n• Pas de publicité non autorisée par les admins.",
                    inline=False
    )
    embed.add_field(name="📌 **Canaux Appropriés**",
                    value="• Utilisez les canaux de manière appropriée selon leur thème.\n• Évitez le hors-sujet dans les discussions.",
                    inline=False
    )
    embed.add_field(name="💬 **Langage et Ton**",
                    value="• Utilisez un langage respectueux et courtois.\n• Évitez les majuscules excessives ou le langage vulgaire.",
                    inline=False
    )
    embed.add_field(name="⚠️ **Respect des Modérateurs**",
                    value="• Suivez les instructions des modérateurs.\n• Respectez leur décision.",
                    inline=False
    )
    embed.add_field(name="🔒 **Protection des Données et DOX**",
                    value="• Ne partagez pas d'informations personnelles. Qu'elles soient à vous ou quelqu'un   d'autre.\n• Respectez la vie privée des autres membres.",
                    inline=False
    )
    embed.add_field(name="​🎈 **Respect des TOS**",
                    value="• Les Terms of Services de Discord s'appliquent également sur ce serveur. Merci de les respecter.\n  (https://discord.com/terms)",
                    inline=False
    )
    embed.set_footer(text="En rejoignant ce serveur, vous acceptez de respecter ces règles. En cas de non-respect, des mesures pourront être prises par l'équipe de modération.\nCe règlement est sujet à modification. Veuillez le consulter régulièrement pour rester à jour."
    )

    await ctx.send(embed=embed)
    
@bot.command()
@commands.has_permissions(administrator=True)
async def openticket(ctx):

    await ctx.message.delete()

    await ctx.send(
        "🎟️ **Support Tickets**\n\nClique sur le bouton pour ouvrir un ticket.\n\n",
        view=TicketView()
    )

@bot.command()
async def closeticket(ctx):

    await ctx.message.delete()

    channel = ctx.channel
    guild = ctx.guild
    creator = None

    if channel.topic:
        creator = guild.get_member(int(channel.topic))

    channel_name = channel.name

    # Vérifie que la commande est utilisée dans un ticket
    if not ctx.channel.name.startswith("ticket-"):
        await ctx.send("❌ Cette commande ne peut être utilisée que dans un ticket.")
        return

    role_tickets = discord.utils.get(ctx.guild.roles, name="<tickets>")

    has_ticket_role = (
        role_tickets is not None
        and role_tickets in ctx.author.roles
    )

    if (
        not has_ticket_role
        and not ctx.author.guild_permissions.manage_channels
    ):
        await ctx.send("❌ Tu n'as pas la permission de fermer ce ticket.", ephemeral=True)
        return

    await ctx.send("🔒 Fermeture du ticket...")

    messages = []

    async for msg in channel.history(limit=200, oldest_first=True):
        messages.append({
            "author": str(msg.author),
            "content": msg.content,
            "time": str(msg.created_at)
        })

    now = datetime.now(timezone.utc)
    formatted_date = now.strftime("%d.%m.%y_%Hh%M")

    data = {
        "channel_name": channel.name,
        "closed_by": str(ctx.author),
        "closed_at": str(datetime.now(timezone.utc)),
        "messages": messages
    }
        
    if not os.path.exists("tickets_backup"):
        os.makedirs("tickets_backup")

    filename = f"{channel.name}_{formatted_date}.json"
    file_path = os.path.join("tickets_backup", filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"--> {datetime.now(timezone.utc)} Ticket fermé : {channel_name} par {ctx.author}")

    embed=discord.Embed(title="🗑️ **CLOSE TICKET** (commande)", description=date, color=0xE67E22)

    embed.add_field(name="Ticket fermé", value=f"{channel.mention} {channel.name}")
    embed.add_field(name="Ticket par", value=f"{creator.mention if creator else 'Inconnu'}", inline=False)
    embed.add_field(name="PAR", value=ctx.author.mention, inline=False)

    embed.timestamp = discord.utils.utcnow()

    await log_message_tickets(embed=embed)

    log_channel = discord.utils.get(guild.text_channels, name="backup-tickets")

    if log_channel is None:
        print("Salon de logs introuvable.")
    else:
        await log_channel.send(
            content=f"📁 Backup du ticket **{channel.name}** fermé par {ctx.author.mention}",
            file=discord.File(file_path)
        )

    await channel.delete()


@bot.tree.command(name="say", description="Envoie un message dans un salon")
@app_commands.checks.has_permissions(administrator=True)
async def say(interaction: discord.Interaction, salon: discord.TextChannel, message: str):
    message = message.replace("\\n", "\n")
    await salon.send(message)
    await interaction.response.send_message("Message envoyé ✅", ephemeral=True)

@say.error
async def say_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Tu n'as pas les permissions administrateur pour utiliser cette commande.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ Tu n'as pas les permissions administrateur pour utiliser cette commande.",
                ephemeral=True
            )
    else:
        raise error
    

@bot.tree.command(name="ban", description="Bannit un membre")
@app_commands.describe(member="Le membre a bannir", reason="Raison du ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member:discord.Member, reason: str = "Aucune Raison"):

    try:
        date = datetime.now(timezone.utc)
        duration = datetime.now(timezone.utc) - member.joined_at

        if member.joined_at:
            duration = datetime.now(timezone.utc) - member.joined_at

            days = duration.days
            hours = duration.seconds // 3600
            minutes = (duration.seconds // 60) % 60
            seconds = duration.seconds % 60
        else:
            days = hours = minutes = seconds = 0

        await member.ban(reason=reason)

        await interaction.response.send_message(
        f"✅ {member.mention} a été banni par {interaction.user}."
    )

        embed=discord.Embed(title="🔒BAN COMMANDE", description=f"{date}", color=discord.Color.red(),timestamp=datetime.now(timezone.utc))

        embed.add_field(name="👤MEMBRE", value=f"{member.mention}\n{member.id}", inline=False)
        embed.add_field(name="🛠️PAR", value=f"{interaction.user.mention}\n{interaction.user.id}", inline=False)
        embed.add_field(name="🗒️RAISON", value=reason or "Aucune raison", inline=False)
        embed.add_field(name="📅JOIN", value=f"{member.joined_at.strftime('%d/%m/%y %H:%M:%S')}", inline=False)
        embed.add_field(name="⌛PRESENT DEPUIS", value=f"{days}j {hours}h {minutes}m et {seconds}s")
        embed.add_field(name="👥Membres restant", value=f"{interaction.guild.member_count}", inline=False)

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await log_message_bot(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Je n'ai pas la permission de bannir ce membre.",
            ephemeral=True
        )

    except discord.HTTPException:
        await interaction.response.send_message(
            "❌ Discord a refusé la requête de bannissement.",
            ephemeral=True
        )

    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"❌ Une erreur est survenue : `{e}`",
                ephemeral=True
            )

@ban.error
async def ban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
    

@bot.tree.command(name="deban", description="Enlève le ban de quelqu'un")
@app_commands.describe(user="Utilisateur à débannir", reason="Raison du déban")
@app_commands.checks.has_permissions(ban_members=True)
async def deban(interaction: discord.Interaction, user: str, reason: str = "Aucune Raison"):
    guild = interaction.guild

    try:
        date = datetime.now(timezone.utc)

        user_id = int(user)
        discord_user = await bot.fetch_user(user_id)
        await guild.unban(discord_user, reason=reason)

        await interaction.response.send_message(f"{discord_user} a été débanni par {interaction.user}", ephemeral=True)

        embed=discord.Embed(title="🔓DEBAN COMMANDE", description=f"{date}", color=0x1B5E20)

        embed.add_field(name="👤MEMBRE", value=f"{discord_user.mention} ({discord_user.id})")
        embed.add_field(name="🗒️RAISON", value=reason or "Aucune raison", inline=False)
        embed.add_field(name="🛠️PAR", value=f"{interaction.user.mention} ({interaction.user.id})")
        embed.add_field(name="👥Membres restant", value=f"{interaction.guild.member_count}", inline=False)

        embed.set_thumbnail(url=discord_user.display_avatar.url)

        embed.timestamp = discord.utils.utcnow()

        await log_message_bot(embed=embed)

    except ValueError:
        await interaction.response.send_message("❌ L'identifiant utilisateur est invalide.", ephemeral=True)

    except discord.NotFound:
        await interaction.response.send_message("❌ Cet utilisatuer n'est pas banni.", ephemeral=True)

@deban.autocomplete("user")
async def deban_autocomplete(
    interaction: discord.Interaction,
    current: str
):
    bans = [ban async for ban in interaction.guild.bans()]

    results = []

    for ban in bans:
        username = f"{ban.user.name} ({ban.user.id})"

        if current.lower() in username.lower():
            results.append(
                app_commands.Choice(
                    name=username[:100],
                    value=str(ban.user.id)
                )
            )

    return results[:25]

@deban.error
async def unban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)


@bot.tree.command(name="botvoc", description="Connecte le bot à votre salon vocal.")
async def botvoc(interaction: discord.Interaction):

    if interaction.user.voice is None:
        await interaction.response.send_message(
            "❌ Vous devez être connecté à un salon vocal.",
            ephemeral=True
        )
        return

    channel = interaction.user.voice.channel

    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.move_to(channel)
    else:
        await channel.connect()

    await interaction.response.send_message(
        f"✅ Connecté à **{channel.name}**, {channel.mention}."
    )


@bot.tree.command(name="botdevoc", description="Déconnecte le bot du salon vocal.")
async def botdevoc(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        await interaction.response.send_message(
            "❌ Connecté à aucun salon vocal.",
            ephemeral=True
        )
        return

    await voice_client.disconnect()
    await interaction.response.send_message("Déconnecté du salon vocal.")



#------------------JOIN ET LEAVE D'UN MEMBRE-----------------------------

@bot.event
async def on_member_join(member):

        date = datetime.now(timezone.utc)
        channel = bot.get_channel(1523708958295199884)

        embed2 = discord.Embed(
            title="JOIN",
            description=f"{date}\n\n{member} {member.mention} ({member.id}) a rejoint le serveur\nNombre de membres : {member.guild.member_count}",
            color=discord.Color.green()
        )
        embed2.timestamp = discord.utils.utcnow()

        print(f"--> {date}, {member} a rejoint le serveur, {member.guild.member_count} membres")
        await channel.send(embed=embed2)

        voc_member_channel = bot.get_channel(1524892090893467699)

        await voc_member_channel.edit(
        name=f"👥 MEMBRES : {voc_member_channel.guild.member_count}")
        

@bot.event
async def on_member_update(before, after):
    channel = bot.get_channel(1524876662087614605)
    role_id = 1524238134760571082

    role = after.guild.get_role(role_id)

    if role in after.roles and role not in before.roles:

        if channel:
            date = datetime.now(timezone.utc)

            embed1 = discord.Embed(
            title=f"🔥 MAIS NAN UN NOUVEAU MEMBRE ! 🔥",
            description=(
                f"Bienvenue {after.mention} sur le serveur !\n*Nous sommes maintenant {after.guild.member_count} membres 🎉*"),

            color=discord.Color.gold())

            embed1.set_thumbnail(url=after.display_avatar.url)

            print(f"{date}, {after} a obtenu le role Membre")

            await channel.send(f"{after.mention}", embed=embed1)




#ban/deban/kick

@bot.event
async def on_member_ban(guild, user):

    date = datetime.now(timezone.utc)
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        if entry.target.id == user.id:

            moderateur = entry.user
            raison = entry.reason

            embed=discord.Embed(title="BAN DISCORD", description=f"{date}", color=discord.Color.red())
            
            embed.add_field(name="👤MEMBRE", value=f"{user.mention} ({user.id})", inline=False)
            embed.add_field(name="🛠️PAR", value=f"{moderateur} ({entry.user.id})", inline=False)
            embed.add_field(name="🗒️RAISON", value=raison or "Aucune raison", inline=False)
            embed.add_field(name="👥Membres restant", value=f"{guild.member_count}", inline=False)

            embed.timestamp = discord.utils.utcnow()

            print(f"--> {date}\n\n{user} s'est fait ban par {moderateur}\nRaison : {entry.reason or 'Aucune raison'}\n{user.guild.member_count} membres à présent\n")
            await log_message_bot(embed=embed)

            return
        
@bot.event
async def on_member_unban(guild, user):
    salon = discord.utils.get(guild.text_channels, name="logs-join-leave-member")
    date = datetime.now(timezone.utc)

    if not salon:
        return
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        if entry.target.id == user.id:
            moderateur = entry.user
            raison = entry.reason

            print(f"--> {date}\n\n{user} s'est fait deban par {moderateur}\n\n{user.guild.member_count} membres à présent\n")

            embed=discord.Embed(title="DEBAN DISCORD", description=f"{date}", color=0x1B5E20)
            
            embed.add_field(name="👤MEMBRE", value=f"{user.mention} ({user.id})", inline=False)
            embed.add_field(name="🛠️PAR", value=f"{moderateur} ({entry.user.id})", inline=False)
            embed.add_field(name="🗒️RAISON", value=raison or "Aucune raison", inline=False)
            embed.add_field(name="👥Membres restant", value=f"{guild.member_count}", inline=False)

            embed.timestamp = discord.utils.utcnow()

            await log_message_bot(embed=embed)

@bot.event
async def on_member_remove(member):

    voc_member_channel = bot.get_channel(1524892090893467699)

    await voc_member_channel.edit(name=f"👥 MEMBRES : {voc_member_channel.guild.member_count}")

    is_kick=False

    date = datetime.now(timezone.utc)

    print(f"on_member_remove appelé pour {member}")

    if member.joined_at is None:
        return

    duration = datetime.now(timezone.utc) - member.joined_at

    datejoin = member.joined_at
    date = datetime.now(timezone.utc)

    days = duration.days
    hours = duration.seconds //3600
    minutes = (duration.seconds // 60) % 60
    seconds = duration.seconds - (((duration.seconds // 60) % 60) * 60)
    totalseconds = duration.seconds


    await asyncio.sleep(2)  # Laisse le temps aux logs d'audit de se mettre à jour

            
    #kick
    async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        print("KICK LOG TROUVE :", entry.user, entry.target)

        if entry.target.id == member.id:
            if (datetime.now(timezone.utc) - entry.created_at).total_seconds() < 10:
                is_kick = True

                print("KICK DETECTE")

                salon = member.guild.get_channel(1523708958295199884)
                print("SALON :", salon)

                if salon:
                    print("ENVOI EMBED")
                    embed=discord.Embed(title="KICK", description=f"{date}", color=0xFF8FA3)

                    embed.add_field(name="MEMBRE", value=member.mention, inline=True)
                    embed.add_field(name="PAR", value=entry.user.mention, inline=True)
                    embed.add_field(name="RAISON", value=entry.reason or 'Aucune raison', inline=False)
                    embed.add_field(name="REJOINT", value=datejoin, inline=False)
                    embed.add_field(name="LA DEPUIS", value=f"{days}j {hours}h {minutes}m {seconds}s\n{totalseconds}s au total", inline=False)
                    embed.add_field(name="MEMBRES RESTANT", value=member.guild.member_count, inline=False)

                    embed.timestamp = discord.utils.utcnow()

                    print(f"--> {date}\n\n{member} s'est fait kick par {entry.user}\nRaison : {entry.reason or 'Aucune raison'}\nRejoint : {datejoin}\nLà depuis {days}j {hours}h {minutes}m {seconds}s\n{totalseconds}s au total\n{member.guild.member_count} membres à présent\n")
                    #await log_message_bot(bot, guild, f">>> --------------------------\n{date}\n\n{member} ({member.mention}) s'est fait kick par {entry.user}\nRaison : {entry.reason or 'Aucune raison'}\nRejoint : {datejoin}\nLà depuis {days}j {hours}h {minutes}m {seconds}s\n{totalseconds}s au total\n{member.guild.member_count} membres à présent\n--------------------------")
                    await log_message_bot(embed=embed)

                break

    #juste leave
    if not is_kick:
        channel = member.guild.get_channel(1523708958295199884)
        if channel:
            print(f"--> {date}\n\n{member} a quitte le serveur \nRejoint : {datejoin}\nLà depuis {days}j {hours}h {minutes}m {seconds}s  ({totalseconds}s au total), {member.guild.member_count} membres")
            embed=discord.Embed(title="LEAVE", description=f"{date}", color=0xFF2D95)

            embed.add_field(name="MEMBRE", value=member.mention, inline=False)
            embed.add_field(name="REJOINT", value=datejoin, inline=False)
            embed.add_field(name="LA DEPUIS", value=f"{days}j {hours}h {minutes}m {seconds}s\n{totalseconds}s au total", inline=False)
            embed.add_field(name="MEMBRES RESTANT", value=member.guild.member_count, inline=False)

            embed.timestamp = discord.utils.utcnow()
            
            await channel.send(embed=embed)
            #bot,
            #guild, 
            #f">>> --------------------------\n{date}\n\n{member} ({member.mention}) a quitte le serveur\nRejoint : {datejoin}\nLà depuis {days}j {hours}h {minutes}m {seconds}s\n{totalseconds}s au total\n{member.guild.member_count} membres à présent\n--------------------------")



#------------------NOTIF YOUTUBE/TWITCH/TIKTOK-----------------------------
    #YOUTUBE

CHANNEL_ID = "UCp3tPPcNwm0Pta4AlEnybkw"

LAST_VIDEO_FILE = "last_video.json"

def load_last_video():
    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE, "r") as f:
            return json.load(f).get("video_id")
    return None


def save_last_video(video_id):
    with open(LAST_VIDEO_FILE, "w") as f:
        json.dump({"video_id": video_id}, f)


async def get_latest_video():
    date = datetime.now(timezone.utc)

    print("CHANNEL_ID :", CHANNEL_ID)

    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
    print(url)

    feed = feedparser.parse(url)

    print("Nombre d'entrées :", len(feed.entries))

    if feed.entries:
        print("Titre :", feed.entries[0].title)
        print("ID :", feed.entries[0].yt_videoid)


    if not feed.entries:
        return None, None

    TITRE_LAST_YT_VIDEO = feed.entries[0].title
    ID_LAST_YT_VIDEO = feed.entries[0].yt_videoid

    embed = discord.Embed(
        title="LOOP CHECK YOUTUBE",
        description=f"=> {date}\n\nCHANNEL ID : {CHANNEL_ID}\nURL : {url}\nNOMBRE D'ENTREES : {len(feed.entries)}\n\n\n__LAST VIDEO__\n\nTitre : {TITRE_LAST_YT_VIDEO}\nID : {ID_LAST_YT_VIDEO}",
        color=0xFF2D95
    )
    embed.timestamp = discord.utils.utcnow()

    latest = feed.entries[0]

    video_id = latest.yt_videoid
    title = latest.title

    await log_message_yt_twitch(embed=embed) 

    return video_id, title



@tasks.loop(minutes=2)
async def check_youtube():
    channel = bot.get_channel(1524875316349112392)

    date = datetime.now(timezone.utc)

    if channel is None:
        return

    latest_id, title = await get_latest_video()

    if latest_id is None:
        return

    last_id = load_last_video()

    if last_id is None:
        save_last_video(latest_id)
        return

    if latest_id != last_id:
        save_last_video(latest_id)

        embed=discord.Embed(title=f"{title}", url=f"https://www.youtube.com/watch?v={latest_id}", color=discord.Color.red())

        embed.set_author(name="Daaks", icon_url="https://static-cdn.jtvnw.net/jtv_user_pictures/3007305b-acb6-4974-8526-74002dc52910-profile_image-300x300.png", url="https://www.youtube.com/@Daaks")
        embed.set_image(url=f"https://img.youtube.com/vi/{latest_id}/maxresdefault.jpg")
        embed.set_footer(text="YouTube", icon_url="https://www.youtube.com/yts/img/favicon_144-vfliLAfaB.png")
        embed.timestamp = discord.utils.utcnow()

        embed1=discord.Embed(title=f"NOTIF NOUVELLE VIDEO YOUTUBE", description=f"{date}\n\n{title}\nhttps://www.youtube.com/watch?v={latest_id}", color=discord.Color.red())
        
        embed1.set_author(name="Daaks", icon_url="https://static-cdn.jtvnw.net/jtv_user_pictures/3007305b-acb6-4974-8526-74002dc52910-profile_image-300x300.png", url="https://www.youtube.com/@Daaks")
        embed1.timestamp = discord.utils.utcnow()

        await channel.send(
            "🎥 **Nouvelle vidéo @everyone** 🎥\n", embed=embed)
        
        await log_message_yt_twitch(embed=embed1)


    #TWITCH

async def get_twitch_token():
    url = "https://id.twitch.tv/oauth2/token"

    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, params=params) as response:
                if response.status != 200:
                    print(f"Erreur Twitch : {response.status}")
                    print(await response.text())
                    return None
                data = await response.json()
                return data["access_token"]
            
        except Exception as e:
            print(f"Erreur lors de la récupération du token Twitch : {e}")
            return None
        
async def check_twitch_live(token):
        
    try:

        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {token}"
        }

        username = TWITCH_USERNAME

        async with aiohttp.ClientSession() as session:

            # récupérer l'id Twitch de la chaîne
            async with session.get(
                "https://api.twitch.tv/helix/users",
                headers=headers,
                params={"login": username}
            ) as response:

                user = await response.json()

                print("Status users :", response.status)
                print("User JSON :", user)
                user_id = user["data"][0]["id"]

            # vérifier le live
            async with session.get(
                "https://api.twitch.tv/helix/streams",
                headers=headers,
                params={"user_id": user_id}
            ) as response:

                stream = await response.json()
                print("Status streams :", response.status)
                print("Stream JSON :", stream)

                if stream["data"]:
                    return {
                        "title": stream["data"][0]["title"],
                        "game": stream["data"][0]["game_name"],
                        "viewers": stream["data"][0]["viewer_count"],
                        "thumbnail": stream["data"][0]["thumbnail_url"],
                        "username": user["data"][0]["display_name"],
                        "profile_image": user["data"][0]["profile_image_url"]
                    }

                return None
            
    except Exception as e:
        print("Erreur check_twitch_live :", repr(e))
        return None

twitch_live = False


async def twitch_checker():
    print(TWITCH_USERNAME)
    print("Client ID :", TWITCH_CLIENT_ID[:5])

    print("Twitch checker lancé")
    channel = bot.get_channel(1523702876596338930)

    global twitch_live

    while True:
        print("Nouvelle vérification")

        token = await get_twitch_token()
        print("Token :", token is not None)

        if token is None:
            await asyncio.sleep(60)
            continue

        live = await check_twitch_live(token)
        print("Live :", live)


        if live and not twitch_live:
                
            try:

                twitch_live = True
                

                embed=discord.Embed(
                    title=live["title"],
                    url="https://twitch.tv/daaks_s",
                    color=discord.Color.purple()
                )

                embed.set_author(name="Daaks", icon_url="https://static-cdn.jtvnw.net/jtv_user_pictures/3007305b-acb6-4974-8526-74002dc52910-profile_image-300x300.png", url="https://twitch.tv/daaks_s")

                embed.add_field(
                    name="🎮 JEU",
                    value=live["game"],
                    inline=True
                )

                embed.add_field(
                    name="👤 Viewers",
                    value=str(live["viewers"]),
                    inline=True
                )

                thumbnail = live["thumbnail"]

                thumbnail = thumbnail.replace(
                    "{width}",
                    "1280"
                ).replace(
                    "{height}",
                    "720"
                )

                embed.set_footer(text="Twitch", icon_url="https://static.twitchcdn.net/assets/favicon-32-e29e246c157142c94346.png")
                embed.timestamp = discord.utils.utcnow()

                embed.set_image(url=thumbnail)

                await channel.send(
                    "**🟪 EN LIVE @everyone 🟪**", embed=embed
                )


                streamtitle = live["title"]
                categorie = live["game"]
                embed2=discord.Embed(title="NOTIF STREAN TWITCH", description=f"{date}\n\nTITRE : {streamtitle}\nCATEGORIE : {categorie}\nhttps://twitch.tv/daaks_s", color=discord.Color.blurple())
                embed2.timestamp = discord.utils.utcnow()

                await log_message_yt_twitch(embed=embed2)

            except Exception as e:
                print("Erreur twitch :", e)

        elif not live:

            twitch_live = False


        await asyncio.sleep(60)



#------------------TICKETS-----------------------------

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎟️ Ouvrir un ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        member = interaction.user

        await interaction.response.defer(ephemeral=True)

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
        if existing:
            await interaction.followup.send("❌ Tu as déjà un ticket.", ephemeral=True)
            return

        category = discord.utils.get(guild.categories, name="TICKETS")
        role_tickets = discord.utils.get(guild.roles, name="<tickets>")
        

        if category is None:
            await interaction.followup.send("❌ Catégorie introuvable.", ephemeral=True)
            return

        if role_tickets is None:
            await interaction.followup.send("❌ Rôle introuvable.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            role_tickets: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{member.name}",
            category=category,
            overwrites=overwrites,
            topic=str(member.id)
        )

        print(f"--> {datetime.now(timezone.utc)} Ticket créé : {channel.name} par {member} | ID: {channel.id}")

        embed=discord.Embed(title="🎟️ **OPEN TICKET**", description=datetime.now(timezone.utc), color=0x2ECC71)

        embed.add_field(name="Ticket créé", value=f"{channel.mention} {channel.name}", inline=False)
        embed.add_field(name="PAR", value=member.mention, inline=False)

        await log_message_tickets(embed=embed)

        await interaction.followup.send(
            f"✅ Ticket créé : {channel.mention}",
            ephemeral=True
        )
    
        embed = discord.Embed(
            title=f"🎟️ TICKET par {member.display_name}",
            description=(f"{member.mention} décris ta demande :\n\n• Explique clairement\n• Ajoute des screenshots si besoin\n• Pas de spam\n• Respect du staff"),
            color=discord.Color.purple()
        )

        await channel.send(
            content=f"{role_tickets.mention}, {member.mention}",
            allowed_mentions=discord.AllowedMentions(roles=True)
        )

        await channel.send(
            embed=embed,
            view=CloseTicketView()
        )

class AddMemberView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder="Choisis un membre à ajouter",
        min_values=1,
        max_values=1
    )
    async def select_member(self, interaction: discord.Interaction, select: discord.ui.UserSelect):

        user = select.values[0]
        channel = interaction.channel

        await channel.set_permissions(
            user,
            view_channel=True,
            send_messages=True,
            read_messages=True
        )

        await interaction.response.send_message(
            f"✅ {user.mention} a été ajouté au ticket.",
            ephemeral=True
        )

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fermer le ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        channel = interaction.channel
        guild = channel.guild
        creator = None

        if channel.topic:
            creator = guild.get_member(int(channel.topic))

        channel_name = channel.name
        role_tickets = discord.utils.get(interaction.guild.roles, name="<tickets>")
        date = {datetime.now(timezone.utc)}

        if (role_tickets not in interaction.user.roles and not interaction.user.guild_permissions.manage_channels):
            await interaction.response.send_message("❌ Tu n'as pas la permission de fermer ce ticket.",ephemeral=True)
            return
        
        await interaction.response.send_message("🔒 Fermeture du ticket...", ephemeral=True)
        
        messages = []

        async for msg in channel.history(limit=200, oldest_first=True):
            messages.append({
                "author": str(msg.author),
                "content": msg.content,
                "time": str(msg.created_at)
            })

        now = datetime.now(timezone.utc)
        formatted_date = now.strftime("%d.%m.%y_%Hh%M")

        data = {
            "channel_name": channel.name,
            "closed_by": str(interaction.user),
            "closed_at": str(datetime.now(timezone.utc)),
            "messages": messages
        }
        
        if not os.path.exists("tickets_backup"):
            os.makedirs("tickets_backup")

        filename = f"{channel.name}_{formatted_date}.json"
        file_path = os.path.join("tickets_backup", filename)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"--> {datetime.now(timezone.utc)} Ticket fermé : {channel_name} par {interaction.user}")

        embed=discord.Embed(title="🗑️ **CLOSE TICKET**", description=datetime.now(timezone.utc), color=0xE67E22)

        embed.add_field(name="Ticket fermé", value=f"{channel.mention} {channel.name}")
        embed.add_field(name="Ticket par", value=f"{creator.mention if creator else 'Inconnu'}", inline=False)
        embed.add_field(name="PAR", value=interaction.user.mention, inline=False)


        await log_message_tickets(embed=embed)

        log_channel = discord.utils.get(guild.text_channels, name="backup-tickets")

        if log_channel is None:
            print("Salon de logs introuvable.")
        else:
            await log_channel.send(
                content=f"📁 Backup du ticket **{channel.name}** fermé par {interaction.user.mention}",
                file=discord.File(file_path)
            )

        await channel.delete()



    @discord.ui.button(label="➕ Ajouter un membre", style=discord.ButtonStyle.secondary, custom_id="add_member_ticket")
    async def add_member(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        member = interaction.user

        role = discord.utils.get(guild.roles, name="<tickets>")

        if role not in member.roles:
            await interaction.response.send_message(
                "❌ Tu n'as pas la permission d'ajouter des membres.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "👤 Mentionne la personne à ajouter ",
            view=AddMemberView(),
            ephemeral=True
        )

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=120)
        except:
            await interaction.followup.send("❌ Temps écoulé.", ephemeral=True)
            return

        await msg.delete()

        if not msg.mentions:
            await interaction.followup.send("❌ Aucun utilisateur détecté.", ephemeral=True)
            return

        user = msg.mentions[0]
        channel = interaction.channel

        await channel.set_permissions(user, view_channel=True, send_messages=True)

        await interaction.followup.send(
            f"✅ Utilisateur ajouté.",
            ephemeral=True
        )



#------------------SALONS VOCAUX TEMPORAIRES-----------------------------

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild

    create_channel = discord.utils.get(guild.voice_channels, name="Créez votre salon")
    category = discord.utils.get(guild.categories, name="⌜VOCAUX⌟")

    if after.channel == create_channel:

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=False),
            member: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, connect=True, manage_channels=True, manage_permissions=True)
        }

        channel = await guild.create_voice_channel(
            name=f"🔊 vocal-{member.name}",
            category=category,  
            overwrites=overwrites
        )
        temp_voice_channels[channel.id] = member.id

        await member.move_to(channel)

        embed=discord.Embed(title="⚒️**COMMANDES SALON VOCAL TEMPORAIRE**", 
                            description=f"{member.mention}, gère ton salon vocal personnel avec ces commandes :",
                            color=0x9B59B6
                            )
        embed.add_field(
                        name="🔒 Gestion",
                        value="""
                    `/lock` • Bloquer l'accès au vocal
                    `/unlock` • Ouvrir l'accès au vocal
                    `/rename` • Renommer le salon
                    `/limit` • Modifier la limite
                    """,
                        inline=False
                    )

        embed.add_field(
                        name="👥 Membres",
                        value="""
                    `/add` • Autoriser un membre
                    `/remove` • Retirer un membre
                    `/owner` • Transférer la propriété
                    """,
                        inline=False
                    )

        embed.set_footer(
                        text="Système de vocaux temporaires"
                    )
        
        embed.timestamp = discord.utils.utcnow()

        await channel.send(content=f"{member.mention}", embed=embed)
        
    if before.channel != after.channel:
        if after.channel and after.channel != create_channel:
            print(f"--> {datetime.now(timezone.utc)} {member} a rejoint : {after.channel.name}")
        
    if before.channel and before.channel != after.channel:
        print(f"\n--> {datetime.now(timezone.utc)} {member} a quitté : {before.channel.name}")
        
    if before.channel and before.channel.id in temp_voice_channels:
        if len(before.channel.members) == 0:
            try:
                del temp_voice_channels[before.channel.id]
                await before.channel.delete()

                print(f"--> {datetime.now(timezone.utc)} supprimé : {before.channel.name}")

            except discord.NotFound:
                pass

    # Slash commands voc temp

@bot.tree.command(name="lock", description="Verrouille ton salon vocal temporaire")
async def lock(interaction: discord.Interaction):

    member = interaction.user

    # Vérifie que le membre est dans un vocal
    if member.voice is None or member.voice.channel is None:
        await interaction.response.send_message(
            "❌ Tu dois être dans ton salon vocal.",
            ephemeral=True
        )
        return

    channel = member.voice.channel

    # Vérifie que c'est un vocal temporaire
    if channel.id not in temp_voice_channels:
        await interaction.response.send_message(
            "❌ Ce n'est pas un salon vocal temporaire.",
            ephemeral=True
        )
        return

    # Vérifie que c'est le propriétaire
    if temp_voice_channels[channel.id] != member.id:
        await interaction.response.send_message(
            "❌ Tu n'es pas le propriétaire de ce salon.",
            ephemeral=True
        )
        return

    # Verrouille le salon
    await channel.set_permissions(
        interaction.guild.default_role,
        connect=False,
        view_channel=True
    )

    await interaction.response.send_message(
        "🔒 Ton salon est maintenant **privé**.",
        ephemeral=True
    )

@bot.tree.command(name="unlock", description="Déverrouille ton salon vocal temporaire")
async def unlock(interaction: discord.Interaction):

    member = interaction.user

    # Vérifie que le membre est dans un vocal
    if member.voice is None or member.voice.channel is None:
        await interaction.response.send_message(
            "❌ Tu dois être dans ton salon vocal.",
            ephemeral=True
        )
        return

    channel = member.voice.channel

    # Vérifie que c'est un vocal temporaire
    if channel.id not in temp_voice_channels:
        await interaction.response.send_message(
            "❌ Ce n'est pas un salon vocal temporaire.",
            ephemeral=True
        )
        return

    # Vérifie que c'est le propriétaire
    if temp_voice_channels[channel.id] != member.id:
        await interaction.response.send_message(
            "❌ Tu n'es pas le propriétaire de ce salon.",
            ephemeral=True
        )
        return

    # Déverrouille le salon
    await channel.set_permissions(
        interaction.guild.default_role,
        connect=True,
        view_channel=True
    )

    await interaction.response.send_message(
        "🔓 Ton salon est maintenant **public**.",
        ephemeral=True
    )

@bot.tree.command(name="add", description="Autorise un membre à rejoindre ton salon vocal temporaire")
async def add(interaction: discord.Interaction, membre: discord.Member):

    user = interaction.user

    # Vérifie que le membre est dans un vocal
    if user.voice is None or user.voice.channel is None:
        await interaction.response.send_message(
            "❌ Tu dois être dans ton salon vocal.",
            ephemeral=True
        )
        return

    channel = user.voice.channel

    # Vérifie que c'est un vocal temporaire
    if channel.id not in temp_voice_channels:
        await interaction.response.send_message(
            "❌ Ce n'est pas un salon vocal temporaire.",
            ephemeral=True
        )
        return

    # Vérifie que c'est le propriétaire
    if temp_voice_channels[channel.id] != user.id:
        await interaction.response.send_message(
            "❌ Tu n'es pas le propriétaire de ce salon.",
            ephemeral=True
        )
        return

    # Ajoute la permission au membre
    await channel.set_permissions(
        membre,
        view_channel=True,
        connect=True,
        speak=True
    )

    await interaction.response.send_message(
        f"✅ {membre.mention} peut maintenant rejoindre ton vocal.",
        ephemeral=True
    )

@bot.tree.command(name="remove", description="Retire l'accès à un membre de ton salon vocal temporaire")
async def remove(interaction: discord.Interaction, membre: discord.Member):

    user = interaction.user

    # Vérifie que le membre est dans un vocal
    if user.voice is None or user.voice.channel is None:
        await interaction.response.send_message(
            "❌ Tu dois être dans ton salon vocal.",
            ephemeral=True
        )
        return

    channel = user.voice.channel

    # Vérifie que c'est un vocal temporaire
    if channel.id not in temp_voice_channels:
        await interaction.response.send_message(
            "❌ Ce n'est pas un salon vocal temporaire.",
            ephemeral=True
        )
        return

    # Vérifie que c'est le propriétaire
    if temp_voice_channels[channel.id] != user.id:
        await interaction.response.send_message(
            "❌ Tu n'es pas le propriétaire de ce salon.",
            ephemeral=True
        )
        return

    # Retire les permissions du membre
    await channel.set_permissions(
        membre,
        overwrite=None
    )

    # Déconnecte la personne si elle est dans ce vocal
    if membre.voice and membre.voice.channel == channel:
        await membre.move_to(None)

    await interaction.response.send_message(
        f"✅ {membre.mention} n'a plus accès à ton vocal.",
        ephemeral=True
    )

@bot.tree.command(name="rename", description="Renomme ton salon vocal")
async def rename(interaction: discord.Interaction, nom: str):

    user = interaction.user

    # Vérifie que le membre est dans un vocal
    if user.voice is None or user.voice.channel is None:
        await interaction.response.send_message(
            "❌ Tu dois être dans ton salon vocal.",
            ephemeral=True
        )
        return

    channel = user.voice.channel

    # Vérifie que c'est un vocal temporaire
    if channel.id not in temp_voice_channels:
        await interaction.response.send_message(
            "❌ Ce n'est pas un salon vocal temporaire.",
            ephemeral=True
        )
        return

    # Vérifie que c'est le propriétaire
    if temp_voice_channels[channel.id] != user.id:
        await interaction.response.send_message(
            "❌ Tu n'es pas le propriétaire de ce salon.",
            ephemeral=True
        )
        return
    
    if len(nom) > 90:
        await interaction.response.send_message(
            "❌ Nom trop long.",
            ephemeral=True
        )
        return

    # Renomme le salon
    await channel.edit(name=f"🔊 {nom}")

    await interaction.response.send_message(
        f"✅ Salon renommé en **🔊 {nom}**.",
        ephemeral=True
    )

@bot.tree.command(name="limit", description="Change la limite de ton salon vocal temporaire (0=♾️)")
async def limit(interaction: discord.Interaction, nombre: int):

    user = interaction.user

    # Vérifie que le membre est dans un vocal
    if user.voice is None or user.voice.channel is None:
        await interaction.response.send_message(
            "❌ Tu dois être dans ton salon vocal.",
            ephemeral=True
        )
        return

    channel = user.voice.channel

    # Vérifie que c'est un vocal temporaire
    if channel.id not in temp_voice_channels:
        await interaction.response.send_message(
            "❌ Ce n'est pas un salon vocal temporaire.",
            ephemeral=True
        )
        return

    # Vérifie que c'est le propriétaire
    if temp_voice_channels[channel.id] != user.id:
        await interaction.response.send_message(
            "❌ Tu n'es pas le propriétaire de ce salon.",
            ephemeral=True
        )
        return

    # Vérifie la limite
    if nombre < 0 or nombre > 99:
        await interaction.response.send_message(
            "❌ La limite doit être entre **0 et 99**.",
            ephemeral=True
        )
        return

    # Applique la limite
    await channel.edit(user_limit=nombre)

    if nombre == 0:
        await interaction.response.send_message(
            "✅ La limite du vocal a été retirée.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"✅ Limite du vocal changée à **{nombre} personnes**.",
            ephemeral=True
        )

@bot.tree.command(name="owner", description="Transfère la propriété de ton salon vocal")
async def owner(interaction: discord.Interaction, membre: discord.Member):

    user = interaction.user

    # Vérifie que le membre est dans un vocal
    if user.voice is None or user.voice.channel is None:
        await interaction.response.send_message(
            "❌ Tu dois être dans ton salon vocal.",
            ephemeral=True
        )
        return

    channel = user.voice.channel

    # Vérifie que c'est un vocal temporaire
    if channel.id not in temp_voice_channels:
        await interaction.response.send_message(
            "❌ Ce n'est pas un salon vocal temporaire.",
            ephemeral=True
        )
        return

    # Vérifie que c'est le propriétaire
    if temp_voice_channels[channel.id] != user.id:
        await interaction.response.send_message(
            "❌ Tu n'es pas le propriétaire de ce salon.",
            ephemeral=True
        )
        return

    # Empêche de donner à un bot
    if membre.bot:
        await interaction.response.send_message(
            "❌ Tu ne peux pas donner la propriété à un bot.",
            ephemeral=True
        )
        return

    # Vérifie que la personne est dans le même vocal
    if membre.voice is None or membre.voice.channel != channel:
        await interaction.response.send_message(
            "❌ Cette personne doit être dans ton salon vocal.",
            ephemeral=True
        )
        return

    # Change le propriétaire
    temp_voice_channels[channel.id] = membre.id

    await interaction.response.send_message(
        f"👑 {membre.mention} est maintenant le propriétaire du vocal.",
        ephemeral=True
    )














bot.run(token) #(toujours a la fin)

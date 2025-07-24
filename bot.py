import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from git_ignore.token_bot import TOKEN

# Channel IDs
VERIFY_CHANNEL = 1397573547395911731
WELCOME_CHANNEL = 1397574415386153040
BOOT_COMMAND_ADMIN = 1397573101990187239
USER_INFO_CHANNEL = 1397573231770079232
ADMIN_LOG_CHANNEL = 1397943758154367077
SUBMITTED_IDEAS_CHANNEL = 1397890496172527667
BOTCOMMAND_USER = 1397577442809479260
SUBMITTING_IDEAS_CHANNEL = 1397891479497740409
TICKET_ROOM = 1397891479497740409

# Role IDs
VERIFY_ROLE_ID = 1397576960468582521
DEVOPS_MEMBER_ROLE_ID = 1397574892509200527

USERS_FILE = "users.json"
TICKET_FILE = "ticket_counter.json"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


user_data = load_json(USERS_FILE, {})
ticket_data = load_json(TICKET_FILE, {"last_ticket": 0})


class VerifyModal(discord.ui.Modal, title="אימות משתמש"):
    full_name = discord.ui.TextInput(label="שם מלא", min_length=2)
    phone = discord.ui.TextInput(label="מספר טלפון", min_length=3)

    def __init__(self, member: discord.Member):
        super().__init__()
        self.member = member

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        verify_role = guild.get_role(VERIFY_ROLE_ID)
        devops_role = guild.get_role(DEVOPS_MEMBER_ROLE_ID)

        if verify_role and verify_role in self.member.roles:
            await self.member.remove_roles(verify_role)
        if devops_role and devops_role not in self.member.roles:
            await self.member.add_roles(devops_role)

        try:
            await self.member.edit(nick=str(self.full_name))
        except discord.Forbidden:
            pass

        user_data[str(self.member.id)] = {
            "name": str(self.full_name),
            "phone": str(self.phone),
        }
        save_json(USERS_FILE, user_data)

        info_channel = guild.get_channel(USER_INFO_CHANNEL)
        if info_channel:
            embed = discord.Embed(title="משתמש עבר אימות", color=0x00ff00)
            embed.add_field(name="שם", value=str(self.full_name), inline=False)
            embed.add_field(name="טלפון", value=str(self.phone), inline=False)
            embed.set_footer(text=f"ID: {self.member.id}")
            await info_channel.send(embed=embed)

        await interaction.response.send_message(
            content="האימות הושלם בהצלחה!", ephemeral=False
        )


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="אימות", style=discord.ButtonStyle.success)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerifyModal(interaction.user))


class IdeaModal(discord.ui.Modal, title="שליחת רעיון"):
    name = discord.ui.TextInput(label="שם", min_length=2)
    idea = discord.ui.TextInput(label="הרעיון", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(SUBMITTED_IDEAS_CHANNEL)
        if channel:
            embed = discord.Embed(title="רעיון חדש", color=0x00ffcc)
            embed.add_field(name="שם", value=str(self.name), inline=False)
            embed.add_field(name="רעיון", value=str(self.idea), inline=False)
            await channel.send(embed=embed)
        await interaction.response.send_message(
            content="הרעיון נשלח", ephemeral=False
        )


class IdeaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="שליחת רעיון", style=discord.ButtonStyle.primary)
    async def send_idea(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IdeaModal())


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="פתיחת טיקט", style=discord.ButtonStyle.primary)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        counter = ticket_data.get("last_ticket", 0) + 1
        ticket_data["last_ticket"] = counter
        save_json(TICKET_FILE, ticket_data)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        for role in guild.roles:
            if role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True
                )

        channel = await guild.create_text_channel(
            name=f"ticket-{counter}", overwrites=overwrites
        )
        await channel.send(f"{member.mention} תודה שפתחת טיקט")
        await interaction.response.send_message(
            content=f"נפתח טיקט <#{channel.id}>", ephemeral=False
        )


async def send_or_edit(channel: discord.TextChannel, content: str | None, view: discord.ui.View):
    async for msg in channel.history(limit=50):
        if msg.author == bot.user:
            await msg.edit(content=content, view=view)
            return
    await channel.send(content=content, view=view)


@bot.event
async def on_ready():
    guild = bot.guilds[0] if bot.guilds else None
    print(f"Logged in as {bot.user}")
    if not guild:
        return

    verify_channel = guild.get_channel(VERIFY_CHANNEL)
    ideas_channel = guild.get_channel(SUBMITTING_IDEAS_CHANNEL)
    ticket_channel = guild.get_channel(TICKET_ROOM)

    if verify_channel:
        await send_or_edit(
            verify_channel,
            content="לחצו על הכפתור לאימות",
            view=VerifyView(),
        )

    if ideas_channel:
        await send_or_edit(
            ideas_channel,
            content="שליחת רעיון",
            view=IdeaView(),
        )

    if ticket_channel:
        await send_or_edit(
            ticket_channel,
            content="לחצו לפתיחת טיקט",
            view=TicketView(),
        )

    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)


@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(WELCOME_CHANNEL)
    if channel:
        embed = discord.Embed(
            title=f"ברוך הבא {member.display_name}", color=0x00ff00
        )
        await channel.send(embed=embed)


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return ctx.author.guild_permissions.administrator and ctx.channel.id == BOOT_COMMAND_ADMIN

    @app_commands.command(name="reset_verify_button", description="איפוס הודעת האימות")
    async def reset_verify_button(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "אין לך הרשאה", ephemeral=False
            )
            return
        if interaction.channel.id != BOOT_COMMAND_ADMIN:
            await interaction.response.send_message(
                "לא ניתן להריץ כאן", ephemeral=False
            )
            return

        channel = interaction.guild.get_channel(VERIFY_CHANNEL)
        if channel:
            async for msg in channel.history(limit=50):
                if msg.author == bot.user:
                    await msg.delete()
            await channel.send(content="לחצו על הכפתור לאימות", view=VerifyView())

        log = interaction.guild.get_channel(ADMIN_LOG_CHANNEL)
        if log:
            embed = discord.Embed(
                title="פעולת אדמין", description=f"{interaction.user} איפס את כפתור האימות"
            )
            await log.send(embed=embed)

        await interaction.response.send_message(
            "כפתור האימות אופס", ephemeral=False
        )


async def setup():
    await bot.add_cog(Admin(bot))


if __name__ == "__main__":
    import asyncio

    asyncio.run(setup())
    bot.run(TOKEN)

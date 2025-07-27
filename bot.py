import discord
from discord.ext import commands
from config import token

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # חובה בשביל on_member_join

bot = commands.Bot(command_prefix="!", intents=intents)

# ====== יצירת כפתור  vrrify אם רול =================================================================================================================================
# === View מתמיד לכפתור האימות ===
class VerifyButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="אמת אותי",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="verify_button"
    )
    async def verify_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_to_add = interaction.guild.get_role(1397574892509200527)   # הרול להוספה
        role_to_remove = interaction.guild.get_role(1397576960468582521)  # הרול להסרה
        if role_to_add:
            await interaction.user.add_roles(role_to_add)
        if role_to_remove and role_to_remove in interaction.user.roles:
            await interaction.user.remove_roles(role_to_remove)
        await interaction.response.send_message("האימות הצליח! רול עודכן.", ephemeral=True)

# === פונקציה לחיבור או יצירת כפתור האימות ===
async def create_or_attach_verify_button(bot):
    channel = bot.get_channel(1397573547395911731)

    # בדיקה אם כבר קיימת הודעה עם הכפתור
    async for msg in channel.history(limit=50):
        if msg.author == bot.user and "אימות המשתמש" in (msg.embeds[0].title if msg.embeds else ""):
            await msg.edit(view=VerifyButtonView())  # חיבור מחדש לכפתור
            return

    # אם לא קיימת הודעה — צור חדשה
    embed = discord.Embed(
        title="אימות המשתמש",
        description="לאימות המשתמש, לחץ על הכפתור למטה.",
        color=0x00FF00
    )
    await channel.send(embed=embed, view=VerifyButtonView())

#========================================================================================================================================================================        

# ====== פקודת שליחת כפתור =====================================================================================================================================================
@bot.tree.command(name="verify_box", description="שלח הודעת אימות עם כפתור")
async def verify_box(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator and interaction.channel.id == 1397573547395911731:
        await create_or_attach_verify_button()
        await interaction.response.send_message("הודעת אימות נשלחה!", ephemeral=True)
    else:
        await interaction.response.send_message("!!אין לך הרשאה או חדר לא מתאים", ephemeral=True)

# ====== on_ready =================================================================================================================================================================
# === שליחת כפתור + מודאל לרעיונות ===
# === מודאל שליחת רעיון עם תיבה גדולה ===
class IdeaModal(discord.ui.Modal):
    def __init__(self, result_channel_id: int):
        super().__init__(title="שליחת רעיון")
        self.result_channel_id = result_channel_id
        
        # שדה שם קצר
        self.name = discord.ui.TextInput(
            label="!הכנס את שמך צדיק",
            style=discord.TextStyle.short,
            max_length=100
        )
        
        # שדה רעיון - תיבת טקסט גדולה
        self.idea = discord.ui.TextInput(
            label="? מהו רעיונך",
            style=discord.TextStyle.paragraph,  # MULTILINE
            max_length=1000,
            required=True,
            placeholder="פתח פיך ויאירו דברך"
        )
        
        self.add_item(self.name)
        self.add_item(self.idea)

    async def on_submit(self, interaction: discord.Interaction):
        result_channel = interaction.client.get_channel(self.result_channel_id)
        embed = discord.Embed(
            title="רעיון חדש!",
            description=f"**שם:** {self.name.value}\n**רעיון:** {self.idea.value}",
            color=0x00FF00
        )
        await result_channel.send(embed=embed)
        await interaction.response.send_message("הרעיון נשלח בהצלחה!", ephemeral=True)

# === View מתמיד עם הכפתור ===
class IdeaButtonView(discord.ui.View):
    def __init__(self, result_channel_id: int):
        super().__init__(timeout=None)
        self.result_channel_id = result_channel_id

    @discord.ui.button(label="שלח רעיון", style=discord.ButtonStyle.green, custom_id="idea_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(IdeaModal(self.result_channel_id))

# === יצירת או חיבור מחדש לכפתור ===
async def create_or_attach_idea_button(bot):
    channel_id = 1397891479497740409        # חדר עם הכפתור
    result_channel_id = 1397890496172527667  # חדר שאליו נשלחים הרעיונות
    channel = bot.get_channel(channel_id)

    # חיפוש הודעה קיימת עם הכפתור
    async for msg in channel.history(limit=50):
        if msg.author == bot.user and "אימות רעיון" in (msg.embeds[0].title if msg.embeds else ""):
            await msg.edit(view=IdeaButtonView(result_channel_id))  # חיבור מחדש
            return

    # אם אין הודעה – ליצור חדשה
    embed = discord.Embed(
        title="אימות רעיון",
        description="לחץ על הכפתור כדי לשלוח שם ורעיון.",
        color=0x00FF00
    )
    await channel.send(embed=embed, view=IdeaButtonView(result_channel_id))


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@bot.event
async def on_ready():
    print("הבוט עלה בהצלחה")
    await create_or_attach_verify_button(bot)
    await bot.tree.sync()  
    await create_or_attach_idea_button(bot)

# ====== הודעת ברוך הבא =======================================================================================================================================================
async def welcam(member):
    channel = bot.get_channel(1397573547395911731)  # ID של חדר ברוכים
    if channel:
        embed = discord.Embed(
            title="🎉 ברוך הבא!",
            description=f"**{member.name}** הצטרף אלינו לשרת!",
            color=0x00ff00
        )
        embed.set_footer(text="אנחנו שמחים לראות אותך כאן!")
        await channel.send(embed=embed)

# ====== הוספת רול למשתמש שנכנס ============================================================================================================================================================
async def verify_role(member):
    role = member.guild.get_role(1397576960468582521)
    if role:
        await member.add_roles(role)
#=============================================================================================================================================================================================        


@bot.event
async def on_member_join(member):
    await welcam(member)
    await verify_role(member)

bot.run(token)

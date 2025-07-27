import discord
from discord.ext import commands
from config import token

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # חובה בשביל on_member_join

bot = commands.Bot(command_prefix="!", intents=intents)

# ====== יצירת כפתור  vrrify אם רול =================================================================================================================================
async def creait_button():
    channel = bot.get_channel(1397573547395911731)
    embed = discord.Embed(
        title="אימות המשתמש",
        description="לאימות המשתמש, לחץ על הכפתור למטה.",
        color=0x00FF00
    )

    button = discord.ui.Button(
        label="אמת אותי",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="verify_button"
    )

    async def callback(interaction: discord.Interaction):
        role_to_add = interaction.guild.get_role(1397574892509200527)   # הרול להוספה
        role_to_remove = interaction.guild.get_role(1397576960468582521)  # הרול להסרה
        if role_to_add:
            await interaction.user.add_roles(role_to_add)
        if role_to_remove and role_to_remove in interaction.user.roles:
            await interaction.user.remove_roles(role_to_remove)
        await interaction.response.send_message("האימות הצליח! רול עודכן.", ephemeral=True)

    button.callback = callback
    view = discord.ui.View()
    view.add_item(button)
    await channel.send(embed=embed, view=view)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
# ====== בדיקת קיום כפתור אימות ================================================================================================================================
async def botton_verify_check():
    channel = bot.get_channel(1397573547395911731)
    button_exists = False
    async for message in channel.history(limit=10):
        for row in message.components:
            for c in row.children:
                if c.custom_id == "verify_button":
                    button_exists = True
                    break
    if not button_exists:
        await creait_button()
#========================================================================================================================================================================        

# ====== פקודת שליחת כפתור =====================================================================================================================================================
@bot.tree.command(name="verify_box", description="שלח הודעת אימות עם כפתור")
async def verify_box(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator and interaction.channel.id == 1397573547395911731:
        await creait_button()
        await interaction.response.send_message("הודעת אימות נשלחה!", ephemeral=True)
    else:
        await interaction.response.send_message("!!אין לך הרשאה או חדר לא מתאים", ephemeral=True)

# ====== on_ready =================================================================================================================================================================
@bot.event
async def on_ready():
    print("הבוט עלה בהצלחה")
    await botton_verify_check()
    await bot.tree.sync()  

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

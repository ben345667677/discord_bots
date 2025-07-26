import discord
from discord.ext import commands
from config import token
intents= discord.Intents.default()#אנפורמצית כניסה מהשרת
intents.message_content = True        #הגדרת גישות

bot = commands.Bot(command_prefix="!", intents=intents)
@bot.event   
async def on_ready():
    print("the bot is conected secsesfuly to the server.")

#פקודה ליצירת כפתור  אימות----button_id="verifi_button"
@bot.tree.command(name="verify_box", description="שלח הודעת אימות עם כפתור")
async def verify_box(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator and interaction.channel.id == 1397573547395911731:
        embed = discord.Embed(
        title="אימות המשתמש",
        description="לאימות המשתמש, לחץ על הכפתור למטה.",
        color=0x00FF00  
        )
        view = discord.ui.View()

        view.add_item(discord.ui.Button(label="אמת אותי", style=discord.ButtonStyle.success, emoji="✅",custom_id="verify_button"))

        await interaction.response.send_message(embed=embed, view=view)
    else :
        if interaction.channel.id != 1397573547395911731:
            await interaction.response.send_message(" !!חדר לא מתאים")
        elif not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(" !!אין לך גישות")     
                
#@bot.event
#async def on_ready():התחלת פונקציית בדיקת כפתור אוטומטית
 #   if 

@bot.event
async def on_message(message):
    if message.content == "!hello":
        await message.channel.send("love you")
bot.run(token)          
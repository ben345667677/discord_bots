import discord
from discord.ext import commands
from config import token

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # חובה בשביל on_member_join

bot = commands.Bot(command_prefix="!", intents=intents)

# ====================================================================================================
# ====== יצירת כפתור אימות (Verify) ==================================================================
# ====================================================================================================

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

# ====================================================================================================
# ====== פקודת Slash לשליחת הודעת אימות ===============================================================
# ====================================================================================================

@bot.tree.command(name="verify_box", description="שלח הודעת אימות עם כפתור")
async def verify_box(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator and interaction.channel.id == 1397573547395911731:
        await create_or_attach_verify_button()
        await interaction.response.send_message("הודעת אימות נשלחה!", ephemeral=True)
    else:
        await interaction.response.send_message("!!אין לך הרשאה או חדר לא מתאים", ephemeral=True)

# ====================================================================================================
# ====== מודאל לשליחת רעיונות (Idea) =================================================================
# ====================================================================================================

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
#====================================================================================================================================================================
# מערכת טיקטים !!!!
# ===============================================================================================================================================================
async def setup_custom_ticket(bot):
    # ===== הגדרות =====
    GUILD_ID = 1396844149520470167        # ID של השרת
    CHANNEL_ID = 1399848018991386704      # ID של הערוץ עם הכפתור
    CATEGORY_ID = 1399846184574783588     # ID של קטגוריית הטיקטים
    ROLE_ID = 1399848536736268338         # ID של רול התמיכה
    LOG_CHANNEL_ID = 1399848398948925540  # ID של חדר הלוגים
    COUNTER_FILE = "ticket_counter.json"

    # ===== פונקציות עזר =====
    def load_counter():
        import json, os
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "r") as f:
                return json.load(f).get("counter", 1)
        return 1

    def save_counter(value):
        import json
        with open(COUNTER_FILE, "w") as f:
            json.dump({"counter": value}, f)

    ticket_counter = load_counter()

    # ===== מחלקות הכפתורים =====
    import discord
    class TicketView(discord.ui.View):
        @discord.ui.button(label="🎫 פתח טיקט", style=discord.ButtonStyle.green)
        async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal ticket_counter
            guild = interaction.guild
            category = guild.get_channel(CATEGORY_ID)

            # Role זמני ייחודי
            temp_role = await guild.create_role(name=f"ticket-{interaction.user.name}", mentionable=False)
            await interaction.user.add_roles(temp_role)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                temp_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.get_role(ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }

            channel_name = f"🎟️│ticket-{ticket_counter}"
            new_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )

            embed = discord.Embed(
                title="🎟️ טיקט חדש נפתח",
                description=f"{interaction.user.mention} פתח טיקט.\n\nנא לתאר את הבעיה שלך כאן.",
                color=0x2ECC71
            )
            await new_channel.send(embed=embed, view=CloseTicketView(interaction.user.id, temp_role.id))

            ticket_counter += 1
            save_counter(ticket_counter)
            await interaction.response.send_message(f"הטיקט שלך נוצר: {new_channel.mention}", ephemeral=True)

    class CloseTicketView(discord.ui.View):
        def __init__(self, opener_id, temp_role_id):
            super().__init__(timeout=None)
            self.opener_id = opener_id
            self.temp_role_id = temp_role_id

        @discord.ui.button(label="🔒 סגור טיקט", style=discord.ButtonStyle.red)
        async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.opener_id and not any(r.id == ROLE_ID for r in interaction.user.roles):
                await interaction.response.send_message("❌ רק פותח הטיקט או בעל הרול יכולים לסגור.", ephemeral=True)
                return
            await interaction.channel.send("בחר סיבה לסגירת הטיקט:", view=FeedbackView(interaction.channel, interaction.user, self.temp_role_id))
            await interaction.response.defer()

    class FeedbackView(discord.ui.View):
        def __init__(self, channel, closer, temp_role_id):
            super().__init__(timeout=None)
            self.channel = channel
            self.closer = closer
            self.temp_role_id = temp_role_id

        async def finalize(self, reason, user):
            log_channel = self.channel.guild.get_channel(LOG_CHANNEL_ID)
            embed = discord.Embed(
                title="📝 לוג סגירת טיקט",
                description=f"**טיקט:** {self.channel.name}\n**סיבה:** {reason}\n**סוגר:** {user.mention}",
                color=0x3498DB
            )
            await log_channel.send(embed=embed)
            temp_role = self.channel.guild.get_role(self.temp_role_id)
            if temp_role:
                await temp_role.delete()
            await self.channel.delete()

        @discord.ui.button(label="🙋‍♂️ פתחתי בטעות", style=discord.ButtonStyle.gray)
        async def reason_mistake(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.finalize("פתח בטעות", interaction.user)

        @discord.ui.button(label="✅ קיבלתי מענה", style=discord.ButtonStyle.green)
        async def reason_answered(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.finalize("קיבל מענה", interaction.user)

        @discord.ui.button(label="🗑️ לא קיבלתי מענה", style=discord.ButtonStyle.red)
        async def reason_trash(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.finalize("לא קיבל מענה", interaction.user)

    # ===== שליחת הודעת הכפתור עם מנגנון חכם =====
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)

    # חיפוש הודעה אחרונה של הבוט
    last_message = None
    async for msg in channel.history(limit=10):
        if msg.author == bot.user:
            last_message = msg
            break

    if last_message:
        # עורך הודעה קיימת
        await last_message.edit(content="לחץ על הכפתור לפתיחת טיקט:", view=TicketView())
    else:
        # יוצר חדשה אם אין
        await channel.send("לחץ על הכפתור לפתיחת טיקט:", view=TicketView())


# ====================================================================================================
# ====== אירוע on_ready ===============================================================================
# ====================================================================================================

@bot.event
async def on_ready():
    print("הבוט עלה בהצלחה")
    await create_or_attach_verify_button(bot)
    await bot.tree.sync()  
    await create_or_attach_idea_button(bot)
    await setup_custom_ticket

# ====================================================================================================
# ====== הודעת ברוך הבא + הוספת רול =================================================================
# ====================================================================================================

# === שליחת הודעת ברוך הבא ===
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

# === הוספת רול ברירת מחדל למשתמש חדש ===
async def verify_role(member):
    role = member.guild.get_role(1397576960468582521)
    if role:
        await member.add_roles(role)

@bot.event
async def on_member_join(member):
    await welcam(member)
    await verify_role(member)

# ====================================================================================================
# ====== הפעלת הבוט ==================================================================================
# ====================================================================================================

bot.run(token)

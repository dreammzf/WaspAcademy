# -*- coding: cp1251 -*-
import discord
from datetime import datetime
import psycopg2
from discord import app_commands

token = 'BOT TOKEN'
server_id = 'DISCORD SERVER ID'
main_channel_id = 'MAIN CHANNEL ID'
voice_channel_id = 'MAIN VOICE CHANNEL ID'
role_5_id = 'ID роли оценки 5'
role_4_id = 'ID роли оценки 4'
role_3_id = 'ID роли оценки 3'
role_2_id = 'ID роли оценки 2'
role_1_id = 'ID роли оценки 1'
role_0_id = 'ID роли оценки 0'

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
isLesson = False
lesson_start_time = str()
lesson_end_time = str()

def db_connect():
    host = "wasp-edu-tg-server.postgres.database.azure.com"
    dbname = "postgres"
    user = "dbadmin"
    password = "hVsx8LVvZpwLf06hgzxf8cxiHE1Bq95U0MmKve07ZUEpWiop"
    try:
        connection = psycopg2.connect(host=host,
                                dbname=dbname,
                                user=user,
                                password=password,
                                sslmode="require")
        connection.autocommit = True
        print(f"Connected to DB \"{dbname}\"")
        return connection
    except:
        print(f"Unable to connect to DB \"{dbname}\"")


try:
    conn = db_connect()
    db = conn.cursor()
except:
    pass


def calculate_attendance_time(member, date):
    db.execute(f"SELECT last_join, last_leave FROM attendance WHERE discordid = {member.id} and date = '{date}';")
    data = db.fetchone()
    if data:
        join_time = datetime.strptime(data[0], '%H:%M:%S')
        leave_time = datetime.strptime(data[1], '%H:%M:%S')
        attendance_time = (leave_time - join_time).seconds
        db.execute(f"SELECT attendance_time FROM attendance WHERE discordid = {member.id} and date = '{date}';")
        data = db.fetchone()
        total_time = attendance_time
        if data[0]:
            total_time += data[0]
        db.execute(f"UPDATE attendance SET attendance_time = '{total_time}' WHERE discordid = {member.id} and date = '{date}';")


@client.event
async def on_voice_state_update(member, before, after):
    if not isLesson:
        return
    date = datetime.now().strftime("%d/%m/%Y")
    time = datetime.now().time().strftime("%H:%M:%S")
    if after.channel and after.channel != before.channel:
       print(f"Ïîëüçîâàòåëü {member.id} çàø¸ë â {after.channel.name} {datetime.now().date()} â {datetime.now().time().replace(microsecond=0)}")
       db.execute(f"UPDATE attendance SET last_join = '{time}', mark = '-' WHERE discordid = {member.id} and date = '{date}';")
    if before.channel and after.channel != before.channel:
       print(f"Ïîëüçîâàòåëü {member.id} âûøåë èç {before.channel.name} {datetime.now().date()} â {datetime.now().time().replace(microsecond=0)}")
       db.execute(f"UPDATE attendance SET last_leave = '{time}' WHERE discordid = {member.id} and date = '{date}';")
       calculate_attendance_time(member, time)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=server_id))
    main_channel = client.get_channel(main_channel_id)
    members = main_channel.members
    for member in members:
        print(member.name)
        print(member.id)
        print(member.joined_at)


@client.event
async def on_member_update(before, after):
    if not isLesson:
        return
    if before.roles != after.roles:
        date = datetime.now().strftime("%d/%m/%Y")
        async for event in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
            if getattr(event.target, "id", None) != before.id:
                continue
            for role in event.after.roles:
                if role.id == role_5_id or role.id == role_4_id or role.id == role_3_id or role.id == role_2_id or role.id == role_1_id or role.id == role_0_id:
                    if role.id == role_0_id:
                        mark = 0
                    if role.id == role_1_id:
                        mark = 1
                    if role.id == role_2_id:
                        mark = 2
                    if role.id == role_3_id:
                        mark = 3
                    if role.id == role_4_id:
                        mark = 4
                    if role.id == role_5_id:
                        mark = 5
                    member = after
                    roles = member.roles
                    role = member.get_role(role.id)
                    roles.remove(role)
                    await member.edit(roles=roles)
                    db.execute(f"SELECT * from attendance WHERE discordid = {member.id} AND date = '{date}' AND mark != '-';")
                    users = db.fetchall()
                    if not users:
                        db.execute(f"SELECT stingers FROM waspusers WHERE discordid = '{member.id}';")
                        stingers_amount = db.fetchone()[0]
                        db.execute(f"UPDATE waspusers SET stingers = {stingers_amount + mark} WHERE discordid = '{member.id}';")
                    db.execute(f"UPDATE attendance SET mark = {mark} WHERE discordid = {member.id} and date = '{date}';")
            break


@tree.command(name="startlesson", description="Íà÷àòü óðîê", guild=discord.Object(id=server_id))
async def start_lesson(interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Íåäîñòàòî÷íî ïðàâ.", ephemeral=True)
        return
    global isLesson, lesson_start_time
    isLesson = True
    date = datetime.now().strftime("%d/%m/%Y")
    time = datetime.now().time().strftime("%H:%M:%S")
    lesson_start_time = datetime.now()
    await interaction.response.send_message("Âû íà÷àëè óðîê.", ephemeral=True)
    db.execute(f"SELECT * FROM attendance WHERE date = '{date}';")
    date_exists = db.fetchall()
    if date_exists:
        return
    db.execute(f"SELECT * FROM waspusers WHERE discordid IS NOT NULL;")
    users = db.fetchall()
    for user in users:
        fullname = f"{user[4]} {user[3]} {user[5]}"
        db.execute(f"INSERT INTO attendance(telegramid, discordid, fullname, date, mark, attendance_time, attendance) VALUES({user[1]}, {user[0]}, '{fullname}', '{date}', 'í', 0, '0%');")
    voice_channel = client.get_channel(voice_channel_id)
    members = voice_channel.members
    for member in members:
        db.execute(f"UPDATE attendance SET last_join = '{time}', mark = '-' WHERE discordid = {member.id} and date = '{date}';")


@tree.command(name="endlesson", description="Çàêîí÷èòü óðîê", guild=discord.Object(id=server_id))
async def end_lesson(interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Íåäîñòàòî÷íî ïðàâ.", ephemeral=True)
        return
    global isLesson, lesson_start_time, lesson_end_time
    if not isLesson:
        return
    isLesson = False
    date = datetime.now().strftime("%d/%m/%Y")
    time = datetime.now().time().strftime("%H:%M:%S")
    lesson_end_time = datetime.now()
    lesson_total_time = (lesson_end_time-lesson_start_time).seconds
    voice_channel = client.get_channel(voice_channel_id)
    members = voice_channel.members
    for member in members:
        db.execute(f"UPDATE attendance SET last_leave = '{time}' WHERE discordid = {member.id} and date = '{date}';")
        calculate_attendance_time(member, date)
    db.execute(f"SELECT date, discordid, attendance_time from attendance")
    users = db.fetchall()
    for user in users:
        try:
            attendance = (user[2]/lesson_total_time)*100
            if attendance > 100:
                attendance = 100
            db.execute(f"UPDATE attendance SET attendance = '{round(attendance)}%' WHERE discordid = {user[1]} and date = '{user[0]}';")
        except:
            pass
    await interaction.response.send_message("Âû çàâåðøèëè óðîê.", ephemeral=True)


@tree.command(name="reg", description="Çàðåãèñòðèðîâàòüñÿ", guild=discord.Object(id=server_id))
async def reg(interaction, ôàìèëèÿ: str, èìÿ: str, îò÷åñòâî: str):
    db.execute(f"SELECT * FROM waspusers WHERE discordid = '{interaction.user.id}'")
    user = db.fetchone()
    if user:
        await interaction.response.send_message("Âû óæå çàðåãèñòðèðîâàíû.", ephemeral=True)
        return
    db.execute(f"SELECT * FROM waspusers WHERE name = '{èìÿ}' AND surname = '{ôàìèëèÿ}' AND lastname = '{îò÷åñòâî}';")
    user = db.fetchone()
    if not user:
        await interaction.response.send_message("\u2757 Ñíà÷àëà çàðåãèñòðèðóéòåñü â áîòå Telegram,\nçàòåì â Discord ñ òåìè æå ÔÈÎ.", ephemeral=True)
        return
    db.execute(f"UPDATE waspusers SET discordid = {interaction.user.id} WHERE name = '{èìÿ}' AND surname = '{ôàìèëèÿ}' AND lastname = '{îò÷åñòâî}';")
    await interaction.response.send_message("\u2705 Óñïåøíàÿ ðåãèñòðàöèÿ.", ephemeral=True)

client.run(token)

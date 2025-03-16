from typing import Optional
from discord import Interaction, ui, Guild, InputTextStyle
import discord
import os
import time
import requests
import json
import random
import string
import datetime
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv(verbose=True)
TOKEN = os.getenv("TOKEN")  # bot token
BOT_ROLE = os.getenv("BOT_ROLE")

intent = discord.Intents()
intent.messages = True # on_messageを実行するために必要な処理。
intent.message_content = True # message.contentのための設定
intent.guilds = True
intent.members = True
intent.reactions = True
intent.message_content = True
client = discord.Bot(intents=intent)

# CTFを選択するためのUI
class Get_CTF_Window(ui.Select):
    def __init__(self, informations):
        options = []
        # The options which can be chosen inside the dropdown
        for i in range(0, 5):
            options.append(discord.SelectOption(label=informations[i][0], value=str(informations[i][1])))

        super().__init__(placeholder="Choose a section", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await set_event(interaction, self.values[0])
        return

# CTFを登録するためのUI        
class Set_CTF_Window(ui.Modal):
    def __init__(self, name, url, password, start, finish):
        super().__init__(title="CTF登録", timeout=None)

        # ctfの名前に年が入っていない場合、category管理めんどいので末尾につける。
        current_year = datetime.now().date().strftime('%Y')
        self.name = ui.InputText(
            label="CTF名",
            style= InputTextStyle.short,
            value= name,
            required=True
        )
        self.url = ui.InputText(
            label="URL",
            style=InputTextStyle.short,
            value=url,
            required=True
        )
        self.password = ui.InputText(
            label="password",
            style=InputTextStyle.short,
            value=password,
            required=True
        )
        self.start = ui.InputText(
            label="開始時刻",
            style=InputTextStyle.short,
            value=start,
            required=True
        )
        self.finish = ui.InputText(
            label="終了時刻",
            style=InputTextStyle.short,
            value=finish,
            required=True
        )
        self.add_item(self.name)
        self.add_item(self.url)
        self.add_item(self.password)
        self.add_item(self.start)
        self.add_item(self.finish)
        
    async def callback(self, interaction):
        guild = interaction.guild

        ctf_name = self.name.value
        url = self.url.value
        password = self.password.value
        start = self.start.value
        finish = self.finish.value

        if discord.utils.get(guild.categories, name=ctf_name):
            await interaction.response.send_message(f"400 Error {ctf_name} is already exists")
            return

        # create category
        bot_role = discord.utils.get(guild.roles, name=BOT_ROLE)
        ctf_category = await guild.create_category(name=ctf_name, overwrites={
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False,
            ),
            bot_role: discord.PermissionOverwrite(
                read_messages=True,
                view_channel=True,
            )
        })

        topic = f"""
        
        CTF: {ctf_name}
        URL: {url}
        password: {password}
        start: {start}
        finish: {finish}
        
        """
        # create text channel and voice channel in ctf_category
        await ctf_category.create_text_channel("info", topic=topic)
        await ctf_category.create_voice_channel('voice')

        await interaction.response.send_message(f"registered {ctf_name}")
        return

# CTFの登録時にパスワード付与
def password_generator():
    length = 16
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# UTC to JST
def utc_to_jst(date):
    # 提供された日時をdatetime objectに変換
    provided_time = datetime.fromisoformat(date.replace('Z', '+00:00'))
  
    # jstに変換
    jst = pytz.timezone("Asia/Tokyo")
    jst_time = provided_time.astimezone(jst)
    
    jst_time_str = jst_time.strftime('%Y-%m-%dT%H:%M:%S%z')

    return jst_time_str

# 動作確認用
@client.event
async def on_ready():
    print("Hello! I am CTF Bot!")

# リアクションが押された時の処理。
# categoryに読み取り権限を与える。
@client.event   
async def on_raw_reaction_add(payload):
    guild = client.get_guild(payload.guild_id)
    text_channel = client.get_channel(payload.channel_id)
    message = await text_channel.fetch_message(payload.message_id)
    user = client.get_user(payload.user_id)

    if message.author.bot:
        # botの出力する内容は、"register ctf-name"なので、"register "を消し去ると、ctf名が取得可能となる
        category_name = message.content.replace("registered ", "")

        category = discord.utils.get(guild.categories, name=category_name)

        if category:
            try:
                # memberにcategoryの読み取り権限を与える。
                member = guild.get_member(user.id)
                await category.set_permissions(member, read_messages=True)
                await message.channel.send(f"{member.name} join {category_name}")

            except Exception as e:
                print(e)
        else:
            channel = message.channel
            await channel.send(f"Error: category not found...")

    return

# /get_event コマンドが走ったときの動作
@client.slash_command(name="get_event", description="get CTF event command")
async def get_event(interaction):
    # get ctf event information 
    timestamp = int(time.time())
    url = f"https://ctftime.org/api/v1/events/?limit=5&start={timestamp}"
    headers = {'User-Agent':'Mozilla/5.0'} # apiを叩いても怒られないように
    response = requests.get(url, headers=headers)
    informations = json.loads(response.text)
    
    # apiの結果から、情報を抽出 
    info_list = []
    for data in informations:

        name = data["title"]
        event_id = data["id"]
        
        info_list.append((name, event_id))
    
    # create view 
    view = ui.View()
    view.add_item(Get_CTF_Window(info_list))
    await interaction.send("select", view=view)

# /set_eventが呼ばれたら処理を開始。
# ctf timesにないCTFでも登録できるようにする。
@client.slash_command(name="set_event", description="set event command")
async def set_event(interaction, event_id=None):
    
    name = ""
    url = ""
    password = password_generator()
    start = ""
    finish = ""
    
    if event_id is not None:
        try:
            # get ctf event information 
            url = f"https://ctftime.org/api/v1/events/{event_id}/"
            headers = {'User-Agent':'Mozilla/5.0'} # apiを叩いても怒られないように
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                await interaction.response.send_message(f"404 Error")
                return
            informations = json.loads(response.text)

            start = utc_to_jst(informations['start'])
            # 2025-01-01 -> 2025
            event_year = start.split("-")[0]

            name = f"{informations['title']} {event_year}" if event_year not in informations['title'] else informations['title']
            url = informations['url']
            password = password_generator()
            finish = utc_to_jst(informations['finish'])
        except Exception as e:
            print(e)
            await interaction.respose.send_message(f"Error")
            return
        
    # create modal window
    window = Set_CTF_Window(name=name, url=url, password=password, start=start, finish=finish)
    await interaction.response.send_modal(modal=window)

client.run(TOKEN)

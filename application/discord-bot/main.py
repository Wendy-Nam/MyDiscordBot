import logging
import discord
from discord import app_commands
from config import DISCORD_BOT_TOKEN, IGNORED_ROLE_IDS
from translate_utils import translate_message, format_multiline_quote
import time

# logger 설정 (벡엔드 실행에서도 디버깅 및 오류 추적을 위한 설정)
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

channel_ids = [] # 번역할 채널 ID를 저장하는 리스트 (메시지 스레드, 일반 채널, 보이스 채널의 채팅란 모두 포함)

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        logger.info(f'봇 로그인 성공: {self.user}')
        await self.tree.sync()

    async def on_message(self, message):
        if message.author == self.user:
            return
        if any(f"<@&{role_id}>" in message.content for role_id in IGNORED_ROLE_IDS):
            return
        # 참고 - V2 버전에서는 !add_channel, !del_channel 등의 텍스트 명령어 기능을 제공하지 않음
        # 대신 Discord 앱 커맨드를 사용하여 더 편리하게 채널을 추가하거나 제거합니다. (/add_channel, /del_channel)
        if message.channel.id in channel_ids or getattr(message, "thread", None):
            start_time = time.perf_counter()
            translated_text = await translate_message(message.content, logger)
            end_time = time.perf_counter()
            logger.info(f"번역 처리 시간: {end_time - start_time:.4f}초")
            if translated_text:
                formatted_text = format_multiline_quote(translated_text)
                if getattr(message, "thread", None):
                    await message.thread.send(formatted_text)
                else:
                    await message.channel.send(formatted_text)
            else:
                await message.channel.send("죄송합니다, 메시지를 번역할 수 없습니다.")

    async def setup_hook(self):
        self.tree.add_command(add_channel)
        self.tree.add_command(del_channel)

@app_commands.command(description="번역할 채널을 추가합니다.")
async def add_channel(interaction: discord.Interaction):
    if interaction.channel_id not in channel_ids:
        channel_ids.append(interaction.channel_id)
        await interaction.response.send_message(f'채널 {interaction.channel.name}이(가) 번역 목록에 추가되었습니다.')
    else:
        await interaction.response.send_message(f'이미 추가된 채널입니다.')

@app_commands.command(description="번역할 채널을 제거합니다.")
async def del_channel(interaction: discord.Interaction):
    if interaction.channel_id in channel_ids:
        channel_ids.remove(interaction.channel_id)
        await interaction.response.send_message(f'채널 {interaction.channel.name}이(가) 번역 목록에서 제거되었습니다.')
    else:
        await interaction.response.send_message(f'이미 제거된 채널입니다.')

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
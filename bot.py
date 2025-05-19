import os
import re
import logging
from dotenv import load_dotenv
import openai
import discord
from discord.ext import commands
from discord import app_commands # app_commands 를 임포트
import langdetect # langdetect 라이브러리 추가

# .env 파일에서 환경 변수 로드
load_dotenv()

# 키와 토큰
discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

# .env에서 번역 무시할 역할 ID 목록을 불러옴 (쉼표로 구분된 문자열) / 예: 다른 봇 ID
ignored_roles_raw = os.getenv("IGNORED_ROLE_IDS", "")
IGNORED_ROLE_IDS = [role_id.strip() for role_id in ignored_roles_raw.split(",") if role_id.strip()]

# 로깅 설정
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# 콘솔 핸들러 추가 (선택 사항)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(console_handler)

# 여러 채널 ID 추가
channel_ids = []

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        logger.info(f'봇 로그인 성공: {self.user}')
        await self.tree.sync()  # 글로벌 커맨드 등록
        logger.info('글로벌 커맨드 동기화 완료')

    async def on_message(self, message):
        if message.author == self.user:
            return

        logger.debug(f'받은 메시지: {message.content}, 보낸 사람: {message.author}, 채널: {message.channel}')

        # 메시지에 무시할 역할이 멘션되었는지 확인
        if any(f"<@&{role_id}>" in message.content for role_id in IGNORED_ROLE_IDS):
            logger.debug(f"무시할 역할 멘션으로 인해 메시지 무시: {message.content}")
            return
        # 봇이 태그되었는지 확인 (v1 버전 명령어 처리)
        if self.user.mentioned_in(message):
            content = message.content.replace(f'<@{self.user.id}>', '').strip()
            if content.startswith('!add_channel'):
                new_channel_id = message.channel.id
                if new_channel_id not in channel_ids:
                    channel_ids.append(new_channel_id)
                    await message.channel.send(f'채널 {message.channel.name}이(가) 번역 목록에 추가되었습니다.')
                    logger.info(f'채널 {message.channel.name}이(가) 번역 목록에 추가됨. 현재 채널 ID 목록: {channel_ids}')
                else:
                    logger.debug(f'채널 {message.channel.name}은(는) 이미 번역 목록에 있습니다.')
            elif content.startswith('!del_channel'):
                del_channel_id = message.channel.id
                if del_channel_id in channel_ids:
                    channel_ids.remove(del_channel_id)
                    await message.channel.send(f'채널 {message.channel.name}이(가) 번역 목록에서 제거되었습니다.')
                    logger.info(f'채널 {message.channel.name}이(가) 번역 목록에서 제거됨. 현재 채널 ID 목록: {channel_ids}')
                else:
                    logger.debug(f'채널 {message.channel.name}은(는) 번역 목록에 없습니다.')
            # 명령어가 포함된 메시지를 번역하지 않도록 함
            return
        
        # 지정된 채널과 스레드에서만 메시지 처리
        if message.channel.id in channel_ids or getattr(message, "thread", None):
            logger.debug(f"번역할 메시지: {message.content}")
            translated_text = await translate_message(message.content)
            logger.debug(f"번역 결과: {translated_text}")

            if translated_text:
                formatted_text = format_multiline_quote(translated_text)
                logger.debug(f"포맷된 메시지: {formatted_text}")
                if formatted_text:
                    if getattr(message, "thread", None):
                        await message.thread.send(formatted_text)
                        logger.info(f"번역된 메시지를 스레드 {message.thread.name}에 전송함")
                    else:
                        await message.channel.send(formatted_text)
                        logger.info(f"번역된 메시지를 채널 {message.channel.name}에 전송함")
                else:
                    logger.warning("포맷된 메시지가 비어 있습니다.")
            else:
                logger.error("번역 실패.")
                await message.channel.send("죄송합니다, 메시지를 번역할 수 없습니다.")
        else:
            logger.debug(f"번역 채널에 해당하지 않아 처리하지 않음: {message.channel.id}")


    async def setup_hook(self):
        # Add the commands to the command tree.
        self.tree.add_command(add_channel)
        self.tree.add_command(del_channel)

# v2 버전 명령어 처리 (슬래시 커맨드 메뉴 지원)
@app_commands.command(description="번역할 채널을 추가합니다.")
async def add_channel(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if channel_id not in channel_ids:
        channel_ids.append(channel_id)
        await interaction.response.send_message(f'채널 {interaction.channel.name}이(가) 번역 목록에 추가되었습니다.')
        logger.info(f'채널 {interaction.channel.name}이(가) 번역 목록에 추가됨. 현재 채널 ID 목록: {channel_ids}')
    else:
        await interaction.response.send_message(f'채널 {interaction.channel.name}은(는) 이미 번역 목록에 있습니다.')

@app_commands.command(description="번역할 채널을 제거합니다.")
async def del_channel(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if channel_id in channel_ids:
        channel_ids.remove(channel_id)
        await interaction.response.send_message(f'채널 {interaction.channel.name}이(가) 번역 목록에서 제거되었습니다.')
        logger.info(f'채널 {interaction.channel.name}이(가) 번역 목록에서 제거됨. 현재 채널 ID 목록: {channel_ids}')
    else:
        await interaction.response.send_message(f'채널 {interaction.channel.name}은(는) 번역 목록에 없습니다.')
        

def format_multiline_quote(text):
    if text is None:
        return "번역 실패 또는 결과 없음."
    lines = text.split('\n')
    formatted_lines = [f"> *{line}*" if line.strip() != "" else "> " for line in lines]
    return '\n'.join(formatted_lines)

def split_text_by_sentence(text, max_length):
    # 문장 단위로 나누기 위해 정규 표현식을 사용
    sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
    sentences = sentence_endings.split(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

async def translate_message(content):
    try:
        # URL 마스킹 처리
        url_pattern = re.compile(r'(https?://\S+)|(www\.\S+)')
        masked_content = re.sub(url_pattern, "[link]", content)

        # 링크만 있는지 확인
        if masked_content.strip() == "[link]" * len(re.findall(url_pattern, content)):
            return "이 메시지는 링크만 포함하고 있어 번역하지 않습니다."

        # 언어 감지
        try:
            source_language = langdetect.detect(masked_content)
            logger.debug(f"감지된 언어: {source_language}")
        except langdetect.LangDetectException:
            logger.warning("언어 감지에 실패하여 기본값(영어)을 사용합니다.")
            source_language = "en"  # 기본 언어 설정

        # 번역할 언어 설정
        target_language = "en" if source_language != "en" else "ko"

        # 문단 단위로 나누기 위해 개행 문자를 기준으로 분리
        paragraphs = masked_content.split('\n\n')
        translated_paragraphs = []

        for paragraph in paragraphs:
            # 문장이 너무 길 경우 청크로 분리
            chunks = split_text_by_sentence(paragraph, max_length=500)
            translated_chunks = []

            for chunk in chunks:
                # 번역할 텍스트와 언어를 명시
                prompt = f"Translate this {source_language} text to {target_language}: {chunk}"

                # GPT-3.5-turbo 사용, 필러 제거 및 간결한 번역 유도
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content":
                        "You are a translation assistant. Translate the content into the specified target language. For Korean translations, use '-요' endings for general conversation. Avoid formal endings like '-다 / -습니다'. Use informal endings or slang for personal thoughts, casual statements, or emotions. Keep the translation concise and clear, avoiding filler language. Preserve bullet points, numbered lists, and formatting."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.07
                )
                translated_chunks.append(response['choices'][0]['message']['content'])

            # 번역된 청크들을 합쳐서 문단으로 결합
            translated_paragraph = ' '.join(translated_chunks)
            translated_paragraphs.append(translated_paragraph)

        # 번역된 문단들을 다시 합침
        translated_text = '\n\n'.join(translated_paragraphs)
        translated_text = translated_text.replace('자산', '작업물')
        logger.info(f'감지 언어 {source_language} ==> 번역 언어 {target_language}')
        return translated_text
    
    except Exception as e:
        logger.error(f'번역 중 오류 발생: {e}')
        return None

# 봇 클라이언트 설정
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(discord_bot_token)

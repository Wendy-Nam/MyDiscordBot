# -*- coding: utf-8 -*-
import discord
import openai
import re

# 키와 토큰
discord_bot_token = 'your_openai_api_key' # 🔐 REQUIRED / Discord 봇 토큰을 여기에 입력하세요.
openai.api_key = 'your_discord_token' # 🔐 REQUIRED / OpenAI API 키를 여기에 입력하세요.
channel_ids = []  # 여러 채널 ID 추가


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Extract mentions from the message
        mentions = message.mentions

        # Check if any of the mentions are other bots
        if any(user.bot for user in mentions):
            return

        # 봇이 태그되었는지 확인
        if self.user.mentioned_in(message):
            # 명령어 처리
            content = message.content.replace(f'<@{self.user.id}>', '').strip()

            # @Lingo 명령어가 포함된 메시지를 무시
            if content.startswith('!add_channel'):
                new_channel_id = message.channel.id
                if new_channel_id not in channel_ids:
                    channel_ids.append(new_channel_id)
                    await message.channel.send(f'Channel {message.channel.name} has been added to the list.')
                    print(f"Current channel IDs: {channel_ids}")

            elif content.startswith('!del_channel'):
                del_channel_id = message.channel.id
                if del_channel_id in channel_ids:
                    channel_ids.remove(del_channel_id)
                    await message.channel.send(f'Channel {message.channel.name} has been removed from the list.')
                    print(f"Current channel IDs: {channel_ids}")

            # 명령어가 포함된 메시지를 번역하지 않도록 함
            return
        
        # 지정된 채널과 스레드에서만 메시지 처리
        if message.channel.id in channel_ids or message.thread:
            translated_text = await translate_message(message.content)
            
            if translated_text:
                formatted_text = format_multiline_quote(translated_text)

                if formatted_text:
                    if message.thread:
                        await message.thread.send(formatted_text)
                    else:
                        await message.channel.send(formatted_text)
            else:
                await message.channel.send("Sorry, I couldn't translate the message.")

def format_multiline_quote(text):
    if text is None:
        return "Translation failed or produced no output."
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
            return "This message only contains links, no translation provided."

        # 메시지 전체에서 언어 감지
        if any(char in masked_content for char in "가나다라마바사아자차카타파하"):
            source_language = "Korean"
            target_language = "English"
        elif any(char in masked_content for char in "абвгґдежзийклмнопрстуфхцчшщьюяіїє"):
            source_language = "Ukrainian"
            target_language = "Korean"
        else:
            source_language = "English"
            target_language = "Korean"

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

        return translated_text
    
    except Exception as e:
        print(f'Error during translation: {e}')
        return None  # 오류 발생 시 None을 반환


# 봇 클라이언트 설정
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(discord_bot_token)

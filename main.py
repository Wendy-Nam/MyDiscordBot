# -*- coding: utf-8 -*-
import discord
import openai
import re

# 키와 토큰
discord_bot_token = 'your_openai_api_key' # 🔐 REQUIRED / Discord 봇 토큰을 여기에 입력하세요.
openai.api_key = 'your_discord_token' # 🔐 REQUIRED / OpenAI API 키를 여기에 입력하세요.
channel_ids = ['None', '1279725258911387680']  # 여러 채널 ID 추가

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        for channel_id in channel_ids:
            channel = client.get_channel(int(channel_id))
            await channel.send('> *Hello, I am a Discord bot helping with real-time translation (KR-EN, UK-EN)!*')

    async def on_message(self, message):
        if message.author == self.user:
            # 봇 자신의 메시지는 처리하지 않음
            return

        # 지정된 채널과 스레드에서만 메시지 처리
        if str(message.channel.id) in channel_ids or message.thread:
            # 메시지를 번역
            translated_text = await translate_message(message.content)
            
            # 인용 블록과 이탤릭체를 줄마다 추가하는 함수
            def format_multiline_quote(text):
                lines = text.split('\n')
                formatted_lines = [f"> *{line}*" if line.strip() != "" else "> " for line in lines]
                return '\n'.join(formatted_lines)

            # 메시지를 줄마다 포맷팅
            formatted_text = format_multiline_quote(translated_text)

            # 번역된 메시지를 해당 채널 또는 스레드에 전송
            if formatted_text:
                if message.thread:  # 메시지가 스레드에서 온 경우
                    await message.thread.send(formatted_text)
                else:  # 일반 채널 메시지인 경우
                    await message.channel.send(formatted_text)

async def translate_message(content):
    try:
        # 사진이나 링크를 마스킹 처리하기 위한 정규식 패턴
        url_pattern = re.compile(r'(https?://\S+)|(www\.\S+)')
        urls = re.findall(url_pattern, content)

        # 링크 마스킹 처리 및 링크 앞뒤 텍스트 분리
        masked_content = re.sub(url_pattern, lambda x: f"[링크]({x.group(0)})", content)

        # 메시지의 언어를 감지하고 번역 방향 설정
        if any(char in masked_content for char in "가나다라마바사아자차카타파하"):
            prompt = f"Translate the following Korean text to English: {masked_content}"
        elif any(char in masked_content for char in "абвгґдежзийклмнопрстуфхцчшщьюяіїє"):
            prompt = f"Translate the following Ukrainian text to Korean: {masked_content}"
        else:
            prompt = f"Translate the following English text to Korean: {masked_content}"

        # GPT-4를 사용하여 번역 수행, 내용 정리와 간결화를 강조
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a translation assistant. Your task is to summarize and translate content from Korean to English, Ukrainian to Korean, or English to Korean. Summarize the main points in the source language, then translate only the summarized content. Do not include the original summarized content in the output. When translating from Korean, omit subjects or objects when they are implied, and use sentence endings like '-음' or '-ㅁ' to keep it concise. In English translations, use noun forms or bullet points to create a report-like feel. Use informal language or slang if appropriate to make the translation more engaging. Focus on clarity, conciseness, and the preservation of core messages and key details."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 번역된 텍스트 반환
        translated_text = response['choices'][0]['message']['content']

        # 특정 단어 치환
        translated_text = translated_text.replace('자산', '작업물')

        return translated_text
    
    except Exception as e:
        print(f'Error during translation: {e}')
        return "Sorry, I couldn't translate the message."

# 봇 클라이언트 설정
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

# 봇 실행
client.run(discord_bot_token)

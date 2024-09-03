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
            
            def format_multiline_quote(text):
                lines = text.split('\n')
                formatted_lines = [f"> *{line}*" if line.strip() != "" else "> " for line in lines]
                return '\n'.join(formatted_lines)

            formatted_text = format_multiline_quote(translated_text)

            if formatted_text:
                if message.thread:
                    await message.thread.send(formatted_text)
                else:
                    await message.channel.send(formatted_text)

async def translate_message(content):
    try:
        url_pattern = re.compile(r'(https?://\S+)|(www\.\S+)')
        urls = re.findall(url_pattern, content)
        masked_content = re.sub(url_pattern, lambda x: f"[link]({x.group(0)})", content)

        # 요약 및 번역 방향 설정
        if any(char in masked_content for char in "가나다라마바사아자차카타파하"):
            prompt = f"Summarize the key points of the following Korean text and translate it to English. Provide only the translated summary: {masked_content}"
        elif any(char in masked_content for char in "абвгґдежзийклмнопрстуфхцчшщьюяіїє"):
            prompt = f"Summarize the key points of the following Ukrainian text and translate it to Korean. Provide only the translated summary: {masked_content}"
        else:
            prompt = f"Summarize the key points of the following English text and translate it to Korean. Provide only the translated summary: {masked_content}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": 
                 "You are a translation assistant. Your primary task is to summarize the key points and then translate the summary. "
                 "Ensure that the summary includes only the most important information, omitting any unnecessary details or conversational fillers. "
                 "The translation should be concise and to the point, focusing solely on the key points of the original text. Do not include the original content or summary in the output."},
                {"role": "user", "content": prompt}
            ]
        )
        
        translated_text = response['choices'][0]['message']['content']
        translated_text = translated_text.replace('자산', '작업물')

        return translated_text
    
    except Exception as e:
        print(f'Error during translation: {e}')
        return "Sorry, I couldn't translate the message."

# 봇 클라이언트 설정
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(discord_bot_token)

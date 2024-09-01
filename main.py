import discord
import openai


discord_bot_token = 'your_openai_api_key' # 🔐 REQUIRED / Discord 봇 토큰을 여기에 입력하세요.
openai.api_key = 'your_discord_token' # 🔐 REQUIRED / OpenAI API 키를 여기에 입력하세요.
channel_id = 'None'

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        channel = client.get_channel(int(channel_id))
        await channel.send('Hello, I am a Discord bot helping with real-time translation (KR-EN, UK-EN)!')

    async def on_message(self, message):
        if message.author == self.user:
            # 봇 자신의 메시지는 처리하지 않음
            return

        # 지정된 채널과 스레드에서만 메시지 처리
        if str(message.channel.id) == channel_id or message.thread:
            # 메시지를 번역
            translated_text = await translate_message(message.content)

            # 번역된 메시지를 해당 채널 또는 스레드에 전송
            if translated_text:
                if message.thread:  # 메시지가 스레드에서 온 경우
                    await message.thread.send(translated_text)
                else:  # 일반 채널 메시지인 경우
                    await message.channel.send(translated_text)

async def translate_message(content):
    try:
        # 입력된 메시지의 언어를 감지하고 그에 따라 번역 방향 설정
        if any(char in content for char in "가나다라마바사아자차카타파하"):
            prompt = f"Translate the following Korean text to English: {content}"
        elif any(char in content for char in "абвгґдежзийклмнопрстуфхцчшщьюяіїє"):
            prompt = f"Translate the following Ukrainian text to Korean: {content}"
        else:
            prompt = f"Translate the following English text to Korean: {content}"

        # GPT-3.5 Turbo를 사용하여 번역 수행
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates Korean to English, English to Korean or Ukrainian to Korean. Use informal language and keep translations short and concise."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 번역된 텍스트 반환
        translated_text = response['choices'][0]['message']['content']
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

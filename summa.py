import discord
import openai
from datetime import datetime, timedelta
import re
import ast  # Python의 ast 모듈을 사용하여 문자열을 안전하게 변환합니다


# Discord 및 OpenAI 설정
DISCORD_TOKEN = None
OPENAI_API_KEY = None
openai.api_key = OPENAI_API_KEY

# 봇이 활동할 채널 ID와 설명을 저장하는 딕셔너리
channel_data = {}

# Lingo 봇의 사용자 ID
LINGO_BOT_ID = "your_bot_id" # 🔐 REQUIRED   # Lingo 봇의 ID를 여기에 입력하세요.

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print(f"My ID: {self.user.id}")

    async def on_message(self, message):
        # 봇이 보낸 메시지 또는 Lingo 봇이 보낸 메시지는 무시
        if message.author == self.user or message.author.id == int(LINGO_BOT_ID):
            return

        print(f"Received message: {message.content}")
        print(f"Message ID : {message.id}")
        print(f"Author ID : {message.author.id}")

        bot_mention = f'<@{self.user.id}>'
        content = message.content.strip()  # 앞뒤 공백 제거
        if content.startswith(bot_mention):
            command_content = content[len(bot_mention):].strip()  # 봇 태그와 명령어 사이의 공백 허용
            print("Processed message content:", command_content)

            # 모든 명령어 처리
            if command_content.startswith('!add_channel'):
                params = command_content.split(' ', 1)
                if len(params) > 1:
                    description = params[1].strip()
                    new_channel_id = message.channel.id
                    if new_channel_id not in channel_data:
                        channel_data[new_channel_id] = {'description': description}
                        await message.channel.send('Channel added.')
                        print(f"Current channel data: {channel_data}")

            elif command_content.startswith('!del_channel'):
                params = command_content.split(' ', 1)
                del_channel_id = message.channel.id
                if del_channel_id in channel_data:
                    del channel_data[del_channel_id]
                    await message.channel.send('Channel deleted.')
                    print(f"Current channel data: {channel_data}")

            elif command_content.startswith('!channel_info'):
                if message.channel.id in channel_data:
                    description = channel_data[message.channel.id]['description']
                    await message.channel.send(f"Channel description:\n{description}")
                else:
                    await message.channel.send("Channel is not registered.")

            elif command_content.startswith('!summarize'):
                params = command_content.split(' ', 1)
                if len(params) > 1:
                    summary_request = params[1].strip()
                    if message.channel.id in channel_data:
                        match = re.match(r"(\d+)(h|d)", summary_request)
                        if match:
                            print(f"Time-based summary request found: {match.groups()}")
                            amount = int(match.group(1))
                            unit = match.group(2)
                            if unit == 'h':
                                time_limit = datetime.utcnow() - timedelta(hours=amount)
                            elif unit == 'd':
                                time_limit = datetime.utcnow() - timedelta(days=amount)

                            text = ""
                            async for msg in message.channel.history(after=time_limit):
                                if not msg.author.bot and msg.content:
                                    text += msg.content + "\n"
                                
                            char_count = len(text)
                            print(f"Collected {len(text.splitlines())} messages ({char_count} characters) for summarization.")
                            await message.channel.send(f"Collecting {len(text.splitlines())} messages ({char_count} characters) for summarization. Please wait...")

                            description = channel_data[message.channel.id]['description']
                            summary = await summarize_text(text, description)
                            await message.channel.send(f"**Summary for the last {amount}{unit}:**\n{summary}")


                        match = re.match(r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", summary_request)
                        if match:
                            print(f"Date range-based summary request found: {match.groups()}")
                            start_date = datetime.strptime(match.group(1), "%Y-%m-%d")
                            end_date = datetime.strptime(match.group(2), "%Y-%m-%d")

                            text = ""
                            async for msg in message.channel.history(after=start_date, before=end_date + timedelta(days=1)):
                                if not msg.author.bot and msg.content:
                                    text += msg.content + "\n"
                                
                            char_count = len(text)
                            print(f"Collected {len(text.splitlines())} messages ({char_count} characters) for summarization.")
                            await message.channel.send(f"Collecting {len(text.splitlines())} messages ({char_count} characters) for summarization. Please wait...")

                            description = channel_data[message.channel.id]['description']
                            summary = await summarize_text(text, description)
                            await message.channel.send(f"**Summary from {start_date.date()} to {end_date.date()}:**\n{summary}")
                            
                
async def summarize_text(text, instructions=""):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant responsible for summarizing discussions. Use Markdown formatting supported by Discord, such as headings (up to h3), bullet points, bold, and italics."
                "Your role is to provide a concise and clear summary of the conversation with the following guidelines:\n\n"
                "- Keep discussions brief and to the point.\n"
                "- Provide specific details for feedback and ideas. Avoid vague or general statements.\n"
                "- For plans and actions, include only the most crucial points. Do not omit important details.\n"
                "- Organize related points or feedback into relevant groups or sections for better readability.\n"
                "- Use Markdown format for the summary, including bullet points and headers to clearly separate different topics.\n\n"
                "Here is the conversation to summarize:\n\n{text}\n\n{instructions}\n\nSummary:"
            )
        },
        {"role": "user", "content": f"Summarize the following conversation with the instructions provided:\n\n{text}\n\n{instructions}\n\nSummary:"}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # 또는 "gpt-4"로 변경할 수 있습니다.
        messages=messages,
        max_tokens=2000,
        temperature=0.5,
    )
    
    summary = response.choices[0].message['content'].strip()
    print(f"Generated summary: {summary}")
    return summary

async def send_large_message(channel, content):
    # Discord의 메시지 길이 제한(2000자)에 맞추기 위해 메시지를 여러 부분으로 나누어 전송합니다.
    max_length = 2000
    for i in range(0, len(content), max_length):
        await channel.send(content[i:i+max_length])

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)


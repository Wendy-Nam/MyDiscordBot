import discord
import openai
from datetime import datetime, timedelta
import re

# Discord 및 OpenAI 설정
DISCORD_TOKEN = None
OPENAI_API_KEY = None
openai.api_key = OPENAI_API_KEY

ignored_user = "LINGO_BOT_USERNAME"  # 무시할 사용자

# 채널 목록 관리 및 추가 지시사항 설정
channel_instructions = {}

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        # # LINGO_BOT_USERNAME 사용자의 메시지를 무시
        # if message.author == self.user or str(message.author) == ignored_user:
        #     print(f"Message from ignored user {ignored_user} ignored.")

        # 봇이 태그되었는지 확인
        if self.user.mentioned_in(message):
            print(f"Bot mentioned in message: {message.content}")
            await asyncio.sleep(1)  # 메시지가 도착하기 전에 잠시 대기
            await self.process_message(message)

    async def process_message(self, message):
        content = message.content.replace(f'<@{self.user.id}>', '').strip()

        # @Summa 명령어가 포함된 메시지 확인
        if content.startswith('!add_channel'):
            print("Processing !add_channel command.")
            new_channel_id = message.channel.id
            params = content.split(" ", 2)
            instruction = params[2] if len(params) > 2 else ""
            channel_instructions[new_channel_id] = instruction
            await message.channel.send(f'Channel {message.channel.name} has been added to the list.\nInstruction: {instruction}')
            print(f"Channel {message.channel.name} added with instruction: {instruction}")
            print(f"Current channel instructions: {channel_instructions}")

        elif content.startswith('!del_channel'):
            print("Processing !del_channel command.")
            del_channel_id = message.channel.id
            if del_channel_id in channel_instructions:
                del channel_instructions[del_channel_id]
                await message.channel.send(f'Channel {message.channel.name} has been removed from the list.')
                print(f"Channel {message.channel.name} removed from tracking.")
                print(f"Current channel instructions: {channel_instructions}")
            else:
                await message.channel.send(f"This channel is not currently being tracked.")
                print(f"Attempted to remove channel {message.channel.name}, but it wasn't being tracked.")

        elif content.startswith('!summarize'):
            print("Processing !summarize command.")
            channel_id = message.channel.id
            if channel_id in channel_instructions:
                # 시간 기반 요약 파라미터 처리
                match = re.match(r"!summarize\s+(\d+)(h|d)", content)
                if match:
                    print(f"Time-based summary request found: {match.groups()}")
                    amount = int(match.group(1))
                    unit = match.group(2)
                    if unit == 'h':
                        time_limit = datetime.utcnow() - timedelta(hours=amount)
                    elif unit == 'd':
                        time_limit = datetime.utcnow() - timedelta(days=amount)

                    # 메시지 수집 및 요약
                    messages = await message.channel.history(after=time_limit).flatten()
                    print(f"Collected {len(messages)} messages for summarization.")
                    text = "\n".join([msg.content for msg in messages if not msg.author.bot and msg.content])
                    summary = await summarize_text(text, channel_instructions[channel_id])
                    await message.channel.send(f"**Summary for the last {amount}{unit}:**\n{summary}")
                    print(f"Summary sent: {summary}")

                # 날짜 범위 기반 요약 파라미터 처리
                match = re.match(r"!summarize\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", content)
                if match:
                    print(f"Date range-based summary request found: {match.groups()}")
                    start_date = datetime.strptime(match.group(1), "%Y-%m-%d")
                    end_date = datetime.strptime(match.group(2), "%Y-%m-%d")

                    # 메시지 수집 및 요약
                    messages = await message.channel.history(after=start_date, before=end_date + timedelta(days=1)).flatten()
                    print(f"Collected {len(messages)} messages for summarization.")
                    text = "\n".join([msg.content for msg in messages if not msg.author.bot and msg.content])
                    summary = await summarize_text(text, channel_instructions[channel_id])
                    await message.channel.send(f"**Summary from {start_date.date()} to {end_date.date()}:**\n{summary}")
                    print(f"Summary sent: {summary}")
                    
async def summarize_text(text, instructions=""):
    prompt = f"Summarize the following conversation with a focus on feedback, revisions, and explanations, and list them as bullet points:\n\n{text}\n\n{instructions}\n\nSummary:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,  # 토큰 수를 1000으로 설정
        n=1,
        stop=None,
        temperature=0.5,
    )
    summary = response['choices'][0]['text'].strip()
    print(f"Generated summary: {summary}")
    return summary

client = MyClient(intents=discord.Intents.default())
client.run(DISCORD_TOKEN)

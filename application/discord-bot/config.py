import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IGNORED_ROLE_IDS = [role_id.strip() for role_id in os.getenv("IGNORED_ROLE_IDS", "").split(",") if role_id.strip()]
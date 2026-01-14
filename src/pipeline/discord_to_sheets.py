import os
import asyncio
import logging
from typing import List

import discord
from discord.ext import commands
from dotenv import load_dotenv

import gspread
from google.oauth2.service_account import Credentials


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

CHANNEL_IDS = [int(x.strip()) for x in os.getenv("CHANNEL_IDS", "").split(",") if x.strip()]
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "200"))

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATE_DIR = os.path.join(BASE_DIR, "state")


def state_path(channel_id: int) -> str:
    return os.path.join(STATE_DIR, f"last_id_{channel_id}.txt")


def get_last_id(channel_id: int) -> int:
    try:
        with open(state_path(channel_id), "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except Exception:
        return 0


def set_last_id(channel_id: int, message_id: int) -> None:
    with open(state_path(channel_id), "w", encoding="utf-8") as f:
        f.write(str(message_id))


def sheets_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=scopes)
    return gspread.authorize(creds)


def ensure_worksheet(sh, title: str):
    try:
        return sh.worksheet(title)
    except Exception:
        ws = sh.add_worksheet(title=title, rows=2000, cols=10)
        ws.append_row(["timestamp", "author", "content", "message_id", "channel_id"])
        return ws


async def append_rows(ws, rows: List[List[str]], retries: int = 6):
    delay = 2
    for attempt in range(1, retries + 1):
        try:
            await asyncio.to_thread(ws.append_rows, rows, value_input_option="USER_ENTERED")
            return
        except Exception as e:
            logging.warning(f"append_rows failed (attempt {attempt}/{retries}): {e}")
            if attempt == retries:
                raise
            await asyncio.sleep(delay)
            delay = min(delay * 2, 60)


async def catch_up_channel(bot: commands.Bot, channel_id: int, ws):
    channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
    last_id = get_last_id(channel_id)

    logging.info(f"Catch-up channel={channel_id} starting from last_id={last_id}")
    rows: List[List[str]] = []
    newest_id = last_id

    after_obj = discord.Object(id=last_id) if last_id else None
    async for msg in channel.history(limit=None, oldest_first=True, after=after_obj):
        ts = msg.created_at.replace(tzinfo=None).isoformat(timespec="seconds")
        rows.append([ts, str(msg.author), msg.content, str(msg.id), str(channel_id)])
        newest_id = msg.id

        if len(rows) >= BATCH_SIZE:
            await append_rows(ws, rows)
            rows.clear()
            set_last_id(channel_id, newest_id)

    if rows:
        await append_rows(ws, rows)
        set_last_id(channel_id, newest_id)

    logging.info(f"Catch-up channel={channel_id} done. last_id={newest_id}")


async def main():
    if not DISCORD_TOKEN or not SPREADSHEET_ID or not CHANNEL_IDS:
        raise SystemExit("Missing config. Please set DISCORD_TOKEN, SPREADSHEET_ID and CHANNEL_IDS in .env")

    gc = sheets_client()
    sh = gc.open_by_key(SPREADSHEET_ID)

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logging.info(f"Logged in as {bot.user}")
        for cid in CHANNEL_IDS:
            ws = ensure_worksheet(sh, f"channel_{cid}")
            await catch_up_channel(bot, cid, ws)
        logging.info("All channels processed. Bot stays online.")

    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())

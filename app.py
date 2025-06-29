import os
import asyncio
import requests
from requests import RequestException
from flask import Flask, request
import discord
from dotenv import load_dotenv
from threading import Thread
from waitress import serve


# --env config--
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!ask ")


# flask api endpoint (render exposes port 10000 as default)
app = Flask(__name__)

@app.get("/ping")
def ping():
    """Simple endpoint used for uptime checks."""
    return "pong"

@app.route("/reply", methods=["POST"])
def reply():
    """
    n8n calls this endpoints with:
    {
        "channel_id": "123456789012345678",
        "content": "message content"
    }
    """
    body = request.json
    channel = client.get_channel(int(body["channel_id"]))
    asyncio.run_coroutine_threadsafe(
        channel.send(body['content']), client.loop
    )
    return '', 204


# discord gateway
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_message(msg: discord.Message):
    if msg.author.bot:
        return # ignore bot messages
    if msg.content.startswith(BOT_PREFIX):
        prompt = msg.content[len(BOT_PREFIX):].strip()
        payload = {
            "prompt": prompt,
            "user_id": str(msg.author.id),
            "user_name": msg.author.name,
            "channel_id": str(msg.channel.id),
            "message_id": str(msg.id)
        }

        # non-blocking HTTP request to n8n webhook
        asyncio.get_event_loop().run_in_executor(
            None, dispatch_payload, payload
        )


def dispatch_payload(payload: dict):
    """Send payload to the configured n8n webhook."""
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
        if response.status_code != 200:
            print(
                f"n8n webhook returned {response.status_code}: "
                f"{response.text}"
            )
        else:
            # successful dispatch logging is helpful for debugging
            print("Dispatched payload to n8n successfully")
    except RequestException as exc:
        print(f"Error sending payload to n8n webhook: {exc}")

# flask + discord on one render app

def run():
    Thread(target=lambda: serve(app, host='0.0.0.0', port=10000)).start()
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    run()

# discord-n8n-relay
Relay service that connects a Discord bot to an n8n webhook.

## Running locally

The application requires Python 3.12+. Install dependencies with:

```bash
pip install -r requirements.txt
```

Create a `.env` file with the following values:

```
DISCORD_TOKEN=<your discord bot token>
N8N_WEBHOOK_URL=<n8n webhook URL>
# Optional, defaults to `!`
BOT_PREFIX=!ask 
```

Start the relay (uses Waitress instead of Flask's development server):

```bash
python app.py
```

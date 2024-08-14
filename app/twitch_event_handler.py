import os
from twitchio.ext import commands
import requests

# Configuration
TWITCH_OAUTH_TOKEN = os.getenv("TWITCH_OAUTH_TOKEN", "your_oauth_token")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL", "your_channel")
BACKEND_URL = "http://127.0.0.1:5000/twitch/event"

# Twitch Bot setup
class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TWITCH_OAUTH_TOKEN,
            prefix='!',
            initial_channels=[TWITCH_CHANNEL]
        )

    async def event_ready(self):
        print(f'Bot is ready | Logged in as: {self.nick}')

    async def event_message(self, message):
        # Print all incoming messages to the console
        print(message.content)
        await self.handle_commands(message)

    @commands.command(name='fight')
    async def fight(self, ctx):
        # Process the fight command
        user_id = ctx.author.id
        username = ctx.author.name

        # Send a POST request to your backend to handle the fight logic
        response = requests.post(
            BACKEND_URL,
            json={
                "event_type": "chat_command",
                "command": "fight",
                "user_id": user_id,
                "username": username
            }
        )

        # Check if the response was successful
        if response.status_code == 200:
            result = response.json().get("result", "Fight processed.")
            await ctx.send(result)
        else:
            await ctx.send("There was an error processing the fight.")

if __name__ == '__main__':
    bot = Bot()
    bot.run()


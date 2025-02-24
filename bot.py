from twitchio.ext import commands
import os
from dotenv import load_dotenv
import requests
from gamble import LeagueBetting
import asyncio

load_dotenv()

class StreamBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.environ['TWITCH_ACCESS_TOKEN'],
            client_id=os.environ['TWITCH_CLIENT_ID'],
            client_secret=os.environ['TWITCH_CLIENT_SECRET'],
            prefix='!',
            initial_channels=[os.environ['TWITCH_CHANNEL']]
        )
        self.server_url = "http://localhost:5000"
        self.league_betting = LeagueBetting()
        self.betting_task = None

    async def event_ready(self):
        """Called once when the bot goes online."""
        print(f"Bot is ready! | {self.nick}")
        # Start monitoring League games
        self.betting_task = asyncio.create_task(self.monitor_games())

    async def monitor_games(self):
        """Monitor for new League games and handle betting"""
        while True:
            try:
                is_new_game = await self.league_betting.check_current_game()
                if is_new_game:
                    channel = self.get_channel(os.environ['TWITCH_CHANNEL'])
                    await channel.send("📢 New game detected! Use !bet [amount] [win/loss] to place your bets!")
            except Exception as e:
                print(f"Error monitoring games: {e}")
            await asyncio.sleep(60)  # Check every minute

    @commands.command(name="bet")
    async def bet_command(self, ctx, amount: int, prediction: str):
        """Place a bet on the current game"""
        if prediction.lower() not in ['win', 'loss']:
            await ctx.send("❌ Prediction must be 'win' or 'loss'")
            return
            
        result = self.league_betting.place_bet(str(ctx.author.id), amount, prediction)
        await ctx.send(f"@{ctx.author.name} {result}")

    @commands.command(name="points")
    async def points_command(self, ctx):
        """Check your points"""
        points = self.league_betting.get_points(str(ctx.author.id))
        await ctx.send(f"@{ctx.author.name} has {points} points! 💰")

    @commands.command(name="queue")
    async def queue_song(self, ctx, *, song_name: str):
        """Queue a song when someone uses !queue command"""
        try:
            response = requests.post(
                f"{self.server_url}/queue-song",
                json={"song_name": song_name}
            )
            
            if response.status_code == 200:
                await ctx.send(f"Successfully queued: {response.json().get('track', song_name)}")
            else:
                await ctx.send(f"Failed to queue song. Error: {response.json().get('message', 'Unknown error')}")
                
        except requests.RequestException as e:
            await ctx.send("Sorry, couldn't connect to the music server!")
            print(f"Error queueing song: {e}")

def run_bot():
    bot = StreamBot()
    bot.run()

if __name__ == "__main__":
    run_bot()
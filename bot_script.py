from twitchio.ext import commands
from app.game_logic import Bot, register_player, choose_class  # Import necessary functions

# Initialize your game logic bot
game_bot = Bot()

# Start gold accumulation
game_bot.start_gold_accumulation()

# Initialize the Twitch bot
bot = commands.Bot(
    token='TOKEN',
    client_id='CLIENT_ID',
    nick='streamer-rpg-bot',
    prefix='!',
    initial_channels=['TWITCH_USERNAME_HERE']
)

@bot.event
async def event_ready():
    print(f'Ready | {bot.nick} is connected to Twitch')

@bot.event
async def event_message(ctx):
    # Ignore messages from the bot itself to prevent loops
    if ctx.author.name.lower() == bot.nick.lower():
        return

    await bot.handle_commands(ctx)

@bot.command(name='register')
async def register(ctx):
    result = register_player(ctx.author.id, ctx.author.name)
    await ctx.send(f'{ctx.author.name}, {result}')

@bot.command(name='chooseclass')
async def choose_class_command(ctx):
    args = ctx.message.content.split()  # Correctly access the message content
    if len(args) < 2:
        await ctx.send(f"{ctx.author.name}, you need to specify a class name. Example: !chooseclass Warrior")
        return

    class_name = args[1]
    result = choose_class(ctx.author.id, class_name)
    await ctx.send(f"{ctx.author.name}, {result}")

@bot.command(name='help')
async def help_command(ctx):
    help_text = """
Available commands:
!register - Register as a player in the game.
!chooseclass <ClassName> - Choose your class (e.g., Warrior, Mage, Archer).
!attack - Attack the boss if it's spawned.
!spawnmob - Spawn a high-level mob if the streamer is live.
"""
    await ctx.send(help_text)

@bot.command(name='gold')
async def gold_command(ctx):
    gold_amount = game_bot.get_gold(ctx.author.id)  # Use game_bot to call get_gold
    await ctx.send(f"{ctx.author.name}, you have {gold_amount} gold.")

@bot.command(name='attack')
async def attack(ctx):
    result = game_bot.fight_boss(ctx.author.id, 50)  # Use the game_bot instance to call fight_boss
    await ctx.send(f'{ctx.author.name}, {result}')

@bot.command(name='buybuff')
async def buybuff_command(ctx):
    args = ctx.message.content.split()  # Correctly access the message content
    if len(args) < 2:
        await ctx.send(f"{ctx.author.name}, you need to specify a buff name. Example: !buybuff health_boost")
        return

    buff_name = args[1]
    result = game_bot.buy_buff(ctx.author.id, buff_name)
    await ctx.send(f"{ctx.author.name}, {result}")

if __name__ == "__main__":
    bot.run()


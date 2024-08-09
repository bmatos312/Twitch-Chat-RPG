import logging
from sqlalchemy.exc import SQLAlchemyError
from twitchio.ext import commands
from models import Player, PlayerClass
from app import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cooldown Dictionary
fight_cooldowns= {}

# Twitch Bot setup
class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token='YOUR_TWITCH_OAUTH_TOKEN',
            prefix='!',
            initial_channels=['YOUR_CHANNEL']
        )

    async def event_ready(self):
        logger.info(f'Ready | {self.nick}')

    async def event_message(self, message):
        logger.info(message.content)
        await self.handle_commands(message)

    @commands.comman(name='fight')
    async def fight(self, ctx, *, mob_name: str = 'sand serpent'):
	user_id = ctx.author.id
	if user_id in fight_cooldowns and (asyncio.get_event_loop().time() - fight_cooldowns[user_id] < 300):
	    await ctx.send("You must wait 5 minutes before fighting again.")
	    return

	if mob_name.lower() != 'sand serpent':
	    await ctx.send("You can only fight 'Sand Serpent' currently.")
	    return

	result = await start_fight(user_id, mob_name)
	await ctx.send(result)
	fight_cooldowns[user_id] = asyncio.get_event_loop().time()

async def start_fight(user_id, mob_name):
	player = Player.query.filter_by(twitch_id=user_id).first()
	mob = Mob.query.filter_by(name=mob_name).first()
	if not player or not mob:
	    return "Error: Player or mob not found."

	from random import choice
	winner =  choice([player.username, mob.name])
	return f"The fight is over. The winner is {winner}!"


    @commands.command(name='chooseclass')
    async def choose_class(self, ctx, class_choice: str):
        if class_choice.lower() not in ['warrior', 'mage', 'archer']:
            await ctx.send('Invalid class. Choose from Warrior, Mage, or Archer.')
            return
        user_id = ctx.author.id
        success = update_player_class(user_id, class_choice.capitalize())
        if success:
            await ctx.send(f'{ctx.author.name}, you have successfully chosen {class_choice.capitalize()} as your class!')
        else:
            await ctx.send('There was a problem setting your class. Please try again.')

def update_player_class(user_id, class_name):
    try:
        player = Player.query.filter_by(twitch_id=user_id).first()
        player_class = PlayerClass.query.filter_by(name=class_name).first()
        if not player or not player_class:
            logger.error('Player or class not found')
            return False
        player.class_id = player_class.id
        db.session.commit()
        logger.info(f'Updated player {player.username} to class {class_name}')
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f'Database error when updating player class: {e}', exc_info=True)
        return False
    except Exception as e:
        logger.error(f'Unexpected error when updating player class: {e}', exc_info=True)
        return False

if __name__ == '__main__':
    bot = Bot()
    bot.run()


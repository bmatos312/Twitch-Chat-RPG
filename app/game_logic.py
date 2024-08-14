# game_logic.py

import logging
from sqlalchemy.exc import SQLAlchemyError
from twitchio.ext import commands
from app.models import Player, PlayerClass  # Import models directly from models.py
from app.extensions import db  # Import db from extensions instead of app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Function to update player class in the database
def update_player_class(user_id, class_name):
    try:
        player = Player.query.filter_by(twitch_id=user_id).first()  # Assuming twitch_id is stored
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


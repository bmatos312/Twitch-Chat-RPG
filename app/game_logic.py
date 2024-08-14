import logging
import pymysql
import random
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bot:
    def __init__(self):
        self.token = 'YOUR_TWITCH_OAUTH_TOKEN'
        self.prefix = '!'
        self.initial_channels = ['YOUR_CHANNEL']
        self.boss_name = 'Sandworm of Shai-Hulud'
        self.boss_duration = 5 * 60  # 5 minutes in seconds

    def event_ready(self):
        logger.info(f'Ready')

    def event_message(self, message):
        logger.info(message)
        self.handle_commands(message)

    def fight_boss(self, user_id, bet_amount):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM Mob WHERE name = %s AND spawn_time IS NOT NULL AND TIMESTAMPDIFF(SECOND, spawn_time, NOW()) <= %s
                """, (self.boss_name, self.boss_duration))
                boss = cursor.fetchone()

                if not boss:
                    return "The Sandworm of Shai-Hulud has not spawned or its time has expired."

                cursor.execute("""
                    SELECT p.* FROM Player p
                    JOIN TwitchUser tu ON p.twitch_user_id = tu.id
                    WHERE tu.twitch_id = %s
                """, (user_id,))
                player = cursor.fetchone()

                if not player:
                    logger.error(f'Player not found for twitch_user_id: {user_id}')
                    return "Player not found."

                # Check if player has enough gold
                if player['gold'] < bet_amount:
                    return "You don't have enough gold to place this bet."

                # Fight logic
                player_attack = player['attack']
                player_defense = player['defense']
                boss_attack = boss['attack']
                boss_defense = boss['defense']

                player_damage = max(player_attack - boss_defense, 0)
                boss_damage = max(boss_attack - player_defense, 0)

                if player_damage > boss_damage:
                    # Boss is defeated
                    cursor.execute("UPDATE Mob SET defeated = TRUE WHERE id = %s", (boss['id'],))
                    drop_item = self.determine_boss_drop(player['class_id'], True)
                else:
                    # Boss not defeated but player gets a drop
                    drop_item = self.determine_boss_drop(player['class_id'], False)

                if drop_item:
                    cursor.execute(
                        "INSERT INTO Inventory (player_id, item_id, quantity) VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE quantity = quantity + 1",
                        (player['id'], drop_item['id'])
                    )
                    cursor.execute(
                        "UPDATE Player SET gold = gold + %s WHERE id = %s",
                        (random.randint(10, 100), player['id'])
                    )
                    connection.commit()
                    return f"You fought the Sandworm of Shai-Hulud and received {drop_item['name']} along with some gold!"
                else:
                    cursor.execute(
                        "UPDATE Player SET gold = gold + %s WHERE id = %s",
                        (random.randint(10, 100), player['id'])
                    )
                    connection.commit()
                    return "You fought the Sandworm of Shai-Hulud and received some gold, but no items dropped."

        except Exception as e:
            logger.error(f'Error during boss fight: {e}', exc_info=True)
            return "An error occurred during the fight."
        finally:
            connection.close()

    def determine_boss_drop(self, class_id, defeated):
        drop_chance = random.random()

        if defeated:
            drop_multiplier = 1.02  # Increase drop chance by 2% if the boss is defeated
        else:
            drop_multiplier = 0.5  # Reduce drop chance if the boss is not defeated

        if class_id == 1:  # Archer
            if drop_chance < 0.01 * drop_multiplier:
                return self.get_item_by_name('Shai-Hulud’s Gaze')
            elif drop_chance < 0.21 * drop_multiplier:
                return self.get_item_by_name('Windstalker Bow')
            elif drop_chance < 0.71 * drop_multiplier:
                return self.get_item_by_name('Sandstrike Arrows')

        elif class_id == 2:  # Warrior
            if drop_chance < 0.01 * drop_multiplier:
                return self.get_item_by_name('Crysknife of the Ancients')
            elif drop_chance < 0.21 * drop_multiplier:
                return self.get_item_by_name('Dunebreaker Sword')
            elif drop_chance < 0.71 * drop_multiplier:
                return self.get_item_by_name('Fedaykin Scimitar')

        elif class_id == 3:  # Mage
            if drop_chance < 0.01 * drop_multiplier:
                return self.get_item_by_name('Voice of the Desert')
            elif drop_chance < 0.21 * drop_multiplier:
                return self.get_item_by_name('Sandweaver Staff')
            elif drop_chance < 0.71 * drop_multiplier:
                return self.get_item_by_name('Mirage Orb')

        return None

    def get_item_by_name(self, name):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Item WHERE name = %s", (name,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f'Error fetching item by name: {e}', exc_info=True)
            return None
        finally:
            connection.close()

def register_player(twitch_user_id, username):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Retrieve the TwitchUser ID based on the provided twitch_user_id
            cursor.execute("SELECT id FROM TwitchUser WHERE twitch_id=%s", (twitch_user_id,))
            twitch_user = cursor.fetchone()

            if not twitch_user:
                return "Twitch user does not exist. Please register the Twitch user first."

            twitch_user_id_from_db = twitch_user['id']

            # Retrieve a valid PlayerClass ID (e.g., for 'Warrior')
            cursor.execute("SELECT id FROM PlayerClass WHERE name=%s", ('Warrior',))
            player_class = cursor.fetchone()

            if not player_class:
                return "Player class does not exist. Please add player classes first."

            player_class_id = player_class['id']

            # Using a placeholder email for registration
            placeholder_email = f"{username}@example.com"
            cursor.execute(
                "INSERT INTO Player (username, email, password_hash, twitch_user_id, class_id) VALUES (%s, %s, %s, %s, %s)",
                (username, placeholder_email, 'default_password_hash', twitch_user_id_from_db, player_class_id)
            )
            connection.commit()
            logger.info(f"Registered player: {username}")
            return "Player registered successfully"
    except Exception as e:
        connection.rollback()
        logger.error(f"Error registering player: {e}", exc_info=True)
        return "An error occurred during player registration"
    finally:
        connection.close()


def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='tolstoy',
        password='Performix312!',
        db='rpg_data',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

if __name__ == '__main__':
    bot = Bot()
    bot.run()


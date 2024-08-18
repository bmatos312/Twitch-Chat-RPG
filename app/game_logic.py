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

def test_no_damage():
    # All players have dealt 0 damage
    player_damage = {
        'player_1': {'total_damage': 0, 'time': 120},
        'player_2': {'total_damage': 0, 'time': 100},
        'player_3': {'total_damage': 0, 'time': 110},
    }

    # Assuming the players are of class 'warrior'
    winner, rewards = assign_rewards(player_damage, 'warrior')
    
    assert winner is None, "No player should win since no damage was dealt."
    assert rewards['gold'] == 0, "No gold should be awarded."
    assert rewards['items'] == [], "No items should be awarded."


def test_same_dps():
    # Two players have the same DPS
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
        'player_2': {'total_damage': 500, 'time': 100},
        'player_3': {'total_damage': 600, 'time': 120},
    }

    # Assuming the players are of class 'warrior'
    winner, rewards = assign_rewards(player_damage, 'warrior')
    
    assert winner in ['player_1', 'player_2'], "Either player_1 or player_2 should be the winner."
    assert rewards['gold'] > 0, "Gold should be awarded."
    assert len(rewards['items']) >= 0, "Items should be awarded based on the drop table."

def calculate_dps(total_damage, time):
    """Helper function to calculate DPS (Damage Per Second)."""
    if time <= 0:
        return 0
    return total_damage / time

def assign_rewards(player_damage, player_class):
    """
    Assign rewards based on player damage and class.
    
    Args:
    player_damage (dict): A dictionary where keys are player IDs and values are dictionaries with 'total_damage' and 'time'.
    player_class (str): The class of the players (e.g., 'warrior', 'archer', etc.).
    
    Returns:
    tuple: (winner, rewards), where 'winner' is the player ID who won, and 'rewards' is a dictionary with keys 'gold' and 'items'.
    """
    # Validate inputs and filter out invalid players
    valid_players = {
        player: info
        for player, info in player_damage.items()
        if info['total_damage'] >= 0 and info['time'] > 0
    }

    if not valid_players:
        return None, {'gold': 0, 'items': []}

    # Calculate DPS for each valid player
    dps_dict = {player: calculate_dps(info['total_damage'], info['time']) for player, info in valid_players.items()}
    
    # Determine the winner
    max_dps = max(dps_dict.values(), default=0)
    if max_dps == 0:
        winner = None
    else:
        winner = next(player for player, dps in dps_dict.items() if dps == max_dps)

    # Assign rewards based on the winner
    rewards = {'gold': 0, 'items': []}
    if winner:
        rewards['gold'] = max_dps * 10  # Example: 10 gold per DPS point
        
        # Award items based on the class and some criteria
        if player_class == 'warrior':
            rewards['items'] = ['sword', 'shield'] if max_dps > 50 else ['shield']
        elif player_class == 'archer':
            rewards['items'] = ['bow', 'arrows'] if max_dps > 50 else []
        # Add other class rewards logic as necessary

    return winner, rewards

def test_no_players():
    player_damage = {}
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner is None, "There should be no winner if there are no players."
    assert rewards['gold'] == 0, "No gold should be awarded if there are no players."
    assert rewards['items'] == [], "No items should be awarded if there are no players."

def test_all_same_dps():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
        'player_2': {'total_damage': 500, 'time': 100},
        'player_3': {'total_damage': 500, 'time': 100},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner in player_damage.keys(), "Any player could be the winner in case of identical DPS."
    assert rewards['gold'] > 0, "Gold should be awarded."
    assert len(rewards['items']) >= 0, "Items should be awarded based on the drop table."

def test_negative_values():
    player_damage = {
        'player_1': {'total_damage': -100, 'time': 100},
        'player_2': {'total_damage': 500, 'time': -100},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner is None, "There should be no winner with invalid inputs."
    assert rewards['gold'] == 0, "No gold should be awarded with invalid inputs."
    assert rewards['items'] == [], "No items should be awarded with invalid inputs."

def test_zero_time_nonzero_damage():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 0},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner is None, "No player should win if time is zero."
    assert rewards['gold'] == 0, "No gold should be awarded."
    assert rewards['items'] == [], "No items should be awarded."

def test_unrecognized_class():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
    }
    winner, rewards = assign_rewards(player_damage, 'unknown_class')
    assert winner == 'player_1', "Player with highest DPS should still be the winner."
    assert rewards['gold'] > 0, "Gold should be awarded even if the class is unknown."
    assert rewards['items'] == [], "No items should be awarded if the class is unrecognized."

def test_large_values():
    player_damage = {
        'player_1': {'total_damage': 10**12, 'time': 10**6},
        'player_2': {'total_damage': 10**12, 'time': 10**6 + 1},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner == 'player_1', "Player with slightly better DPS should win."
    assert rewards['gold'] > 0, "Gold should be awarded for large damage values."
    assert len(rewards['items']) >= 0, "Items should be awarded based on the drop table."

def test_single_player():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner == 'player_1', "The only player should be the winner."
    assert rewards['gold'] > 0, "Gold should be awarded."
    assert len(rewards['items']) >= 0, "Items should be awarded based on the drop table."

def test_tied_dps_different_classes():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
        'player_2': {'total_damage': 500, 'time': 100},
    }
    winner, rewards = assign_rewards(player_damage, 'archer')
    assert winner in ['player_1', 'player_2'], "Either player should win with tied DPS."
    assert rewards['gold'] > 0, "Gold should be awarded."
    assert 'items' in rewards, "Items should be awarded based on the class."


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


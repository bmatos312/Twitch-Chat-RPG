import logging
import pymysql
import random
import datetime
import time
import schedule
import threading

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
        self.gold_accumulation_interval = 60  # Interval in seconds for gold accumulation

    def start_gold_accumulation(self):
        """Start a thread to accumulate gold for players based on their level."""
        def accumulate_gold():
            while True:
                try:
                    connection = get_db_connection()
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE Player SET gold = gold + level")
                        connection.commit()
                        logger.info("Gold accumulated for all players based on their level")
                except Exception as e:
                    logger.error(f"Error during gold accumulation: {e}", exc_info=True)
                finally:
                    connection.close()
                time.sleep(self.gold_accumulation_interval)

        # Start the gold accumulation in a separate thread
        threading.Thread(target=accumulate_gold, daemon=True).start()

    def get_gold(self, twitch_user_id):
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                # Retrieve the player's gold balance
                cursor.execute("""
                    SELECT p.gold FROM Player p
                    JOIN TwitchUser tu ON p.twitch_user_id = tu.id
                    WHERE tu.twitch_id = %s
                """, (twitch_user_id,))
                player = cursor.fetchone()

                if not player:
                    return "Player not found. Please register first."

                return player['gold']
        except Exception as e:
            logger.error(f"Error retrieving gold balance: {e}", exc_info=True)
            return "An error occurred while checking your gold balance."
        finally:
            connection.close()

    def buy_buff(self, twitch_user_id, buff_name):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Get the player's gold
            cursor.execute("""
                SELECT p.id, p.gold FROM Player p
                JOIN TwitchUser tu ON p.twitch_user_id = tu.id
                WHERE tu.twitch_id = %s
            """, (twitch_user_id,))
            player = cursor.fetchone()

            if not player:
                return "Player not found. Please register first."

            player_id = player['id']
            player_gold = player['gold']

            # Define the buffs and their costs
            buffs = {
                "health_boost": {"cost": 50, "description": "Increase your health by 50%"},
                "dps_boost": {"cost": 75, "description": "Increase your DPS by 20%"},
                "steal_gold": {"cost": 100, "description": "Roll a chance to steal gold from another player"},
            }

            if buff_name not in buffs:
                return f"Invalid buff name. Available buffs are: {', '.join(buffs.keys())}"

            buff = buffs[buff_name]
            if player_gold < buff['cost']:
                return f"You don't have enough gold to buy {buff_name}. It costs {buff['cost']} gold."

            # Deduct the cost of the buff from the player's gold
            cursor.execute("UPDATE Player SET gold = gold - %s WHERE id = %s", (buff['cost'], player_id))
            connection.commit()

            # Apply the buff effect
            if buff_name == "health_boost":
                cursor.execute("UPDATE Player SET health = health * 1.5 WHERE id = %s", (player_id,))
                connection.commit()
                return "Your health has been increased by 50%."

            elif buff_name == "dps_boost":
                cursor.execute("UPDATE Player SET dps = dps * 1.2 WHERE id = %s", (player_id,))
                connection.commit()
                return "Your DPS has been increased by 20%."

            elif buff_name == "steal_gold":
                # Get a random target player
                cursor.execute("""
                    SELECT id, gold FROM Player WHERE id != %s ORDER BY RAND() LIMIT 1
                """, (player_id,))
                target = cursor.fetchone()

                if not target:
                    return "No other players to steal from."

                target_gold = target['gold']
                stolen_percentage = random.randint(1, 25) / 100.0
                stolen_amount = int(target_gold * stolen_percentage)

                # Steal gold from the target player
                cursor.execute("UPDATE Player SET gold = gold - %s WHERE id = %s", (stolen_amount, target['id']))
                cursor.execute("UPDATE Player SET gold = gold + %s WHERE id = %s", (stolen_amount, player_id))
                connection.commit()

                return f"You stole {stolen_amount} gold from another player!"
    except Exception as e:
        connection.rollback()
        logger.error(f"Error buying buff: {e}", exc_info=True)
        return "An error occurred while buying the buff."
    finally:
        connection.close()

def register_player(twitch_user_id, username):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Check if the user is already registered
            cursor.execute("SELECT id FROM Player WHERE twitch_user_id=(SELECT id FROM TwitchUser WHERE twitch_id=%s)", (twitch_user_id,))
            player = cursor.fetchone()

            if player:
                return "You are already registered."

            # Register the user without a class
            cursor.execute("SELECT id FROM TwitchUser WHERE twitch_id=%s", (twitch_user_id,))
            twitch_user = cursor.fetchone()

            if not twitch_user:
                return "Twitch user does not exist. Please register the Twitch user first."

            twitch_user_id_from_db = twitch_user['id']
            placeholder_email = f"{username}@example.com"

            cursor.execute(
                "INSERT INTO Player (username, email, password_hash, twitch_user_id) VALUES (%s, %s, %s, %s)",
                (username, placeholder_email, 'default_password_hash', twitch_user_id_from_db)
            )
            connection.commit()
            return "Registered successfully! Please select your class using !chooseclass <ClassName>."
    except Exception as e:
        connection.rollback()
        logger.error(f"Error registering player: {e}", exc_info=True)
        return "An error occurred during registration."
    finally:
        connection.close()

def choose_class(twitch_user_id, class_name):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Check if the player exists
            cursor.execute("""
                SELECT id FROM Player WHERE twitch_user_id=(SELECT id FROM TwitchUser WHERE twitch_id=%s)
            """, (twitch_user_id,))
            player = cursor.fetchone()

            if not player:
                return "Player not found. Please register first."

            # Check if the class exists
            cursor.execute("SELECT id FROM PlayerClass WHERE name=%s", (class_name,))
            player_class = cursor.fetchone()

            if not player_class:
                return "Invalid class name. Please choose a valid class."

            # Update the player's class
            cursor.execute("UPDATE Player SET class_id=%s WHERE id=%s", (player_class['id'], player['id']))
            connection.commit()

            return f"Class changed to {class_name} successfully!"
    except Exception as e:
        connection.rollback()
        logger.error(f"Error changing class: {e}", exc_info=True)
        return "An error occurred while changing class."
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

def calculate_xp(monster, is_event_monster=False):
    base_xp = monster['xp_value']
    if is_event_monster:
        return base_xp * 2  # Double XP for event monsters
    return base_xp

def award_xp(player, monster, is_event_monster=False):
    xp_earned = calculate_xp(monster, is_event_monster)
    player['xp'] += xp_earned
    player['level'], player['xp'], leveled_up = calculate_level(player['level'], player['xp'])
    if leveled_up:
        apply_stat_increases(player)
        give_level_up_rewards(player)
    return xp_earned

def scale_mob(mob, player_level):
    mob['health'] += player_level * mob['health_scaling']
    mob['attack'] += player_level * mob['attack_scaling']
    mob['defense'] += player_level * mob['defense_scaling']
    return mob

def is_streamer_live(client_id, client_secret, streamer_id):
    # Get an OAuth token
    token_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    token_response = requests.post(token_url, params=params)
    access_token = token_response.json().get("access_token")
    
    # Check stream status
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    stream_url = f"https://api.twitch.tv/helix/streams?user_id={streamer_id}"
    stream_response = requests.get(stream_url, headers=headers)
    data = stream_response.json()
    
    if data.get('data') and len(data['data']) > 0:
        return True  # Streamer is live
    else:
        return False  # Streamer is not live
def spawn_high_level_mob():
    high_level_mobs = ["Sandworm of Shai-Hulud", "Paul Atreides", "Baron Harkonnen"]
    chosen_mob = random.choice(high_level_mobs)
    print(f"A {chosen_mob} has spawned!")

def check_and_spawn_mob():
    if is_streamer_live(client_id, client_secret, streamer_id):
        spawn_high_level_mob()
    else:
        print("Streamer is not live. No mob spawned.")

    # Schedule the mob spawn twice a day at specific times (e.g., 1 PM and 7 PM)
    schedule.every().day.at("13:00").do(check_and_spawn_mob)
    schedule.every().day.at("19:00").do(check_and_spawn_mob)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def notify_players(mob_name):
    message = f"A wild {mob_name} has appeared! Prepare for battle!"
    # Send this message to Twitch chat or display it in the game
    print(message)  # Example placeholder

def spawn_high_level_mob():
    high_level_mobs = ["Sandworm of Shai-Hulud", "Paul Atreides", "Baron Harkonnen"]
    chosen_mob = random.choice(high_level_mobs)
    notify_players(chosen_mob)
    print(f"A {chosen_mob} has spawned!")

def update_mob_spawn_in_db(mob_name):
    # Example of how you might update your database
    # Assuming you have a 'Mob' table and an 'active' field to indicate active mobs
    cursor.execute("UPDATE Mob SET active = 1 WHERE name = %s", (mob_name,))
    db.commit()

def spawn_high_level_mob():
    high_level_mobs = ["Sandworm of Shai-Hulud", "Paul Atreides", "Baron Harkonnen"]
    chosen_mob = random.choice(high_level_mobs)
    notify_players(chosen_mob)
    update_mob_spawn_in_db(chosen_mob)
    print(f"A {chosen_mob} has spawned!")

def change_class(twitch_user_id, class_name):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Check if the player exists
            cursor.execute("""
                SELECT p.id FROM Player p
                JOIN TwitchUser tu ON p.twitch_user_id = tu.id
                WHERE tu.twitch_id = %s
            """, (twitch_user_id,))
            player = cursor.fetchone()

            if not player:
                return "Player not found. Please register first."

            # Check if the class exists
            cursor.execute("SELECT id FROM PlayerClass WHERE name=%s", (class_name,))
            player_class = cursor.fetchone()

            if not player_class:
                return "Invalid class name. Please choose a valid class."

            # Update the player's class
            cursor.execute("UPDATE Player SET class_id=%s WHERE id=%s", (player_class['id'], player['id']))
            connection.commit()

            return f"Class changed to {class_name} successfully!"
    except Exception as e:
        connection.rollback()
        logger.error(f"Error changing class: {e}", exc_info=True)
        return "An error occurred while changing class."
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


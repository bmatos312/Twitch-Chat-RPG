import pymysql
from datetime import datetime

# Database connection
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='tolstoy',
        password='Performix312!',
        db='rpg_data',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Example function to retrieve a player by username
def get_player_by_username(username):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Player WHERE username=%s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result
    finally:
        connection.close()

# Example function to add a new player
def add_player(username, email, password_hash, class_id, twitch_user_id=None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Player (username, email, password_hash, class_id, twitch_user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (username, email, password_hash, class_id, twitch_user_id, datetime.utcnow()))
            connection.commit()
    finally:
        connection.close()

# Example function to get a player's inventory
def get_player_inventory(player_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT Item.name, Inventory.quantity 
                FROM Inventory
                JOIN Item ON Inventory.item_id = Item.id
                WHERE Inventory.player_id = %s
            """
            cursor.execute(sql, (player_id,))
            result = cursor.fetchall()
            return result
    finally:
        connection.close()

# Example function to add a new item to a player's inventory
def add_item_to_inventory(player_id, item_id, quantity=1):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Inventory (player_id, item_id, quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + %s
            """
            cursor.execute(sql, (player_id, item_id, quantity, quantity))
            connection.commit()
    finally:
        connection.close()

# Similarly, you can add more functions for other models like Mob, GameSession, etc.


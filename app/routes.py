from flask import Blueprint, request, jsonify, redirect, url_for
import pymysql
from app.extensions import twitch
from app.game_logic import Bot, register_player  # Import the register_player function

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Welcome to the Twitch RPG Backend"

def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='tolstoy',
        password='Performix312!',
        db='rpg_data',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

@main.route('/test-db')
def test_db():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM Player")
            result = cursor.fetchone()
        connection.close()
        return jsonify({"status": "success", "players_count": result['count']})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

import json  # Add this import for handling JSON

@main.route('/twitch/event', methods=['POST'])
def handle_twitch_event():
    event_data = request.json
    print(f"Received event data: {event_data}")  # Debug print

    if not event_data:
        return jsonify({"error": "Invalid request"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            event_type = event_data.get('event_type')
            twitch_user_id = event_data.get('user_id')
            username = event_data.get('username')

            print(f"Event type: {event_type}, Twitch User ID: {twitch_user_id}, Username: {username}")  # Debug print

            # Retrieve the actual TwitchUser id from the database
            cursor.execute("SELECT id FROM TwitchUser WHERE twitch_id=%s", (twitch_user_id,))
            twitch_user = cursor.fetchone()

            if not twitch_user:
                # If the user doesn't exist, insert it first
                cursor.execute("INSERT INTO TwitchUser (twitch_id, username) VALUES (%s, %s)", (twitch_user_id, username))
                connection.commit()
                twitch_user_id_from_db = cursor.lastrowid
                print(f"Inserted new Twitch user: {username}, ID: {twitch_user_id_from_db}")  # Debug print
            else:
                twitch_user_id_from_db = twitch_user['id']

            # Log the event using the actual TwitchUser id
            event_data_json = json.dumps(event_data)  # Convert to JSON string
            cursor.execute(
                "INSERT INTO TwitchEvent (event_type, twitch_user_id, timestamp, data) VALUES (%s, %s, NOW(), %s)",
                (event_type, twitch_user_id_from_db, event_data_json)
            )
            connection.commit()
            print(f"Logged event: {event_type} for user {username}")  # Debug print

            # Trigger game logic if necessary
            if event_type == 'chat_command':
                command = event_data.get('command').lower()
                print(f"Processing command: {command}")  # Debug print

                if command == '!register':
                    result = register_player(twitch_user_id, username)
                    print(f"Registration result: {result}")  # Debug print
                    return jsonify({"result": result}), 200

                elif command == '!fight':
                    bot = Bot()
                    bet_amount = event_data.get('bet_amount', 0)  # Get bet_amount from event data, default to 0 if not provided
                    result = bot.fight(twitch_user_id, bet_amount)
                    print(f"Fight result: {result}")  # Debug print
                    return jsonify({"result": result}), 200

        connection.close()
        print("Event processed successfully")  # Debug print
        return jsonify({"status": "Event processed"}), 200

    except Exception as e:
        print(f"Error occurred: {e}")  # Debug print
        return jsonify({"error": str(e)}), 500

@main.route('/twitch/auth')
def twitch_auth():
    return twitch.authorize_redirect(redirect_uri=url_for('twitch_callback', _external=True))

@main.route('/twitch/callback')
def twitch_callback():
    token = twitch.authorize_access_token()
    resp = twitch.get('userinfo')
    profile = resp.json()
    # Handle user information and session management here
    return redirect(url_for('main.home'))


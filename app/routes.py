from flask import Blueprint, request, jsonify, redirect, url_for
from app import app, get_db_connection

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Welcome to the Twitch RPG Backend"

@main.route('/test-db')
def test_db():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS player_count FROM Player")
            result = cursor.fetchone()
        connection.close()
        return jsonify({"status": "success", "players_count": result['player_count']})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@main.route('/twitch/event', methods=['POST'])
def handle_twitch_event():
    event_data = request.json
    if not event_data:
        return jsonify({"error": "Invalid request"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            event_type = event_data.get('event_type')
            twitch_user_id = event_data.get('user_id')
            username = event_data.get('username')

            # Insert or update the Twitch user in the database
            cursor.execute("SELECT id FROM TwitchUser WHERE twitch_id=%s", (twitch_user_id,))
            twitch_user = cursor.fetchone()
            if not twitch_user:
                cursor.execute("INSERT INTO TwitchUser (twitch_id, username) VALUES (%s, %s)", (twitch_user_id, username))
                connection.commit()

            # Log the event
            cursor.execute(
                "INSERT INTO TwitchEvent (event_type, twitch_user_id, timestamp, data) VALUES (%s, %s, NOW(), %s)",
                (event_type, twitch_user_id, str(event_data))
            )
            connection.commit()
        
        connection.close()

        return jsonify({"status": "Event processed"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/twitch/auth')
def twitch_auth():
    # Your OAuth logic here
    pass

@main.route('/twitch/callback')
def twitch_callback():
    # Your OAuth callback logic here
    pass

app.register_blueprint(main)

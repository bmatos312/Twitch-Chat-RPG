from flask import Flask, request, jsonify, redirect, url_for
from app import app, db, twitch
from app. models import TwitchUser, TwitchEvent, Player
from app.game_logic import Bot

@app.route('/')
def home():
    return "Welcome to the Twitch RPG Backend"

@app.route('/twitch/event', methods=['POST'])
def handle_twitch_event():
    event_data = request.json
    if not event_data:
        return jsonify({"error": "Invalid request"}), 400

    try:
        # Parse the Twitch event and store it in the database
        event_type = event_data.get('event_type')
        twitch_user_id = event_data.get('user_id')
        username = event_data.get('username')

        # Store or update the Twitch user in the database
        twitch_user = TwitchUser.query.filter_by(twitch_id=twitch_user_id).first()
        if not twitch_user:
            twitch_user = TwitchUser(twitch_id=twitch_user_id, username=username)
            db.session.add(twitch_user)
            db.session.commit()

        # Create and store the event
        new_event = TwitchEvent(
            event_type=event_type,
            twitch_user_id=twitch_user.id,
            timestamp=datetime.utcnow(),
            data=event_data
        )
        db.session.add(new_event)
        db.session.commit()

        # Trigger game logic if necessary
        if event_type == 'chat_command':
            command = event_data.get('command')
            if command == '!fight':
                bot = Bot()
                result = bot.fight(twitch_user_id)
                return jsonify({"result": result}), 200

        return jsonify({"status": "Event processed"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/twitch/auth')
def twitch_auth():
    return twitch.authorize_redirect(redirect_uri=url_for('twitch_callback', _external=True))

@app.route('/twitch/callback')
def twitch_callback():
    token = twitch.authorize_access_token()
    resp = twitch.get('userinfo')
    profile = resp.json()
    # Handle user information and session management here
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)


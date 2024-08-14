from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

print("Setting up extensions...")  # Debug print

db = SQLAlchemy()
print("SQLAlchemy initialized.")  # Debug print

oauth = OAuth()
print("OAuth initialized.")  # Debug print

twitch = oauth.register(
    name='twitch',
    client_id='your_client_id',
    client_secret='your_client_secret',
    authorize_url='https://id.twitch.tv/oauth2/authorize',
    token_url='https://id.twitch.tv/oauth2/token',
    userinfo_url='https://api.twitch.tv/helix/users',
    redirect_uri='http://localhost:5000/twitch/callback',
    client_kwargs={'scope': 'user:read:email'},
)
print("Twitch OAuth client registered.")  # Debug print


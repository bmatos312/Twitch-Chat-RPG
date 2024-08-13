from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['OAUTH_CREDENTIALS'] = {
    'twitch': {
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret',
        'authorize_url': 'https://id.twitch.tv/oauth2/authorize',
        'token_url': 'https://id.twitch.tv/oauth2/token',
        'userinfo_url': 'https://api.twitch.tv/helix/users',
        'redirect_uri': 'http://localhost:5000/twitch/callback',
    }
}

db = SQLAlchemy(app)
oauth = OAuth(app)

twitch = oauth.register(
    name='twitch',
    client_id=app.config['OAUTH_CREDENTIALS']['twitch']['client_id'],
    client_secret=app.config['OAUTH_CREDENTIALS']['twitch']['client_secret'],
    authorize_url=app.config['OAUTH_CREDENTIALS']['twitch']['authorize_url'],
    authorize_params=None,
    authorize_redirect_uri=app.config['OAUTH_CREDENTIALS']['twitch']['redirect_uri'],
    access_token_url=app.config['OAUTH_CREDENTIALS']['twitch']['token_url'],
    access_token_params=None,
    client_kwargs={'scope': 'user:read:email'},
    redirect_uri=app.config['OAUTH_CREDENTIALS']['twitch']['redirect_uri'],
)

from app import routes  # Import routes after initializing app and oauth


from authlib.integrations.flask_client import OAuth

oauth = OAuth()
twitch = oauth.register(
    name='twitch',
    client_id='j2ypgxohqc0wwiq3s6qiz3685hzjmb',
    client_secret='ouhbphhlgmkob3hqnsarm7sqlzgmho',
    authorize_url='https://id.twitch.tv/oauth2/authorize',
    token_url='https://id.twitch.tv/oauth2/token',
    userinfo_url='https://api.twitch.tv/helix/users',
    redirect_uri='https://streamer-rpg.com/twitch/callback',
    client_kwargs={'scope': 'user:read:email'},
)


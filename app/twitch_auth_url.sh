#!/bin/bash

# Replace these with your actual Client ID, Redirect URI, and Scopes
CLIENT_ID="j2ypgxohqc0wwiq3s6qiz3685hzjmb"
REDIRECT_URI="http://localhost:5000/twitch/callback"
SCOPES="user:read:email"  # Add more scopes if needed, separated by spaces

# URL encode the redirect URI and scopes
ENCODED_REDIRECT_URI=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$REDIRECT_URI'''))")
ENCODED_SCOPES=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$SCOPES'''))")

# Construct the full URL
AUTH_URL="https://id.twitch.tv/oauth2/authorize?client_id=$CLIENT_ID&redirect_uri=$ENCODED_REDIRECT_URI&response_type=code&scope=$ENCODED_SCOPES"

# Output the URL
echo "Open the following URL in your browser to authorize the application:"
echo $AUTH_URL


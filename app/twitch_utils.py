import requests
import logging

# Optional: Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
TWITCH_OAUTH_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_STREAMS_URL = "https://api.twitch.tv/helix/streams"

def get_twitch_oauth_token(client_id, client_secret):
    """
    Get OAuth token for Twitch API.
    
    Args:
        client_id (str): The Twitch client ID.
        client_secret (str): The Twitch client secret.
    
    Returns:
        str: OAuth token.
    """
    try:
        params = {
            "client_id": j2ypgxohqc0wwiq3s6qiz3685hzjmb,
            "client_secret": ouhbphhlgmkob3hqnsarm7sqlzgmho,
            "grant_type": "client_credentials"
        }
        response = requests.post(TWITCH_OAUTH_URL, params=params)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logger.info("Successfully retrieved Twitch OAuth token.")
        return access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get Twitch OAuth token: {e}")
        return None

def is_streamer_live(client_id, client_secret, streamer_id):
    """
    Check if a Twitch streamer is currently live.
    
    Args:
        client_id (str): The Twitch client ID.
        client_secret (str): The Twitch client secret.
        streamer_id (str): The Twitch streamer ID.
    
    Returns:
        bool: True if the streamer is live, False otherwise.
    """
    access_token = get_twitch_oauth_token(client_id, client_secret)
    if not access_token:
        return False

    try:
        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}"
        }
        params = {"user_id": streamer_id}
        response = requests.get(TWITCH_STREAMS_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])

        if len(data) > 0 and data[0].get("type") == "live":
            logger.info(f"Streamer {streamer_id} is live.")
            return True
        else:
            logger.info(f"Streamer {streamer_id} is not live.")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to check streamer live status: {e}")
        return False

def get_streamer_id_by_name(client_id, client_secret, streamer_name


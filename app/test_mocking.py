from unittest.mock import patch
from app.twitch_event_handler import get_twitch_user_info

@patch('app.twitch_event_handler.requests.get')
def test_get_twitch_user_info(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'id': '12345', 'name': 'testuser'}

    user_info = get_twitch_user_info('testuser')
    assert user_info['id'] == '12345'
    assert user_info['name'] == 'testuser'

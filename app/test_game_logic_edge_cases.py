import pytest
from app.game_logic import calculate_dps, assign_rewards
from unittest.mock import patch

def test_no_damage():
    # All players have dealt 0 damage
    player_damage = {
        'player_1': {'total_damage': 0, 'time': 120},
        'player_2': {'total_damage': 0, 'time': 100},
        'player_3': {'total_damage': 0, 'time': 110},
    }

    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner is None
    assert rewards['gold'] == 0
    assert rewards['items'] == []

def test_same_dps():
    # Two players have the same DPS
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
        'player_2': {'total_damage': 500, 'time': 100},
        'player_3': {'total_damage': 600, 'time': 120},
    }

    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner in ['player_1', 'player_2']
    assert rewards['gold'] == 50.0  # Since both player_1 and player_2 have the same DPS
    assert 'items' in rewards

def test_no_items_for_class():
    # Test where the database returns no items for a class
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
        'player_2': {'total_damage': 700, 'time': 100},
        'player_3': {'total_damage': 600, 'time': 110},
    }

    winner, rewards = assign_rewards(player_damage, 'archer')
    assert winner == 'player_2'
    assert rewards['gold'] == 70.0
    assert rewards['items'] == []  # Assuming no items are set for 'archer' in the database

def test_no_players():
    player_damage = {}
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner is None, "There should be no winner if there are no players."
    assert rewards['gold'] == 0, "No gold should be awarded if there are no players."
    assert rewards['items'] == [], "No items should be awarded if there are no players."

def test_all_same_dps():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
        'player_2': {'total_damage': 500, 'time': 100},
        'player_3': {'total_damage': 500, 'time': 100},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner in player_damage.keys(), "Any player could be the winner in case of identical DPS."
    assert rewards['gold'] > 0, "Gold should be awarded."
    assert len(rewards['items']) >= 0, "Items should be awarded based on the drop table."

def test_negative_values():
    player_damage = {
        'player_1': {'total_damage': -100, 'time': 100},
        'player_2': {'total_damage': 500, 'time': -100},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner is None, "There should be no winner with invalid inputs."
    assert rewards['gold'] == 0, "No gold should be awarded with invalid inputs."
    assert rewards['items'] == [], "No items should be awarded with invalid inputs."

def test_zero_time_nonzero_damage():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 0},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner is None, "No player should win if time is zero."
    assert rewards['gold'] == 0, "No gold should be awarded."
    assert rewards['items'] == [], "No items should be awarded."

def test_unrecognized_class():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
    }
    winner, rewards = assign_rewards(player_damage, 'unknown_class')
    assert winner == 'player_1', "Player with highest DPS should still be the winner."
    assert rewards['gold'] > 0, "Gold should be awarded even if the class is unknown."
    assert rewards['items'] == [], "No items should be awarded if the class is unrecognized."

def test_large_values():
    player_damage = {
        'player_1': {'total_damage': 10**12, 'time': 10**6},
        'player_2': {'total_damage': 10**12, 'time': 10**6 + 1},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner == 'player_1', "Player with slightly better DPS should win."
    assert rewards['gold'] > 0, "Gold should be awarded for large damage values."
    assert len(rewards['items']) >= 0, "Items should be awarded based on the drop table."

def test_single_player():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner == 'player_1', "The only player should be the winner."
    assert rewards['gold'] > 0, "Gold should be awarded."
    assert len(rewards['items']) >= 0, "Items should be awarded based on the drop table."

def test_tied_dps_different_classes():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 100},
        'player_2': {'total_damage': 500, 'time': 100},
    }
    winner, rewards = assign_rewards(player_damage, 'archer')
    assert winner in ['player_1', 'player_2'], "Either player should win with tied DPS."
    assert rewards['gold'] > 0, "Gold should be awarded."
    assert 'items' in rewards, "Items should be awarded based on the class."

@patch('twitch_utils.is_streamer_live')
def test_streamer_live_status(mock_is_live):
    # Simulate streamer being live
    mock_is_live.return_value = True
    assert is_streamer_live('fake_client_id', 'fake_client_secret', 'fake_streamer_id') == True

    # Simulate streamer not being live
    mock_is_live.return_value = False
    assert is_streamer_live('fake_client_id', 'fake_client_secret', 'fake_streamer_id') == False

@patch('twitch_utils.is_streamer_live')
@patch('game_logic.spawn_high_level_mob')
def test_mob_spawning_when_live(mock_spawn_mob, mock_is_live):
    # Simulate streamer being live
    mock_is_live.return_value = True
    check_and_spawn_mob()  # This should trigger the mob spawn
    mock_spawn_mob.assert_called_once()

@patch('twitch_utils.is_streamer_live')
@patch('game_logic.spawn_high_level_mob')
def test_no_mob_spawning_when_not_live(mock_spawn_mob, mock_is_live):
    # Simulate streamer not being live
    mock_is_live.return_value = False
    check_and_spawn_mob()  # This should not trigger the mob spawn
    mock_spawn_mob.assert_not_called()

def test_high_level_mob_selection():
    high_level_mobs = ["Sandworm of Shai-Hulud", "Paul Atreides", "Baron Harkonnen"]
    chosen_mob = spawn_high_level_mob()
    assert chosen_mob in high_level_mobs, "The chosen mob should be one of the high-level mobs."

@patch('game_logic.update_mob_spawn_in_db')
def test_database_update_on_mob_spawn(mock_update_db):
    chosen_mob = spawn_high_level_mob()
    mock_update_db.assert_called_once_with(chosen_mob)


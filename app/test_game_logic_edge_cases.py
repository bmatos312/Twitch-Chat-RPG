from app.game_logic import calculate_dps, assign_rewards

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


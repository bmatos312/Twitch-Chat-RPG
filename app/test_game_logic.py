from app.game_logic import calculate_dps, assign_rewards

def test_calculate_dps():
    assert calculate_dps(500, 100) == 5.0
    assert calculate_dps(0, 100) == 0.0
    assert calculate_dps(500, 0) == 0.0

def test_assign_rewards():
    player_damage = {
        'player_1': {'total_damage': 500, 'time': 120},
        'player_2': {'total_damage': 700, 'time': 100},
        'player_3': {'total_damage': 600, 'time': 110},
    }
    winner, rewards = assign_rewards(player_damage, 'warrior')
    assert winner == 'player_2'
    assert rewards['gold'] > 0
    assert len(rewards['items']) > 0


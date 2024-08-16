import pytest
from app.game_logic import calculate_score

def test_calculate_score():
    result = calculate_score(5, 10)
    assert result == 15

import pytest
from app.models import User, db

def test_create_user():
    user = User(username='testuser', email='test@example.com')
    db.session.add(user)
    db.session.commit()
    assert user.id is not None

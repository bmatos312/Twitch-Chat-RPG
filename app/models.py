from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    games = db.relationship('GameSession', backref='player', lazy='dynamic')
    twitch_user_id = db.Column(db.Integer, db.ForeignKey('twitch_user.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('player_class.id'), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    attack = db.Column(db.Integer, default=10)
    defense = db.Column(db.Integer, default=5)
    inventory = db.relationship('Item', secondary='inventory', backref='owners')

    def __repr__(self):
        return f'<Player {self.username}>'

class PlayerClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    base_health = db.Column(db.Integer, nullable=False)
    base_attack = db.Column(db.Integer, nullable=False)
    base_defense = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    players = db.relationship('Player', backref='class', lazy=True)

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<GameSession {self.id} for Player {self.player_id}>'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    value = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Item {self.name}>'

class Inventory(db.Model):
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Inventory Item {self.item.name} x{self.quantity} for Player {self.player_id}>'

class TwitchUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    twitch_id = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return f'<TwitchUser {self.username}>'

class TwitchEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(64), nullable=False)
    twitch_user_id = db.Column(db.Integer, db.ForeignKey('twitch_user.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.JSON)

    def __repr__(self):
        return f'<TwitchEvent {self.event_type} by TwitchUser {self.twitch_user_id}>'

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))
    points = db.Column(db.Integer, default=0)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    item = db.relationship('Item', backref='rewards')

    def __repr__(self):
        return f'<Reward {self.description}>'


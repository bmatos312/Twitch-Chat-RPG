from datetime import datetime
from app import db
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False

# Player Model
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    games = db.relationship('GameSession', backref='player', lazy='dynamic')
    twitch_user_id = db.Column(db.Integer, db.ForeignKey('twitch_user.id'), nullable=True)
    twitch_user = db.relationship('TwitchUser', backref='player', uselist=False)
    class_id = db.Column(db.Integer, db.ForeignKey('player_class.id'), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=100)
    attack = db.Column(db.Integer, default=10)
    defense = db.Column(db.Integer, default=5)
    inventory = db.relationship('Item', backref='owner', lazy=True)

    def __repr__(self):
        return f'<Player {self.username}>'

class PlayerClass(db.MOdel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    base_health = db.Column(db.Integer, nullable=False)
    base_attack = db.Column(db.Intger, nullable=False)
    base_defense = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
   
    Players = db.relationship('Player', backref='player_class', lazy=True)

# GameSession Model
class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<GameSession {self.id} for Player {self.player_id}>'

# Item Model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    value = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Item {self.name}>'

# Inventory Model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    item = db.relationship('Item', backref='inventory')

    def __repr__(self):
        return f'<Inventory Item {self.item.name} x{self.quantity} for Player {self.player_id}>'

# TwitchUser Model
class TwitchUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    twitch_id = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    player = db.relationship('Player', backref='twitch_user', uselist=False)

    def __repr__(self):
        return f'<TwitchUser {self.username}>'

# TwitchEvent Model
class TwitchEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(64), nullable=False)  # e.g., 'chat_command', 'follow', 'subscription'
    twitch_user_id = db.Column(db.Integer, db.ForeignKey('twitch_user.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.JSON)  # Store additional data about the event
    twitch_user = db.relationship('TwitchUser', backref='events')
    player = db.relationship('Player', backref='events')

    def __repr__(self):
        return f'<TwitchEvent {self.event_type} by TwitchUser {self.twitch_user_id}>'

# Reward Model
class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256))
    points = db.Column(db.Integer, default=0)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    item = db.relationship('Item', backref='rewards')

    def __repr__(self):
        return f'<Reward {self.description}>'


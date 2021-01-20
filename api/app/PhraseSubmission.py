from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from app import db
from app.Player import Player

MAX_PHRASE_LENGTH = 2048

class PhraseSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime(), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player = db.relationship(Player, lazy='joined')
    phrase = db.Column(db.String(MAX_PHRASE_LENGTH), nullable=False)

    def __init__(self, player, phrase):
        self.time = datetime.now()
        self.player = player
        self.phrase = phrase

    def get_player(self):
        return self.player

    def get_phrase(self):
        return self.phrase

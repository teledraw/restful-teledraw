from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import TEXT

from app import db
from app.Player import Player

MAX_IMAGE_LENGTH = 5242880

class ImageSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime(), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player = db.relationship(Player, lazy='joined')
    image = db.Column(TEXT(MAX_IMAGE_LENGTH), nullable=False)

    def __init__(self, player, image):
        self.time = datetime.now()
        self.player = player
        self.image = image

    def get_player(self):
        return self.player

    def get_image(self):
        return self.image

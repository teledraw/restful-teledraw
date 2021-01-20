from datetime import datetime

from app import db

MAX_LENGTH = 256

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_LENGTH), nullable=False)
    status = db.Column(db.String(MAX_LENGTH), nullable=False)
    time_joined = db.Column(db.DateTime(), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    def __init__(self, username):
        self.name = username
        self.status = "SUBMIT_INITIAL_PHRASE"
        self.time_joined = datetime.now()

    def get_name(self):
        return self.name

    def get_status(self):
        return self.status

    def set_status(self, new_status):
        self.status = new_status

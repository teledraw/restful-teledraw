from datetime import datetime

from app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False)
    time_joined = db.Column(db.DateTime(), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    def __init__(self, username):
        self._name = username
        self._status = "SUBMIT_INITIAL_PHRASE"
        self._time_joined = datetime.now()

    def get_name(self):
        return self._name

    def get_status(self):
        return self._status

    def set_status(self, new_status):
        self._status = new_status

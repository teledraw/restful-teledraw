from datetime import datetime


class Player:
    _name = ""
    _status = ""
    _time_joined = None

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

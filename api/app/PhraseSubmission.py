from datetime import datetime


class PhraseSubmission:
    _time = None
    _player = None
    _phrase = ""

    def __init__(self, player, phrase):
        self._time = datetime.now()
        self._player = player
        self._phrase = phrase

    def get_player(self):
        return self._player

    def get_phrase(self):
        return self._phrase

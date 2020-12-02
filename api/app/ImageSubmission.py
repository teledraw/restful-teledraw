from datetime import datetime


class ImageSubmission:
    _time = None
    _player = None
    _image = ""

    def __init__(self, player, image):
        self._time = datetime.now()
        self._player = player
        self._image = image

    def get_player(self):
        return self._player

    def get_image(self):
        return self._image

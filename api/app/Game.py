class Game:

    userStatuses = dict()
    images = dict()
    phrases = dict()
    code = ""

    def __init__(self, game_code):
        self.code = game_code
        self.userStatuses = dict()
        self.phrases = dict()
        self.images = dict()


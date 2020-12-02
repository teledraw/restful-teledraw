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

    def is_over(self):
        number_of_users = len(self.userStatuses.keys())
        for user in self.userStatuses.keys():
            if user not in self.phrases.keys() or user not in self.images.keys() or len(
                    self.phrases[user]) + len(
                    self.images[user]) != number_of_users:
                return False
        return number_of_users > 0

    def too_late_to_join(self):
        return not all(status == "SUBMIT_INITIAL_PHRASE" for status in list(self.userStatuses.values()))

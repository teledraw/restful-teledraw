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

    def set_user_status(self, username, new_status):
        self.userStatuses[username] = new_status
        self.update_status_if_all_players_done()

    def update_status_if_all_players_done(self):
        if all(status == 'WAIT' for status in self.userStatuses.values()):
            next_status = 'SUBMIT_PHRASE' if self.get_phase_number() % 2 == 1 else 'SUBMIT_IMAGE'
            if self.is_over():
                next_status = 'GAME_OVER'
            for user in self.userStatuses.keys():
                self.set_user_status(user, next_status)

    def get_phase_number(self):
        current_number_of_players = len(self.userStatuses)
        if len(self.phrases) < current_number_of_players:
            return 1
        elif len(self.images) < current_number_of_players:
            return 2
        else:
            completed_phrase_rounds = len(self.phrases[min(self.phrases, key=len)])
            completed_image_rounds = len(self.images[min(self.images, key=len)])
            return 1 + completed_image_rounds + completed_phrase_rounds

    def save_phrase(self, username, new_phrase):
        if username not in self.phrases.keys():
            self.phrases[username] = [new_phrase]
        else:
            self.phrases[username].append(new_phrase)
        self.set_user_status(username, "WAIT")

    def save_image(self, username, new_image):
        if username not in self.images.keys():
            self.images[username] = [new_image]
        else:
            self.images[username].append(new_image)
        self.set_user_status(username, "WAIT")

    def join(self, username):
        self.set_user_status(username, 'SUBMIT_INITIAL_PHRASE')

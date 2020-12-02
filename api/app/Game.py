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

    def get_phrase_prompt(self, username):
        username_of_phrase_source = self.get_previous_player(username)
        return self.phrases[username_of_phrase_source][-1]

    def get_image_prompt(self, username):
        username_of_image_source = self.get_previous_player(username)
        return self.images[username_of_image_source][-1]

    def get_next_player(self, username):
        usernames = list(self.userStatuses.keys())
        return usernames[0] if usernames.index(username) == len(usernames) - 1 else usernames[
            usernames.index(username) + 1]

    def get_previous_player(self, username):
        usernames = list(self.userStatuses.keys())
        return usernames[len(usernames) - 1] if usernames.index(username) == 0 else usernames[
            usernames.index(username) - 1]

    def get_user_status(self, username, just_the_status=False):
        status_for_user = self.userStatuses[username]
        if just_the_status:
            return {'description': status_for_user}
        elif status_for_user == 'SUBMIT_IMAGE' or status_for_user == 'SUBMIT_PHRASE':
            return {'description': status_for_user,
                    'prompt': self.get_phrase_prompt(
                        username) if status_for_user == 'SUBMIT_IMAGE' else self.get_image_prompt(username),
                    'previousPlayerUsername': self.get_previous_player(username),
                    'nextPlayerUsername': self.get_next_player(username)}
        return {'description': status_for_user, 'previousPlayerUsername': self.get_previous_player(username),
                'nextPlayerUsername': self.get_next_player(username)}

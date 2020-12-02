class Game:
    _userStatuses = dict()
    _images = dict()
    _phrases = dict()
    code = ""

    def __init__(self, game_code):
        self.code = game_code
        self._userStatuses = dict()
        self._phrases = dict()
        self._images = dict()

    def is_over(self):
        number_of_users = len(self._userStatuses.keys())
        for user in self._userStatuses.keys():
            if user not in self._phrases.keys() or user not in self._images.keys() or len(
                    self._phrases[user]) + len(
                self._images[user]) != number_of_users:
                return False
        return number_of_users > 0

    def is_action_allowed(self, username, action):
        if(action == "submitphrase"):
            return self.get_user_status(username, True)['description'] in ["SUBMIT_PHRASE", "SUBMIT_INITIAL_PHRASE"]
        elif(action == "submitimage"):
            return self.get_user_status(username, True)['description'] == "SUBMIT_IMAGE"
        return False

    def has_player(self, username):
        return username in self._userStatuses.keys()

    def too_late_to_join(self):
        return not all(status == "SUBMIT_INITIAL_PHRASE" for status in list(self._userStatuses.values()))

    def set_user_status(self, username, new_status):
        self._userStatuses[username] = new_status
        self.update_status_if_all_players_done()

    def update_status_if_all_players_done(self):
        if all(status == 'WAIT' for status in self._userStatuses.values()):
            next_status = 'SUBMIT_PHRASE' if self.get_phase_number() % 2 == 1 else 'SUBMIT_IMAGE'
            if self.is_over():
                next_status = 'GAME_OVER'
            for user in self._userStatuses.keys():
                self.set_user_status(user, next_status)

    def get_phase_number(self):
        current_number_of_players = len(self._userStatuses)
        if len(self._phrases) < current_number_of_players:
            return 1
        elif len(self._images) < current_number_of_players:
            return 2
        else:
            completed_phrase_rounds = len(self._phrases[min(self._phrases, key=len)])
            completed_image_rounds = len(self._images[min(self._images, key=len)])
            return 1 + completed_image_rounds + completed_phrase_rounds

    def save_phrase(self, username, new_phrase):
        if username not in self._phrases.keys():
            self._phrases[username] = [new_phrase]
        else:
            self._phrases[username].append(new_phrase)
        self.set_user_status(username, "WAIT")

    def save_image(self, username, new_image):
        if username not in self._images.keys():
            self._images[username] = [new_image]
        else:
            self._images[username].append(new_image)
        self.set_user_status(username, "WAIT")

    def join(self, username):
        self.set_user_status(username, 'SUBMIT_INITIAL_PHRASE')

    def get_phrase_prompt(self, username):
        username_of_phrase_source = self.get_previous_player(username)
        return self._phrases[username_of_phrase_source][-1]

    def get_image_prompt(self, username):
        username_of_image_source = self.get_previous_player(username)
        return self._images[username_of_image_source][-1]

    def get_players(self):
        return self._userStatuses.keys()

    def get_next_player(self, username):
        usernames = list(self._userStatuses.keys())
        return usernames[0] if usernames.index(username) == len(usernames) - 1 else usernames[
            usernames.index(username) + 1]

    def get_previous_player(self, username):
        usernames = list(self._userStatuses.keys())
        return usernames[len(usernames) - 1] if usernames.index(username) == 0 else usernames[
            usernames.index(username) - 1]

    def get_user_status(self, username, just_the_status=False):
        status_for_user = self._userStatuses[username]
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

    def get_all_submission_threads_indexed_by_user(self):
        to_return = list()
        for username in self._userStatuses.keys():
            to_return.append({"originator": username, "submissions": self.get_user_submission_thread(username)})
        return to_return

    def get_user_submission_thread(self, username):
        users = list(self._userStatuses.keys())
        index_of_original_user = users.index(username)
        to_return = [self._phrases[username][0]]
        for i in range(1, len(users)):
            user = users[(index_of_original_user + i) % len(users)]
            to_return.append(
                self._phrases[user][int(i / 2)] if i % 2 == 0 else
                self._images[user][
                    int(i / 2)])
        return to_return

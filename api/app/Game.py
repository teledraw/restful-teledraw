from flask_sqlalchemy import SQLAlchemy

from app.ImageSubmission import ImageSubmission
from app.PhraseSubmission import PhraseSubmission
from app.Player import Player

db = SQLAlchemy()
MAX_CODE_LENGTH = 40

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(MAX_CODE_LENGTH), unique=True, nullable=False)

    players = db.relationship(Player, lazy='joined')
    _image_submissions = list()
    _phrase_submissions = list()

    def __init__(self, game_code):
        self.code = game_code
        self._players = list()
        self._image_submissions = list()
        self._phrase_submissions = list()

    def get_player(self, username):
        return next((player for player in self._players if player.get_name() == username), None)

    def is_over(self):
        number_of_users = len(self.get_players())
        if number_of_users < 1:
            return False
        else:
            return len(self._phrase_submissions) + len(self._image_submissions) == number_of_users ** 2

    def is_action_allowed(self, username, action):
        if action == "submitphrase":
            return self.get_user_status(username, True)['description'] in ["SUBMIT_PHRASE", "SUBMIT_INITIAL_PHRASE"]
        elif action == "submitimage":
            return self.get_user_status(username, True)['description'] == "SUBMIT_IMAGE"
        return False

    def has_player(self, username):
        return username in self.get_playernames()

    def too_late_to_join(self):
        return not all(status == "SUBMIT_INITIAL_PHRASE" for status in list(p.get_status() for p in self._players))

    def too_early_to_start(self):
        return len(self._players) < 2

    def set_user_status(self, username, new_status):
        self.get_player(username).set_status(new_status)
        self.update_status_if_all_players_done()

    def update_status_if_all_players_done(self):
        if all(status == 'WAIT' for status in list(p.get_status() for p in self.get_players())):
            next_status = 'SUBMIT_PHRASE' if self.get_phase_number() % 2 == 1 else 'SUBMIT_IMAGE'
            if self.is_over():
                next_status = 'GAME_OVER'
            for user in self.get_playernames():
                self.set_user_status(user, next_status)

    def get_phase_number(self):
        current_number_of_players = len(self.get_players())
        if len(self._phrase_submissions) < current_number_of_players:
            return 1
        elif len(self._image_submissions) < current_number_of_players:
            return 2
        else:
            completed_phrase_rounds = len(self._phrase_submissions) / len(self.get_players())
            completed_image_rounds = len(self._image_submissions) / len(self.get_players())
            return 1 + completed_image_rounds + completed_phrase_rounds

    def save_phrase(self, username, new_phrase):
        self._phrase_submissions.append(PhraseSubmission(self.get_player(username), new_phrase))
        self.set_user_status(username, "WAIT")

    def save_image(self, username, new_image):
        self._image_submissions.append(ImageSubmission(self.get_player(username), new_image))
        self.set_user_status(username, "WAIT")

    def join(self, username):
        if not self.has_player(username):
            self._players.append(Player(username))
            self.set_user_status(username, 'SUBMIT_INITIAL_PHRASE')

    def get_phrase_prompt(self, username):
        username_of_phrase_source = self.get_previous_player(username)
        return self.get_all_submissions_by_player(self.get_player(username_of_phrase_source), type='phrase')[-1].get_phrase()

    def get_image_prompt(self, username):
        username_of_image_source = self.get_previous_player(username)
        return self.get_all_submissions_by_player(self.get_player(username_of_image_source))[-1].get_image()

    def get_all_submissions_by_player(self, player, type='image'):
        return list(filter(lambda x: x.get_player() == player, self._image_submissions if type == 'image' else self._phrase_submissions))

    def get_playernames(self):
        return [player.name for player in self.players]

    def get_next_player(self, username):
        usernames = self.get_playernames()
        return usernames[0] if usernames.index(username) == len(usernames) - 1 else usernames[
            usernames.index(username) + 1]

    def get_previous_player(self, username):
        usernames = self.get_playernames()
        return usernames[len(usernames) - 1] if usernames.index(username) == 0 else usernames[
            usernames.index(username) - 1]

    def get_user_status(self, username, just_the_status=False):
        status_for_user = self.get_player(username).get_status()
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
        for username in list(p.get_name() for p in self.get_players()):
            to_return.append({"originator": username, "submissions": self.get_user_submission_thread(username)})
        return to_return

    def get_user_submission_thread(self, username):
        users = self.get_playernames()
        index_of_original_user = users.index(username)
        to_return = [self.get_all_submissions_by_player(self.get_player(username), type='phrase')[0].get_phrase()]
        for i in range(1, len(users)):
            user = users[(index_of_original_user + i) % len(users)]
            to_return.append(
                self.get_all_submissions_by_player(self.get_player(user), type='phrase')[int(i / 2)].get_phrase() if i % 2 == 0 else
                self.get_all_submissions_by_player(self.get_player(user))[
                    int(i / 2)].get_image())
        return to_return

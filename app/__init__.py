import click
from flask import Flask
from flask import request
from flask import jsonify


_userStatuses = {}
# SUBMIT_INITIAL_PHRASE, SUBMIT_IMAGE, WAIT
_phrases = {}

def create_app():
    app = Flask(__name__)

    # a simple response that says hello
    @app.route('/')
    def hello_world():
        return 'Hello World!'

    @app.route('/join', methods=['POST'])
    def join_game():
        if checkUsernameExists(request):
            _userStatuses[request.form.get('username')] = 'SUBMIT_INITIAL_PHRASE'
            return '', 200
        return '', 400


    @app.route('/status', methods=['GET'])
    def get_status_for_player():
        if request.args['username'] in _userStatuses.keys():
            statusForUser = _userStatuses[request.args['username']]
            if(statusForUser == 'SUBMIT_IMAGE'):
                prompt = getPhrasePrompt(request.args['username'])
                return jsonify({'description': statusForUser, 'prompt': prompt}), 200
            return jsonify({'description': statusForUser}), 200
        return '', 400

    @app.route('/phrase', methods=['POST'])
    def submit_phrase():
        if request.form.get('username') in _userStatuses.keys() and (_userStatuses[request.form.get('username')] in ["SUBMIT_INITIAL_PHRASE", "SUBMIT_PHRASE"]):
            savePhrase(request.form.get('username'), request.form.get('phrase'))
            _userStatuses[request.form.get('username')] = "WAIT"

            if all(status == 'WAIT' for status in _userStatuses.values()):
                for user in _userStatuses.keys():
                    _userStatuses[user] = 'SUBMIT_IMAGE'
            return '', 200
        return '', 400


    def checkUsernameExists(_request):
        return (_request.form.get('username') is not None and _request.form.get('username') != '')


    def checkStatusForPlayer(username):
        if(username in _userStatuses.keys()):
            return _userStatuses[username]
        else:
            return "ERROR_USER_NOT_JOINED"

    def savePhrase(username, phrase):
        if(username not in _phrases.keys()):
            _phrases[username] = [phrase]
        else:
            _phrases[username].append(phrase)

    def getPhrasePrompt(username):
        users = list(_userStatuses.keys())
        indexOfUser = users.index(username)
        usernameOfPhraseSource = users[(indexOfUser + 1) % len(users)]
        return _phrases[usernameOfPhraseSource][-1]

    # enable flask test command
    # specify the test location for test discovery
    # or pass argument of test name to run specific test
    @app.cli.command("test")
    @click.argument('test_names', nargs=-1)
    def test(test_names):
        import unittest
        if test_names:
            tests = unittest.TestLoader().loadTestsFromNames(test_names)
        else:
            tests = unittest.TestLoader().discover('tests')
        unittest.TextTestRunner(verbosity=2).run(tests)

    return app

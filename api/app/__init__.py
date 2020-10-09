import click
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin

_userStatuses = {}
_phrases = {}
_images = {}


def gameOver():
    number_of_users = len(_userStatuses.keys())
    for user in _userStatuses.keys():
        if user not in _phrases.keys() or user not in _images.keys() or len(_phrases[user]) + len(
                _images[user]) != number_of_users:
            return False
    return number_of_users > 0

def tooLateToJoin():
    return not all(status == "SUBMIT_INITIAL_PHRASE" for status in list(_userStatuses.values()))


def getNextPlayer(username):
    usernames = list(_userStatuses.keys())
    return usernames[0] if usernames.index(username) == len(usernames) - 1 else usernames[usernames.index(username) + 1]


def getPreviousPlayer(username):
    usernames = list(_userStatuses.keys())
    return usernames[len(usernames) - 1] if usernames.index(username) == 0 else usernames[usernames.index(username) - 1]


def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    @app.route('/')
    @cross_origin()
    def hello_world():
        return 'This is the Arktika API base URL.  Please add an endpoint name to your request to get started.'

    @app.route('/join', methods=['POST'])
    @cross_origin()
    def join_game():
        if not request_includes_username(request):
            return jsonify({'error': "Cannot join without username."}), 400
        elif tooLateToJoin():
            return jsonify({'error': "Cannot join a game in progress."}), 400
        else:
            _userStatuses[request.json['username']] = 'SUBMIT_INITIAL_PHRASE'
            return '', 200

    @app.route('/status', methods=['GET'])
    @cross_origin()
    def get_status_for_player():
        if request.args['username'] in _userStatuses.keys():
            return jsonify(get_user_status(request.args['username'])), 200
        return '', 400

    def get_user_status(username):
        statusForUser = _userStatuses[username]
        if (statusForUser == 'SUBMIT_IMAGE' or statusForUser == 'SUBMIT_PHRASE'):
            return {'description': statusForUser,
                    'prompt': getPhrasePrompt(username) if statusForUser == 'SUBMIT_IMAGE' else getImagePrompt(
                        username), 'previousPlayerUsername': getPreviousPlayer(username),
                    'nextPlayerUsername': getNextPlayer(username)}
        return {'description': statusForUser, 'previousPlayerUsername': getPreviousPlayer(username),
                'nextPlayerUsername': getNextPlayer(username)}

    @app.route('/phrase', methods=['POST'])
    @cross_origin()
    def submit_phrase():
        if request.json['username'] in _userStatuses.keys() and (
                _userStatuses[request.json['username']] in ["SUBMIT_INITIAL_PHRASE", "SUBMIT_PHRASE"]):
            savePhrase(request.json['username'], request.json['phrase'])
            _userStatuses[request.json['username']] = "WAIT"

            if all(status == 'WAIT' for status in _userStatuses.values()):
                next_status = 'SUBMIT_IMAGE'
                if gameOver():
                    next_status = 'GAME_OVER'

                for user in _userStatuses.keys():
                    _userStatuses[user] = next_status
            return '', 200
        return '', 400

    @app.route('/image', methods=['POST'])
    @cross_origin()
    def submit_image():
        if request.json['username'] in _userStatuses.keys() and (
                _userStatuses[request.json['username']] == "SUBMIT_IMAGE"):
            saveImage(request.json['username'], request.json['image'])
            _userStatuses[request.json['username']] = "WAIT"

            if all(status == 'WAIT' for status in _userStatuses.values()):
                next_status = 'SUBMIT_PHRASE'
                if gameOver():
                    next_status = 'GAME_OVER'
                for user in _userStatuses.keys():
                    _userStatuses[user] = next_status
            return '', 200
        return '', 400

    @app.route('/summary', methods=['GET'])
    @cross_origin()
    def summary():
        status_summary = list()
        for user in _userStatuses.keys():
            user_status = dict()
            user_status['username'] = user
            user_status['status'] = get_user_status(user)
            status_summary.append(user_status)
        return jsonify(status_summary), 200

    @app.route('/results', methods=['GET'])
    @cross_origin()
    def get_results():
        if gameOver():
            return jsonify(getAllSubmissionThreadsByUser()), 200
        else:
            return 'Cannot get results: game not over', 400

    @app.route('/restart', methods=['POST'])
    @cross_origin()
    def restart_game():
        _userStatuses.clear()
        _phrases.clear()
        _images.clear()
        return '', 200

    def getAllSubmissionThreadsByUser():
        toReturn = list()
        for user in _userStatuses.keys():
            toReturn.append({"originator": user, "submissions": getUserSubmissionThread(user)})
        return toReturn

    def getUserSubmissionThread(username):
        users = list(_userStatuses.keys())
        indexOfOriginalUser = users.index(username)
        toReturn = [_phrases[username][0]]
        for i in range(1, len(_userStatuses.keys())):
            user = users[(indexOfOriginalUser + i) % len(users)]
            toReturn.append(_phrases[user][int(i / 2)] if i % 2 == 0 else _images[user][int(i / 2)])
        return toReturn

    def request_includes_username(_request):
        return (_request.json is not None and _request.json['username'] is not None and _request.json['username'] != '')

    def savePhrase(username, phrase):
        if (username not in _phrases.keys()):
            _phrases[username] = [phrase]
        else:
            _phrases[username].append(phrase)

    def getPhrasePrompt(username):
        users = list(_userStatuses.keys())
        indexOfUser = users.index(username)
        usernameOfPhraseSource = users[(indexOfUser + 1) % len(users)]
        return _phrases[usernameOfPhraseSource][-1]

    def saveImage(username, image):
        if (username not in _images.keys()):
            _images[username] = [image]
        else:
            _images[username].append(image)

    def getImagePrompt(username):
        users = list(_userStatuses.keys())
        indexOfUser = users.index(username)
        usernameOfImageSource = users[(indexOfUser + 1) % len(users)]
        return _images[usernameOfImageSource][-1]

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

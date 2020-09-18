import click
from flask import Flask
from flask import request
from flask import jsonify
import math


_userStatuses = {}
# SUBMIT_INITIAL_PHRASE, SUBMIT_IMAGE, WAIT
_phrases = {}
_images = {}


def gameOver():
    number_of_users = len (_userStatuses.keys())
    for user in _userStatuses.keys():
        if user not in _phrases.keys() or user not in _images.keys() or len(_phrases[user]) + len(_images[user]) != number_of_users:
            return False
    return number_of_users > 0

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
            if(statusForUser == 'SUBMIT_PHRASE'):
                prompt = getImagePrompt(request.args['username'])
                return jsonify({'description': statusForUser, 'prompt': prompt}), 200
            return jsonify({'description': statusForUser}), 200
        return '', 400

    @app.route('/phrase', methods=['POST'])
    def submit_phrase():
        if request.form.get('username') in _userStatuses.keys() and (_userStatuses[request.form.get('username')] in ["SUBMIT_INITIAL_PHRASE", "SUBMIT_PHRASE"]):
            savePhrase(request.form.get('username'), request.form.get('phrase'))
            _userStatuses[request.form.get('username')] = "WAIT"

            if all(status == 'WAIT' for status in _userStatuses.values()):
                next_status = 'SUBMIT_IMAGE'
                if gameOver():
                    next_status = 'GAME_OVER'

                for user in _userStatuses.keys():
                    _userStatuses[user] = next_status
            return '', 200
        return '', 400

    @app.route('/image', methods=['POST'])
    def submit_image():
        if request.form.get('username') in _userStatuses.keys() and (_userStatuses[request.form.get('username')] == "SUBMIT_IMAGE"):
            saveImage(request.form.get('username'), request.form.get('image'))
            _userStatuses[request.form.get('username')] = "WAIT"

            if all(status == 'WAIT' for status in _userStatuses.values()):
                next_status = 'SUBMIT_PHRASE'
                if gameOver():
                    next_status = 'GAME_OVER'
                for user in _userStatuses.keys():
                    _userStatuses[user] = next_status
            return '', 200
        return '', 400

    @app.route('/results', methods=['GET'])
    def get_results():
        if gameOver():
            return jsonify(getAllSubmissionThreadsByUser()), 200
        else:
            return 'Cannot get results: game not over', 400


    @app.route('/restart', methods=['POST'])
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
            toReturn.append(_phrases[user][int(i/2)] if i % 2 == 0 else _images[user][int(i/2)])
        return toReturn


    def checkUsernameExists(_request):
        return (_request.form.get('username') is not None and _request.form.get('username') != '')

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

    def saveImage(username, image):
        if(username not in _images.keys()):
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

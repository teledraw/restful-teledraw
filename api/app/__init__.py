import click
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin

_games = dict()


def gameOver(game):
    number_of_users = len(_games[game]['userStatuses'].keys())
    for user in _games[game]['userStatuses'].keys():
        if user not in _games[game]['phrases'].keys() or user not in _games[game]['images'].keys() or len(
                _games[game]['phrases'][user]) + len(
            _games[game]['images'][user]) != number_of_users:
            return False
    return number_of_users > 0


def game_exists(game):
    return game in _games.keys()


def tooLateToJoin(game):
    return game_exists(game) and not all(
        status == "SUBMIT_INITIAL_PHRASE" for status in list(_games[game]['userStatuses'].values()))


def getNextPlayer(username, gamecode):
    usernames = list(_games[gamecode]['userStatuses'].keys())
    return usernames[0] if usernames.index(username) == len(usernames) - 1 else usernames[usernames.index(username) + 1]


def getPreviousPlayer(username, gamecode):
    usernames = list(_games[gamecode]['userStatuses'].keys())
    return usernames[len(usernames) - 1] if usernames.index(username) == 0 else usernames[usernames.index(username) - 1]


def create_game(game_code):
    _games[game_code] = {'userStatuses': dict(), 'phrases': dict(), 'images': dict()}


def err(message, statusCode=400):
    return jsonify({"error": message}), statusCode


def request_includes_game_code(_request):
    return _request.json is not None and 'game' in _request.json.keys() and _request.json['game'] != ''


def request_includes_username(_request):
    return _request.json is not None and 'username' in _request.json.keys() and _request.json['username'] != ''


def args_includes_username(_request):
    return _request.args is not None and 'username' in _request.args.keys() and _request.args['username'] != ''


def args_includes_game_code(_request):
    return _request.args is not None and 'game' in _request.args.keys() and _request.args['game'] != ''


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
        (username, gamecode) = require_request_data(request, 'join game', inBody=True)
        if not username:
            return gamecode
        elif tooLateToJoin(gamecode):
            return err("Cannot join a game in progress.")
        else:
            if (gamecode not in _games.keys()):
                create_game(gamecode)
            _games[gamecode]['userStatuses'][username] = 'SUBMIT_INITIAL_PHRASE'
            return '', 200

    @app.route('/status', methods=['GET'])
    @cross_origin()
    def get_status_for_player():
        (username, gamecode) = require_request_data(request, 'get player status')
        if not username:
            return gamecode
        elif gamecode not in _games.keys():
            return err('No such game: "' + gamecode + '".')
        elif username in _games[gamecode]['userStatuses'].keys():
            return jsonify(get_user_status(username, gamecode)), 200
        else:
            return err('Unexplained error getting status')

    def get_user_status(username, gamecode):
        statusForUser = _games[gamecode]['userStatuses'][username]
        if (statusForUser == 'SUBMIT_IMAGE' or statusForUser == 'SUBMIT_PHRASE'):
            return {'description': statusForUser,
                    'prompt': getPhrasePrompt(username,
                                              gamecode) if statusForUser == 'SUBMIT_IMAGE' else getImagePrompt(
                        username, gamecode), 'previousPlayerUsername': getPreviousPlayer(username, gamecode),
                    'nextPlayerUsername': getNextPlayer(username, gamecode)}
        return {'description': statusForUser, 'previousPlayerUsername': getPreviousPlayer(username, gamecode),
                'nextPlayerUsername': getNextPlayer(username, gamecode)}

    @app.route('/phrase', methods=['POST'])
    @cross_origin()
    def submit_phrase():
        (username, gamecode) = require_request_data(request, 'submit phrase', inBody=True)
        if not username:
            return gamecode
        elif gamecode not in _games.keys():
            return err('No such game: "' + gamecode + '".')
        elif _games[gamecode]['userStatuses'][username] not in ["SUBMIT_INITIAL_PHRASE",
                                                                                            "SUBMIT_PHRASE"]:
            return err('Cannot submit phrase: it is not ' + request.json[
                'username'] + '\'s turn to submit a phrase.')
        if username in _games[gamecode]['userStatuses'].keys():
            savePhrase(username, gamecode, request.json['phrase'])
            set_user_status(username, gamecode, "WAIT")
            return '', 200
        return err('Unexplained error submitting phrase')

    @app.route('/image', methods=['POST'])
    @cross_origin()
    def submit_image():
        (username, gamecode) = require_request_data(request, 'submit image', inBody=True)
        if not username:
            return gamecode
        if gamecode not in _games.keys():
            return err('No such game: "' + gamecode + '".')
        elif _games[gamecode]['userStatuses'][username] != "SUBMIT_IMAGE":
            return err('Cannot submit image: it is not ' + username + '\'s turn to submit an image.')
        elif username in _games[gamecode]['userStatuses'].keys():
            saveImage(username, gamecode, request.json['image'])
            set_user_status(username, gamecode, 'WAIT')
            return '', 200
        return err('Unexplained error submitting image')

    def update_status_if_all_players_done(gamecode):
        if all(status == 'WAIT' for status in _games[gamecode]['userStatuses'].values()):
            next_status = 'SUBMIT_PHRASE' if len(_games[gamecode]['images']) >= len(
                _games[gamecode]['phrases']) else 'SUBMIT_IMAGE'
            if gameOver(gamecode):
                next_status = 'GAME_OVER'
            for user in _games[gamecode]['userStatuses'].keys():
                set_user_status(user, gamecode, next_status)

    def set_user_status(username, gamecode, new_status):
        _games[gamecode]['userStatuses'][username] = new_status
        update_status_if_all_players_done(gamecode)

    @app.route('/summary', methods=['GET'])
    @cross_origin()
    def summary():
        if not args_includes_game_code(request):
            return err('Cannot get summary without a game code.')
        elif request.args['game'] not in _games.keys():
            return err('No such game: "' + request.args['game'] + '".')
        else:
            status_summary = list()
            for user in _games[request.args['game']]['userStatuses'].keys():
                user_status = dict()
                user_status['username'] = user
                user_status['status'] = get_user_status(user, request.args['game'])
                status_summary.append(user_status)
            return jsonify(status_summary), 200

    @app.route('/results', methods=['GET'])
    @cross_origin()
    def get_results():
        if not args_includes_game_code(request):
            return err('Cannot get results without a game code.')
        elif request.args['game'] not in _games.keys():
            return err('Cannot get results.  No such game: "' + request.args['game'] + '".')
        elif gameOver(request.args['game']):
            return jsonify(getAllSubmissionThreadsByUser(request.args['game'])), 200
        else:
            return err('Cannot get results: game not over.')

    @app.route('/restart', methods=['POST'])
    @cross_origin()
    def restart_game():
        _games.clear()
        return '', 200

    def getAllSubmissionThreadsByUser(gamecode):
        toReturn = list()
        for username in _games[gamecode]['userStatuses'].keys():
            toReturn.append({"originator": username, "submissions": getUserSubmissionThread(username, gamecode)})
        return toReturn

    def getUserSubmissionThread(username, gamecode):
        users = list(_games[gamecode]['userStatuses'].keys())
        indexOfOriginalUser = users.index(username)
        toReturn = [_games[gamecode]['phrases'][username][0]]
        for i in range(1, len(users)):
            user = users[(indexOfOriginalUser + i) % len(users)]
            toReturn.append(
                _games[gamecode]['phrases'][user][int(i / 2)] if i % 2 == 0 else _games[gamecode]['images'][user][
                    int(i / 2)])
        return toReturn

    def savePhrase(username, gamecode, new_phrase):
        if (username not in _games[gamecode]['phrases'].keys()):
            _games[gamecode]['phrases'][username] = [new_phrase]
        else:
            _games[gamecode]['phrases'][username].append(new_phrase)

    def getPhrasePrompt(username, gamecode):
        users = list(_games[gamecode]['userStatuses'].keys())
        indexOfUser = users.index(username)
        usernameOfPhraseSource = users[(indexOfUser + 1) % len(users)]
        return _games[gamecode]['phrases'][usernameOfPhraseSource][-1]

    def saveImage(username, gamecode, new_image):
        if (username not in _games[gamecode]['images'].keys()):
            _games[gamecode]['images'][username] = [new_image]
        else:
            _games[gamecode]['images'][username].append(new_image)

    def getImagePrompt(username, gamecode):
        users = list(_games[gamecode]['userStatuses'].keys())
        indexOfUser = users.index(username)
        usernameOfImageSource = users[(indexOfUser + 1) % len(users)]
        return _games[gamecode]['images'][usernameOfImageSource][-1]

    def require_request_data(_request, forTask, variables=['username', 'game'], inBody=False):
        data = _request.json if inBody else _request.args
        for variable in variables:
            if (data is None or variable not in data.keys() or data[
                variable] == ''):
                return (False, err('Cannot ' + forTask + ': Missing ' + variable + '.'))
        return (data[variable] for variable in variables)

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

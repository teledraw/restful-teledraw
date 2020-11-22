import click
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin

_games = dict()


def game_over(game):
    number_of_users = len(_games[game]['userStatuses'].keys())
    for user in _games[game]['userStatuses'].keys():
        if user not in _games[game]['phrases'].keys() or user not in _games[game]['images'].keys() or len(
                _games[game]['phrases'][user]) + len(
            _games[game]['images'][user]) != number_of_users:
            return False
    return number_of_users > 0


def game_exists(game):
    return game in _games.keys()


def too_late_to_join(game):
    return game_exists(game) and not all(
        status == "SUBMIT_INITIAL_PHRASE" for status in list(_games[game]['userStatuses'].values()))


def get_next_player(username, gamecode):
    usernames = list(_games[gamecode]['userStatuses'].keys())
    return usernames[0] if usernames.index(username) == len(usernames) - 1 else usernames[usernames.index(username) + 1]


def get_previous_player(username, gamecode):
    usernames = list(_games[gamecode]['userStatuses'].keys())
    return usernames[len(usernames) - 1] if usernames.index(username) == 0 else usernames[usernames.index(username) - 1]


def create_game(game_code):
    _games[game_code] = {'userStatuses': dict(), 'phrases': dict(), 'images': dict()}


def update_status_if_all_players_done(gamecode):
    if all(status == 'WAIT' for status in _games[gamecode]['userStatuses'].values()):
        next_status = 'SUBMIT_PHRASE' if get_phase_number(gamecode) % 2 == 1 else 'SUBMIT_IMAGE'
        if game_over(gamecode):
            next_status = 'GAME_OVER'
        for user in _games[gamecode]['userStatuses'].keys():
            set_user_status(user, gamecode, next_status)


def set_user_status(username, gamecode, new_status):
    _games[gamecode]['userStatuses'][username] = new_status
    update_status_if_all_players_done(gamecode)


def get_all_submission_threads_by_user(gamecode):
    to_return = list()
    for username in _games[gamecode]['userStatuses'].keys():
        to_return.append({"originator": username, "submissions": get_user_submission_thread(username, gamecode)})
    return to_return


def get_user_submission_thread(username, gamecode):
    users = list(_games[gamecode]['userStatuses'].keys())
    index_of_original_user = users.index(username)
    to_return = [_games[gamecode]['phrases'][username][0]]
    for i in range(1, len(users)):
        user = users[(index_of_original_user + i) % len(users)]
        to_return.append(
            _games[gamecode]['phrases'][user][int(i / 2)] if i % 2 == 0 else _games[gamecode]['images'][user][
                int(i / 2)])
    return to_return


def save_phrase(username, gamecode, new_phrase):
    if (username not in _games[gamecode]['phrases'].keys()):
        _games[gamecode]['phrases'][username] = [new_phrase]
    else:
        _games[gamecode]['phrases'][username].append(new_phrase)


def get_phrase_prompt(username, gamecode):
    users = list(_games[gamecode]['userStatuses'].keys())
    username_of_phrase_source = get_previous_player(username, gamecode)
    return _games[gamecode]['phrases'][username_of_phrase_source][-1]


def save_image(username, gamecode, new_image):
    if (username not in _games[gamecode]['images'].keys()):
        _games[gamecode]['images'][username] = [new_image]
    else:
        _games[gamecode]['images'][username].append(new_image)


def get_image_prompt(username, gamecode):
    users = list(_games[gamecode]['userStatuses'].keys())
    username_of_image_source = get_previous_player(username, gamecode)
    return _games[gamecode]['images'][username_of_image_source][-1]

def get_phase_number(gamecode):
    current_number_of_players = len(_games[gamecode]['userStatuses'])
    if len(_games[gamecode]['phrases']) < current_number_of_players:
        return 1
    elif len(_games[gamecode]['images']) < current_number_of_players:
        return 2
    else:
        completed_phrase_rounds = len(_games[gamecode]['phrases'][min(_games[gamecode]['phrases'], key=len)])
        completed_image_rounds = len(_games[gamecode]['images'][min(_games[gamecode]['images'], key=len)])
        return 1 + completed_image_rounds + completed_phrase_rounds


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
        (username, gamecode) = require_request_data(request, 'join game', in_body=True)
        if not username:
            return gamecode
        elif too_late_to_join(gamecode):
            return err("Cannot join a game in progress.")
        else:
            if (gamecode not in _games.keys()):
                create_game(gamecode)
            _games[gamecode]['userStatuses'][username] = 'SUBMIT_INITIAL_PHRASE'
            return '', 200

    @app.route('/game/player/<path:username>', methods=['GET'])
    @cross_origin()
    def statusRequiresGameCode(username):
        return err('Cannot get player status for '+username+': missing game code.')

    @app.route('/game/<path:gamecode>/player', methods=['GET'])
    @cross_origin()
    def statusRequiresUsername(gamecode):
        return err('Cannot get player status: missing username.')

    @app.route('/game/<path:gamecode>/player/<path:username>', methods=['GET'])
    @cross_origin()
    def get_status_for_player(gamecode, username):
        if gamecode not in _games.keys():
            return err('No such game: "' + gamecode + '".')
        elif username in _games[gamecode]['userStatuses'].keys():
            return jsonify(get_user_status(username, gamecode)), 200
        else:
            return err('Unexplained error getting status')

    def get_user_status(username, gamecode, just_the_status=False):
        status_for_user = _games[gamecode]['userStatuses'][username]
        if(just_the_status):
            return {'description':status_for_user}
        elif (status_for_user == 'SUBMIT_IMAGE' or status_for_user == 'SUBMIT_PHRASE'):
            return {'description': status_for_user,
                    'prompt': get_phrase_prompt(username,
                                                gamecode) if status_for_user == 'SUBMIT_IMAGE' else get_image_prompt(
                        username, gamecode), 'previousPlayerUsername': get_previous_player(username, gamecode),
                    'nextPlayerUsername': get_next_player(username, gamecode)}
        return {'description': status_for_user, 'previousPlayerUsername': get_previous_player(username, gamecode),
                'nextPlayerUsername': get_next_player(username, gamecode)}

    @app.route('/phrase', methods=['POST'])
    @cross_origin()
    def submit_phrase():
        (username, gamecode) = require_request_data(request, 'submit phrase', in_body=True)
        if not username:
            return gamecode
        elif gamecode not in _games.keys():
            return err('No such game: "' + gamecode + '".')
        elif _games[gamecode]['userStatuses'][username] not in ["SUBMIT_INITIAL_PHRASE",
                                                                "SUBMIT_PHRASE"]:
            return err('Cannot submit phrase: it is not ' + request.json[
                'username'] + '\'s turn to submit a phrase.')
        if username in _games[gamecode]['userStatuses'].keys():
            save_phrase(username, gamecode, request.json['phrase'])
            set_user_status(username, gamecode, "WAIT")
            return '', 200
        return err('Unexplained error submitting phrase')

    @app.route('/image', methods=['POST'])
    @cross_origin()
    def submit_image():
        (username, gamecode) = require_request_data(request, 'submit image', in_body=True)
        if not username:
            return gamecode
        if gamecode not in _games.keys():
            return err('No such game: "' + gamecode + '".')
        elif _games[gamecode]['userStatuses'][username] != "SUBMIT_IMAGE":
            return err('Cannot submit image: it is not ' + username + '\'s turn to submit an image.')
        elif username in _games[gamecode]['userStatuses'].keys():
            save_image(username, gamecode, request.json['image'])
            set_user_status(username, gamecode, 'WAIT')
            return '', 200
        return err('Unexplained error submitting image')

    @app.route('/game', methods=['GET'])
    @cross_origin()
    def summaryRequiresGameCode():
        return err('Cannot get current summary: missing game code.')

    @app.route('/game/<path:game>', methods=['GET'])
    @cross_origin()
    def summary(game):
        gamecode = game
        if gamecode not in _games.keys():
            return err('No such game: "' + gamecode + '".')
        else:
            status_summary = dict()
            status_summary['canJoin'] = not too_late_to_join(gamecode)
            status_summary['phaseNumber'] = get_phase_number(gamecode)
            status_summary['players'] = []
            for user in _games[gamecode]['userStatuses'].keys():
                user_status = dict()
                user_status['username'] = user
                user_status['status'] = get_user_status(user, gamecode, just_the_status=True)
                status_summary['players'].append(user_status)
            return jsonify(status_summary), 200

    @app.route('/game/results', methods=['GET'])
    @cross_origin()
    def resultsRequiresGameCode():
        return err('Cannot get results: missing game code.')

    @app.route('/game/<path:game>/results', methods=['GET'])
    @cross_origin()
    def get_results(game):
        gamecode = game
        if gamecode not in _games.keys():
            return err('Cannot get results.  No such game: "' + gamecode + '".')
        elif game_over(gamecode):
            return jsonify(get_all_submission_threads_by_user(gamecode)), 200
        else:
            return err('Cannot get results: game not over.')

    @app.route('/restart', methods=['POST'])
    @cross_origin()
    def restart_game():
        _games.clear()
        return '', 200

    def require_request_data(_request, for_task, variables=['username', 'game'], in_body=False):
        data = _request.json if in_body else _request.args
        for variable in variables:
            if (data is None or variable not in data.keys() or data[
                variable] == ''):
                return (False, err('Cannot ' + for_task + ': Missing ' + variable + '.'))
        to_return = list(data[variable] for variable in variables)
        if len(to_return) < 2:
            to_return.append(False)
        return to_return

    def err(message, status_code=400):
        return jsonify({"error": message}), status_code

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

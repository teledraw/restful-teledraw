import click
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin

from app.Game import Game

_games = list()

def get_game_by_code(game_code):
    return next((game for game in _games if game.code == game_code), None)


def game_exists(gamecode):
    return any(game.code == gamecode for game in _games)


def create_game(game_code):
    _games.append(Game(game_code))


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
        elif game_exists(gamecode) and get_game_by_code(gamecode).too_late_to_join() and not get_game_by_code(gamecode).is_over():
            return err("Cannot join a game in progress.")
        else:
            if not game_exists(gamecode):
                create_game(gamecode)
            get_game_by_code(gamecode).join(username)
            return '', 200

    @app.route('/game/player/<path:username>', methods=['GET'])
    @cross_origin()
    def statusRequiresGameCode(username):
        return err('Cannot get player status for ' + username + ': missing game code.')


    @app.route('/game/<path:gamecode>/player', methods=['GET'])
    @cross_origin()
    def statusRequiresUsername(gamecode):
        return err('Cannot get player status: missing username.')


    @app.route('/game/<path:gamecode>/player/<path:username>', methods=['GET'])
    @cross_origin()
    def get_status_for_player(gamecode, username):
        if not game_exists(gamecode):
            return err('No such game: "' + gamecode + '".')
        else:
            game = get_game_by_code(gamecode)
            if game.has_player(username):
                return jsonify(game.get_user_status(username)), 200
            else:
                return err('Unexplained error getting status')


    @app.route('/phrase', methods=['POST'])
    @cross_origin()
    def submit_phrase():
        (username, gamecode) = require_request_data(request, 'submit phrase', in_body=True)
        if not username:
            return gamecode
        elif not game_exists(gamecode):
            return err('No such game: "' + gamecode + '".')
        else:
            game = get_game_by_code(gamecode)
            if not game.is_action_allowed(username, "submitphrase"):
                return err('Cannot submit phrase: it is not ' + request.json[
                    'username'] + '\'s turn to submit a phrase.')
            elif game.has_player(username):
                game.save_phrase(username, request.json['phrase'])
                return '', 200
            return err('Unexplained error submitting phrase')

    @app.route('/image', methods=['POST'])
    @cross_origin()
    def submit_image():
        (username, gamecode) = require_request_data(request, 'submit image', in_body=True)
        if not username:
            return gamecode
        if not game_exists(gamecode):
            return err('No such game: "' + gamecode + '".')
        else:
            game = get_game_by_code(gamecode)
            if not game.is_action_allowed(username, "submitimage"):
                return err('Cannot submit image: it is not ' + username + '\'s turn to submit an image.')
            elif game.has_player(username):
                game.save_image(username, request.json['image'])
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
        if not game_exists(gamecode):
            return err('No such game: "' + gamecode + '".')
        else:
            game = get_game_by_code(gamecode)
            status_summary = dict()
            status_summary['canJoin'] = not game.too_late_to_join()
            status_summary['canStart'] = not game.too_early_to_start() and game.get_phase_number() < 2
            status_summary['phaseNumber'] = game.get_phase_number()
            status_summary['players'] = []
            for user in game.get_playernames():
                user_status = dict()
                user_status['username'] = user
                user_status['status'] = game.get_user_status(user, just_the_status=True)
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
        if not game_exists(gamecode):
            return err('Cannot get results.  No such game: "' + gamecode + '".')
        else:
            game = get_game_by_code(gamecode)
            if game.is_over():
                return jsonify(game.get_all_submission_threads_indexed_by_user()), 200
            else:
                return err('Cannot get results: game not over.')

    @app.route('/restart', methods=['POST'])
    @cross_origin()
    def clear_all():
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

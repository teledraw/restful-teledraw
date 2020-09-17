import click
from flask import Flask
from flask import request


_users = list()

def create_app():
    app = Flask(__name__)

    # a simple response that says hello
    @app.route('/')
    def hello_world():
        return 'Hello World!'

    @app.route('/join', methods=['POST'])
    def join_game():
        if checkUsernameExists(request):
            _users.append(request.form.get('username'))
            return '', 200
        return '', 400


    @app.route('/status', methods=['GET'])
    def get_status_for_player():
        if request.args['username'] in _users:
            return "SUBMIT_INITIAL_PHRASE", 200
        return '', 400


    def checkUsernameExists(_request):
        return (_request.form.get('username') is not None and _request.form.get('username') != '')


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

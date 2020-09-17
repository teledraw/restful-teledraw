import click
from flask import Flask
from flask import request


def create_app():
    app = Flask(__name__)

    # a simple response that says hello
    @app.route('/')
    def hello_world():
        return 'Hello World!'

    @app.route('/join', methods=['POST'])
    def join_game():
        if checkUsernameExists(request):
            return '', 200
        return '', 400


    def checkUsernameExists(_request):
        return (_request.form.get('name') is not None and _request.form.get('name') != '')


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

import unittest
from flask import current_app


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        # creates a test client
        self.app = current_app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_helloWorldEndpoint(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello World!')

    def test_canJoinByPostingUsername(self):
        response = self.app.post('/join', data={'username': 'Mikey'})
        self.assertEqual(response.status_code, 200)

    def test_canJoinByPostingUsername(self):
        response = self.app.get('/join')
        self.assertEqual(response.status_code, 405)

    def test_cannotJoinWithoutAUsername(self):
        response = self.app.post('/join', data={'username': ''})
        self.assertEqual(response.status_code, 400)

    def test_canJoinAndAskGameForNextStep(self):
        self.app.post('/join', data={'username': 'Mikey'})
        response = self.app.get('/status?username=Mikey')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"SUBMIT_INITIAL_PHRASE")

    ##Error case test
    #def test_getNextStepSays400IfYouHaveNotJoined(self):
    #    response = self.app.get('/status?username=Mikey')
    #    self.assertEqual(response.status_code, 400)


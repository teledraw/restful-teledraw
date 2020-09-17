import unittest
from flask import current_app


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        # creates a test client
        self.app = current_app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def assertStatusDescription(self, statusCode=200, statusMessage="", username=""):
       response = self.app.get('/status?username=' + username)
       self.assertEqual(response.status_code, statusCode)
       self.assertEqual(response.get_json()['description'], statusMessage)

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
        self.assertStatusDescription(200, "SUBMIT_INITIAL_PHRASE", "Mikey")

    ##Error case test
    # def test_getNextStepSays400IfYouHaveNotJoined(self):
    #    response = self.app.get('/status?username=Mikey')
    #    self.assertEqual(response.status_code, 400)

    def test_canPostInitialPhrase(self):
        self.app.post('/join', data={'username': 'Mikey'})
        self.app.post('/join', data={'username': 'NotMikey'})
        response = self.app.post('/phrase', data={'username': 'Mikey',
                                                  'phrase': 'Ever dance with the devil in the pale moonlight?'})
        self.assertEqual(response.status_code, 200)
        self.assertStatusDescription(200, "WAIT", "Mikey")

    def test_promptForImageAfterAllPlayersSubmitInitialPhrase(self):
        self.app.post('/join', data={'username': 'Mikey'})
        self.app.post('/join', data={'username': 'NotMikey'})
        self.app.post('/phrase', data={'username': 'Mikey',
                                                  'phrase': 'Ever dance with the devil in the pale moonlight?'})
        self.app.post('/phrase', data={'username': 'NotMikey',
                                                  'phrase': 'The devil went down to Georgia.'})

        self.assertStatusDescription(200, "SUBMIT_IMAGE", "Mikey")
        self.assertStatusDescription(200, "SUBMIT_IMAGE", "NotMikey")

    def test_imagePromptsIncludeProperPhrase(self):
        self.app.post('/join', data={'username': 'Mikey'})
        self.app.post('/join', data={'username': 'NotMikey'})
        self.app.post('/phrase', data={'username': 'Mikey',
                                                  'phrase': 'Ever dance with the devil in the pale moonlight?'})
        self.app.post('/phrase', data={'username': 'NotMikey',
                                                  'phrase': 'The devil went down to Georgia.'})

        response = self.app.get('/status?username=' + 'Mikey')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['description'], "SUBMIT_IMAGE")
        self.assertEqual(response.get_json()['prompt'], 'The devil went down to Georgia.')

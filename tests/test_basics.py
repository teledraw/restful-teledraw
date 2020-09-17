import unittest
from flask import current_app


class MikeyNotMikeyTestCase(unittest.TestCase):
    def setUp(self):
        # creates a test client
        self.app = current_app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True
        self.app.post("/restart")

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

    def test_cannotJoinWithoutUsername(self):
        response = self.app.get('/join')
        self.assertEqual(response.status_code, 405)

    def test_canEraseTheGame(self):
        response = self.app.post('/join', data={'username': 'Mikey'})
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/restart')
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/status?username=Mikey')
        self.assertEqual(response.status_code, 400)


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
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()

        response = self.app.get('/status?username=' + 'Kirk')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['description'], "SUBMIT_IMAGE")
        self.assertEqual(response.get_json()['prompt'], 'The devil went down to Georgia.')

    def test_phrasePromptsIncludeProperImage(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkBonesAndSpock()
        self.addImagesForKirkBonesAndSpock()

        response = self.app.get('/status?username=' + 'Kirk')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['description'], "SUBMIT_PHRASE")
        self.assertEqual(response.get_json()['prompt'], 'spock image')

    def test_statusIsGameOverAfterOneSubmissionPerPlayer(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.addImagesForKirkAndSpock()


        response = self.app.get('/status?username=' + 'Kirk')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['description'], 'GAME_OVER')




    def addKirkAndSpock(self):
        self.app.post('/join', data={'username': 'Kirk'})
        self.app.post('/join', data={'username': 'Spock'})

    def addKirkBonesAndSpock(self):
        self.addKirkAndSpock()
        self.app.post('/join', data={'username': 'Bones'})

    def addPhrasesForKirkAndSpock(self):
        self.app.post('/phrase', data={'username': 'Kirk',
                                       'phrase': 'Ever dance with the devil in the pale moonlight?'})
        self.app.post('/phrase', data={'username': 'Spock',
                                       'phrase': 'The devil went down to Georgia.'})

    def addPhrasesForKirkBonesAndSpock(self):
        self.addPhrasesForKirkAndSpock()
        self.app.post('/phrase', data={'username': 'Bones',
                                       'phrase': 'That is devilishly clever.'})

    def addImagesForKirkAndSpock(self):
        self.app.post('/image', data={'username': 'Kirk',
                                       'image': 'kirk image'})
        self.app.post('/image', data={'username': 'Spock',
                                       'image': 'spock image'})

    def addImagesForKirkBonesAndSpock(self):
        self.addImagesForKirkAndSpock()
        self.app.post('/image', data={'username': 'Bones',
                                      'image': 'bones image'})

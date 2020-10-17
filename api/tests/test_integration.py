import unittest
from flask import current_app


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        # creates a test client
        self.app = current_app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True
        self.app.post("/restart")

    def tearDown(self):
        pass

    def assertPlayerStatus(self, statusCode=200, statusMessage="", username="", game="NCC-1701D", prompt="",
                           playerBefore="", playerAfter=""):
        response = self.app.get('/status?username=' + username + '&game=' + game)
        self.assertEqual(response.status_code, statusCode)
        if (statusMessage):
            self.assertEqual(response.get_json()['description'], statusMessage)
        if (prompt):
            self.assertEqual(response.get_json()['prompt'], prompt)
        if (playerBefore):
            self.assertEqual(response.get_json()['previousPlayerUsername'], playerBefore)
        if (playerAfter):
            self.assertEqual(response.get_json()['nextPlayerUsername'], playerAfter)

    def post_image(self, username="", image="", game="NCC-1701D"):
        return self.app.post('/image', json={'username': username, 'image': image, 'game': game})

    def get_results(self, game="NCC-1701D"):
        if game:
            return self.app.get("/results?game="+game)
        else:
            return self.app.get("/results")

    def assertResultsError(self, error, game="NCC-1701D", statusCode=400):
        response = self.get_results(game)
        self.assertEqual(response.status_code, statusCode)
        self.assertEqual(response.get_json()['error'], error)

    def assertPostImageError(self, username="", image="", game="", error="", status_code=400):
        response = self.post_image(username, image, game)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get_json()['error'],
                         error)

    def post_phrase(self, username="", phrase="", game="NCC-1701D"):
        return self.app.post('/phrase', json={'username': username, 'phrase': phrase, 'game': game})

    def assertPostPhraseError(self, username="", phrase="", game="", error="", status_code=400):
        response = self.post_phrase(username, phrase, game)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get_json()['error'], error)

    def assertStatusError(self, errorMessage="", username="", game=""):
        response = self.app.get('/status?username=' + username + '&game=' + game)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], errorMessage)

    def test_helloWorldEndpoint(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'This is the Arktika API base URL.  Please add an endpoint '
                                                        'name to your request to get started.')

    def test_canJoinByPostingUsernameAndGameCode(self):
        response = self.app.post('/join', json={'username': 'Mikey', 'game': 'gamey'})
        self.assertEqual(response.status_code, 200)

    def test_cannotJoinWithoutAPostBody(self):
        response = self.app.get('/join')
        self.assertEqual(response.status_code, 405)

    def test_canEraseTheGame(self):
        response = self.app.post('/join', json={'username': 'Mikey', 'game': 'gamey'})
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/restart')
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/status?username=Mikey&game=gamey')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json and 'error' in response.json.keys())
        self.assertEqual(response.json['error'], 'No such game: "gamey".')

    def test_cannotJoinWithoutAUsername(self):
        response = self.app.post('/join', json={'game': 'XYZORG'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot join without a username.")

    def test_cannotJoinWithoutPostingAGameName(self):
        response = self.app.post('/join', json={'username': 'Jimmy'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot join without a game code.")

    def test_cannotGetStatusWithoutAUsername(self):
        self.addKirkAndSpock()
        self.assertStatusError(errorMessage="Cannot get status without a username.", username="")

    def test_cannotGetStatusWithoutAGameName(self):
        self.addKirkAndSpock()
        self.assertStatusError(errorMessage="Cannot get status without a game code.", username="Kirk")

    def test_canJoinAndAskGameForNextStep(self):
        self.addKirkAndSpock()
        self.assertPlayerStatus(200, "SUBMIT_INITIAL_PHRASE", "Kirk")

    def test_getNextStepSays400IfYouHaveNotJoined(self):
        response = self.app.get('/status?username=Mikey')
        self.assertEqual(response.status_code, 400)

    def test_statusEndpointCorrectlyIdentifiesPlayersBeforeAndAfterYou_2player(self):
        self.addKirkAndSpock()
        self.assertPlayerStatus(username="Kirk", playerBefore="Spock", playerAfter="Spock")
        self.assertPlayerStatus(username="Spock", playerBefore="Kirk", playerAfter="Kirk")

    def test_statusEndpointCorrectlyIdentifiesPlayersBeforeAndAfterYou_3player(self):
        self.addKirkBonesAndSpock()
        self.assertPlayerStatus(username="Kirk", playerBefore="Bones", playerAfter="Spock")
        self.assertPlayerStatus(username="Spock", playerBefore="Kirk", playerAfter="Bones")
        self.assertPlayerStatus(username="Bones", playerBefore="Spock", playerAfter="Kirk")

    def test_summaryEndpointCanSummarizeAtGameStart(self):
        self.addKirkBonesAndSpock()
        response = self.app.get('/summary?game=NCC-1701D')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['username'], "Kirk")
        self.assertEqual(response.json[1]['username'], "Spock")
        self.assertEqual(response.json[2]['username'], "Bones")
        self.assertEqual(response.json[0]['status']['description'], "SUBMIT_INITIAL_PHRASE")
        self.assertEqual(response.json[1]['status']['description'], "SUBMIT_INITIAL_PHRASE")
        self.assertEqual(response.json[2]['status']['description'], "SUBMIT_INITIAL_PHRASE")

    def test_summaryRequiresGameName(self):
        self.addKirkBonesAndSpock()
        response = self.app.get('/summary')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot get summary without a game code.")

    def test_summaryWarnsOfInvalidGameName(self):
        self.addKirkBonesAndSpock()
        response = self.app.get('/summary?game=NCC-1701C')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], 'No such game: "NCC-1701C".')

    def test_canPostInitialPhrase(self):
        self.addKirkAndSpock()
        response = self.post_phrase("Kirk", 'Ever dance with the devil in the pale moonlight?')
        self.assertEqual(response.status_code, 200)
        self.assertPlayerStatus(200, "WAIT", "Kirk")

    def test_promptForImageAfterAllPlayersSubmitInitialPhrase(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertPlayerStatus(200, "SUBMIT_IMAGE", "Kirk")
        self.assertPlayerStatus(200, "SUBMIT_IMAGE", "Spock")

    def test_cannotJoinAfterAllPlayersSubmitInitialPhrase(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        response = self.app.post('/join', json={'username': 'Mikey', 'game': 'NCC-1701D'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot join a game in progress.")

    def test_imagePromptsIncludeProperPhrase(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertPlayerStatus(200, "SUBMIT_IMAGE", "Kirk", prompt='The devil went down to Georgia.')

    def test_cannotSubmitPhraseWhenItIsImageTime(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        response = self.post_phrase("Spock", 'The devil is in the details.')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'],
                         "Cannot submit phrase: it is not Spock's turn to submit a phrase.")

    def test_cannotSubmitPhraseWithoutAUsername(self):
        self.addKirkAndSpock()
        response = self.app.post('/phrase', json={'username': '', 'phrase': 'The devil is in the details.'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'],
                         "Cannot submit phrase without a username.")

    def test_cannotSubmitImageWhenItIsPhraseTime(self):
        self.addKirkAndSpock()
        response = self.post_image("Spock", "spock image")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'],
                         "Cannot submit image: it is not Spock's turn to submit an image.")

    def test_cannotSubmitImageWithoutUsername(self):
        self.addKirkAndSpock()
        response = self.app.post('/image', json={'username': '',
                                                 'image': 'spock image'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'],
                         "Cannot submit image without a username.")

    def test_cannotSubmitPhraseWithoutGameName(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertPostPhraseError("Kirk", "roll the dice", error="Cannot submit phrase without a game code.")

    def test_cannotSubmitImageWithoutGameName(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertPostImageError("Kirk", "pix", error="Cannot submit image without a game code.")

    def test_submitImageWarnsOfInvalidGameName(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertPostImageError("Kirk", "an image", "NCC-1701C", 'No such game: "NCC-1701C".')

    def test_submitPhraseWarnsOfInvalidGameName(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertPostPhraseError("Kirk", "the devils of our nature", "NCC-1701C", 'No such game: "NCC-1701C".')

    def test_phrasePromptsIncludeProperImage(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkBonesAndSpock()
        self.addImagesForKirkBonesAndSpock()

        self.assertPlayerStatus(200, "SUBMIT_PHRASE", "Kirk", prompt='spock image')

    def test_statusIsGameOverForEveryoneAfterOneSubmissionPerPlayer(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.addImagesForKirkAndSpock()
        self.assertPlayerStatus(200, "GAME_OVER", "Kirk")
        self.assertPlayerStatus(200, "GAME_OVER", "Spock")

    def test_cannotGetResultsPriorToGameBeingOver(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertResultsError('Cannot get results: game not over.')

    def test_cannotGetResultsWithoutGameCode(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.addImagesForKirkAndSpock()
        self.assertResultsError('Cannot get results without a game code.', '')

    def test_cannotGetResultsWithoutValidGameCode(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.addImagesForKirkAndSpock()
        self.assertResultsError('Cannot get results.  No such game: "NCC-1701C".', 'NCC-1701C')

    def test_canGetResultsAfterCompletedTwoPlayerGame(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.addImagesForKirkAndSpock()
        response = self.get_results()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]['originator'], "Kirk")
        self.assertEqual(response.get_json()[0]['submissions'][0], "Ever dance with the devil in the pale moonlight?")
        self.assertEqual(response.get_json()[0]['submissions'][1], "spock image")

        self.assertEqual(response.get_json()[1]['originator'], "Spock")
        self.assertEqual(response.get_json()[1]['submissions'][0], "The devil went down to Georgia.")
        self.assertEqual(response.get_json()[1]['submissions'][1], "kirk image")

    def test_canGetResultsAfterCompletedThreePlayerGame(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkBonesAndSpock()
        self.addImagesForKirkBonesAndSpock()
        self.addSecondPhrasesForKirkBonesAndSpock()
        response = self.get_results()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]['originator'], "Kirk")
        self.assertEqual(response.get_json()[0]['submissions'][0], "Ever dance with the devil in the pale moonlight?")
        self.assertEqual(response.get_json()[0]['submissions'][1], "spock image")
        self.assertEqual(response.get_json()[0]['submissions'][2], "What the devil does that mean?")

        self.assertEqual(response.get_json()[1]['originator'], "Spock")
        self.assertEqual(response.get_json()[1]['submissions'][0], "The devil went down to Georgia.")
        self.assertEqual(response.get_json()[1]['submissions'][1], "bones image")
        self.assertEqual(response.get_json()[1]['submissions'][2], "The devil's drink!")

        self.assertEqual(response.get_json()[2]['originator'], "Bones")
        self.assertEqual(response.get_json()[2]['submissions'][0], "That is devilishly clever.")
        self.assertEqual(response.get_json()[2]['submissions'][1], "kirk image")
        self.assertEqual(response.get_json()[2]['submissions'][2], "The devil is in the details.")

    def test_canGetResultsAfterACompletedThreePlayerGame_DifferentSubmissionOrder(self):
        self.addKirkBonesAndSpock()

        self.post_phrase('Kirk', 'Ever dance with the devil in the pale moonlight?')
        self.post_phrase('Spock', 'The devil went down to Georgia.')
        self.post_phrase('Bones', 'That is devilishly clever.')
        self.post_image("Kirk", "kirk image")
        self.post_image("Spock", "spock image")
        self.post_image("Bones", "bones image")

        self.addSecondPhrasesForKirkBonesAndSpock()
        response = self.get_results()
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]['originator'], "Kirk")
        self.assertEqual(response.get_json()[0]['submissions'][0],
                         "Ever dance with the devil in the pale moonlight?")
        self.assertEqual(response.get_json()[0]['submissions'][1], "spock image")
        self.assertEqual(response.get_json()[0]['submissions'][2], "What the devil does that mean?")
        self.assertEqual(response.get_json()[1]['originator'], "Spock")
        self.assertEqual(response.get_json()[1]['submissions'][0], "The devil went down to Georgia.")
        self.assertEqual(response.get_json()[1]['submissions'][1], "bones image")
        self.assertEqual(response.get_json()[1]['submissions'][2], "The devil's drink!")
        self.assertEqual(response.get_json()[2]['originator'], "Bones")
        self.assertEqual(response.get_json()[2]['submissions'][0], "That is devilishly clever.")
        self.assertEqual(response.get_json()[2]['submissions'][1], "kirk image")
        self.assertEqual(response.get_json()[2]['submissions'][2], "The devil is in the details.")

    def addKirkAndSpock(self):
        self.app.post('/join', json={'username': 'Kirk', 'game': 'NCC-1701D'})
        self.app.post('/join', json={'username': 'Spock', 'game': 'NCC-1701D'})

    def addKirkBonesAndSpock(self):
        self.addKirkAndSpock()
        self.app.post('/join', json={'username': 'Bones', 'game': 'NCC-1701D'})

    def addPhrasesForKirkAndSpock(self):
        self.post_phrase('Kirk', 'Ever dance with the devil in the pale moonlight?')
        self.post_phrase('Spock', 'The devil went down to Georgia.')

    def addPhrasesForKirkBonesAndSpock(self):
        self.addPhrasesForKirkAndSpock()
        self.post_phrase('Bones', 'That is devilishly clever.')

    def addSecondPhrasesForKirkBonesAndSpock(self):
        self.post_phrase('Spock', 'The devil is in the details.')
        self.post_phrase('Bones', 'What the devil does that mean?')
        self.post_phrase('Kirk', 'The devil\'s drink!')

    def addImagesForKirkAndSpock(self):
        self.post_image("Kirk", "kirk image")
        self.post_image("Spock", "spock image")

    def addImagesForKirkBonesAndSpock(self):
        self.addImagesForKirkAndSpock()
        self.post_image("Bones", "bones image")

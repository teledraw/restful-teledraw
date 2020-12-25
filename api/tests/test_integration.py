import unittest
from flask import current_app

from app import db

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        # creates a test client
        self.app = current_app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True
        self.app.post("/restart")

        db.create_all()

    def tearDown(self):
        pass

    def assertPlayerStatus(self, statusMessage="", username="", game="NCC-1701", prompt="", playerBefore="",
                           playerAfter="", statusCode=200):
        response = self.app.get('/game/'+game+'/player/'+username)
        self.assertEqual(response.status_code, statusCode)
        if (statusMessage):
            self.assertEqual(response.get_json()['description'], statusMessage)
        if (prompt):
            self.assertEqual(response.get_json()['prompt'], prompt)
        if (playerBefore):
            self.assertEqual(response.get_json()['previousPlayerUsername'], playerBefore)
        if (playerAfter):
            self.assertEqual(response.get_json()['nextPlayerUsername'], playerAfter)

    def post_image(self, username="", image="", game="NCC-1701"):
        return self.app.post('/image', json={'username': username, 'image': image, 'game': game})

    def get_results(self, game="NCC-1701"):
        if game:
            return self.app.get("/game/" + game + "/results")
        else:
            return self.app.get("/game/results")

    def assertResultsError(self, error, game="NCC-1701", statusCode=400):
        response = self.get_results(game)
        self.assertEqual(response.status_code, statusCode)
        self.assertEqual(response.get_json()['error'], error)

    def assertPostImageError(self, username="", image="", game="", error="", status_code=400):
        response = self.post_image(username, image, game)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get_json()['error'],
                         error)

    def post_phrase(self, username="", phrase="", game="NCC-1701"):
        return self.app.post('/phrase', json={'username': username, 'phrase': phrase, 'game': game})

    def assertPostPhraseError(self, username="", phrase="", game="", error="", status_code=400):
        response = self.post_phrase(username, phrase, game)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get_json()['error'], error)

    def assertStatusError(self, errorMessage="", username="", game=""):
        url = ('/game/' + ((game + '/') if len(game) > 0 else "")) + ('player' + (('/' + username) if len(username) > 0 else ""))
        response = self.app.get(url)
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
        response = self.app.get('/game/gamey/player/Mikey')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json and 'error' in response.json.keys())
        self.assertEqual(response.json['error'], 'No such game: "gamey".')

    def test_cannotJoinWithoutAUsername(self):
        response = self.app.post('/join', json={'game': 'XYZORG'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot join game: Missing username.")

    def test_cannotJoinWithoutPostingAGameName(self):
        response = self.app.post('/join', json={'username': 'Jimmy'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot join game: Missing game.")

    def test_cannotGetStatusWithoutAUsername(self):
        self.addKirkAndSpock()
        self.assertStatusError(errorMessage="Cannot get player status: missing username.", username="", game="NCC-1701")

    def test_cannotGetStatusWithoutAGameName(self):
        self.addKirkAndSpock()
        self.assertStatusError(errorMessage="Cannot get player status for Kirk: missing game code.", username="Kirk")

    def test_canJoinAndAskGameForNextStep(self):
        self.addKirkAndSpock()
        self.assertPlayerStatus("SUBMIT_INITIAL_PHRASE", "Kirk")

    def test_getNextStepSays400IfYouHaveNotJoined(self):
        self.assertStatusError('No such game: "abc".', "Mikey", "abc")

    def test_statusEndpointCorrectlyIdentifiesPlayersBeforeAndAfterYou_2player(self):
        self.addKirkAndSpock()
        self.assertPlayerStatus(username="Kirk", playerBefore="Spock", playerAfter="Spock")
        self.assertPlayerStatus(username="Spock", playerBefore="Kirk", playerAfter="Kirk")

    def test_statusEndpointCorrectlyIdentifiesPlayersBeforeAndAfterYou_3player(self):
        self.addKirkBonesAndSpock()
        self.assertPlayerStatus(username="Kirk", playerBefore="Bones", playerAfter="Spock")
        self.assertPlayerStatus(username="Spock", playerBefore="Kirk", playerAfter="Bones")
        self.assertPlayerStatus(username="Bones", playerBefore="Spock", playerAfter="Kirk")

    def test_statusEndpointCorrectlyIdentifiesPlayersBeforeAndAfterYou_5player(self):
        self.addKirkBonesAndSpock()
        self.add_obrien_and_worf(game='NCC-1701')
        self.assertPlayerStatus(username="Kirk", playerBefore="Worf", playerAfter="Spock")
        self.assertPlayerStatus(username="Spock", playerBefore="Kirk", playerAfter="Bones")
        self.assertPlayerStatus(username="Bones", playerBefore="Spock", playerAfter="Obrien")
        self.assertPlayerStatus(username="Obrien", playerBefore="Bones", playerAfter="Worf")
        self.assertPlayerStatus(username="Worf", playerBefore="Obrien", playerAfter="Kirk")

    def test_summaryEndpointCanSummarizeAtGameStart(self):
        self.addKirkBonesAndSpock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['players'][0]['username'], "Kirk")
        self.assertEqual(response.json['players'][0]['username'], "Kirk")
        self.assertEqual(response.json['players'][0]['username'], "Kirk")
        self.assertEqual(response.json['players'][1]['username'], "Spock")
        self.assertEqual(response.json['players'][2]['username'], "Bones")
        self.assertEqual(response.json['players'][0]['status']['description'], "SUBMIT_INITIAL_PHRASE")
        self.assertEqual(response.json['players'][1]['status']['description'], "SUBMIT_INITIAL_PHRASE")
        self.assertEqual(response.json['players'][2]['status']['description'], "SUBMIT_INITIAL_PHRASE")

    def test_summaryEndpointCanSummarizeMidRound(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkBonesAndSpock()
        self.post_image("Kirk", "kirk image")
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['players'][0]['username'], "Kirk")
        self.assertEqual(response.json['players'][1]['username'], "Spock")
        self.assertEqual(response.json['players'][2]['username'], "Bones")
        self.assertEqual(response.json['players'][0]['status']['description'], "WAIT")
        self.assertEqual(response.json['players'][1]['status']['description'], "SUBMIT_IMAGE")
        self.assertEqual(response.json['players'][2]['status']['description'], "SUBMIT_IMAGE")
        self.assertEqual(response.json['phaseNumber'], 2)
        self.assertEqual(response.json['isOver'], False)

    def test_summaryEndpointCanSummarizeAtGameEnd(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkBonesAndSpock()
        self.addImagesForKirkBonesAndSpock()
        self.add_second_phrases_for_kirk_bones_and_spock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['players'][0]['username'], "Kirk")
        self.assertEqual(response.json['players'][1]['username'], "Spock")
        self.assertEqual(response.json['players'][2]['username'], "Bones")
        self.assertEqual(response.json['players'][0]['status']['description'], "GAME_OVER")
        self.assertEqual(response.json['players'][1]['status']['description'], "GAME_OVER")
        self.assertEqual(response.json['players'][2]['status']['description'], "GAME_OVER")
        self.assertEqual(response.json['phaseNumber'], 4)
        self.assertEqual(response.json['isOver'], True)

    def test_summaryIncludesOnlyStatusDescriptionsNotFullStatuses(self):
        self.addKirkBonesAndSpock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.json['players'][0]['status'].keys()), ['description'])

    def test_summaryReportsJoinableGamePositivelyAtStart(self):
        self.addKirkBonesAndSpock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canJoin'], True)

    def test_summaryReportsOnePersonIsNotEnoughToStart(self):
        response = self.app.post('/join', json={'username': 'Kirk', 'game': 'NCC-1701'})
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canStart'], False)

    def test_summaryReportsTwoPeopleIsEnoughToStart(self):
        self.addKirkBonesAndSpock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canStart'], True)

    def test_summary_aStartedGameGannotStart(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkBonesAndSpock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canStart'], False)

    def test_summaryReportsJoinableGameNegativelyAfterPhaseOne(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkBonesAndSpock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canJoin'], False)
        self.assertEqual(response.json['phaseNumber'], 2)

    def test_summaryRequiresGameName(self):
        self.addKirkBonesAndSpock()
        response = self.app.get('/game')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot get current summary: missing game code.")

    def test_summaryWarnsOfInvalidGameName(self):
        self.addKirkBonesAndSpock()
        response = self.app.get('/game/NCC-1701C')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], 'No such game: "NCC-1701C".')

    def test_canPostInitialPhrase(self):
        self.addKirkAndSpock()
        response = self.post_phrase("Kirk", 'Ever dance with the devil in the pale moonlight?')
        self.assertEqual(response.status_code, 200)
        self.assertPlayerStatus("WAIT", "Kirk")

    def test_promptForImageAfterAllPlayersSubmitInitialPhrase(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertPlayerStatus("SUBMIT_IMAGE", "Kirk")
        self.assertPlayerStatus("SUBMIT_IMAGE", "Spock")

    def test_cannotJoinAfterAllPlayersSubmitInitialPhrase(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        response = self.app.post('/join', json={'username': 'Mikey', 'game': 'NCC-1701'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot join a game in progress.")

    def test_canJoinAgainAfterGameOver(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.addImagesForKirkAndSpock()
        response = self.app.post('/join', json={'username': 'Mikey', 'game': 'NCC-1701'})
        self.assertEqual(response.status_code, 200)

    def test_imagePromptsIncludeProperPhrase(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkBonesAndSpock()
        self.assertPlayerStatus("SUBMIT_IMAGE", "Kirk", prompt='That is devilishly clever.', statusCode=200)
        self.assertPlayerStatus("SUBMIT_IMAGE", "Spock", prompt='Ever dance with the devil in the pale moonlight?', statusCode=200)
        self.assertPlayerStatus("SUBMIT_IMAGE", "Bones", prompt='The devil went down to Georgia.', statusCode=200)

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
                         "Cannot submit phrase: Missing username.")

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
                         "Cannot submit image: Missing username.")

    def test_cannotSubmitPhraseWithoutGameName(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertPostPhraseError("Kirk", "roll the dice", error="Cannot submit phrase: Missing game.")

    def test_cannotSubmitImageWithoutGameName(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertPostImageError("Kirk", "pix", error="Cannot submit image: Missing game.")

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

        self.assertPlayerStatus("SUBMIT_PHRASE", "Kirk", prompt='bones image')

    def test_statusIsGameOverForEveryoneAfterOneSubmissionPerPlayer(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.addImagesForKirkAndSpock()
        self.assertPlayerStatus("GAME_OVER", "Kirk")
        self.assertPlayerStatus("GAME_OVER", "Spock")

    def test_cannotGetResultsPriorToGameBeingOver(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.assertResultsError('Cannot get results: game not over.')

    def test_cannotGetResultsWithoutGameCode(self):
        self.addKirkAndSpock()
        self.addPhrasesForKirkAndSpock()
        self.addImagesForKirkAndSpock()
        self.assertResultsError('Cannot get results: missing game code.', '')

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
        self.add_second_phrases_for_kirk_bones_and_spock()
        response = self.get_results()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]['originator'], "Kirk")
        self.assertEqual(response.get_json()[0]['submissions'][0], "Ever dance with the devil in the pale moonlight?")
        self.assertEqual(response.get_json()[0]['submissions'][1], "spock image")
        self.assertEqual(response.get_json()[0]['submissions'][2], "Bones phrase 2")

        self.assertEqual(response.get_json()[1]['originator'], "Spock")
        self.assertEqual(response.get_json()[1]['submissions'][0], "The devil went down to Georgia.")
        self.assertEqual(response.get_json()[1]['submissions'][1], "bones image")
        self.assertEqual(response.get_json()[1]['submissions'][2], "Kirk phrase 2")

        self.assertEqual(response.get_json()[2]['originator'], "Bones")
        self.assertEqual(response.get_json()[2]['submissions'][0], "That is devilishly clever.")
        self.assertEqual(response.get_json()[2]['submissions'][1], "kirk image")
        self.assertEqual(response.get_json()[2]['submissions'][2], "Spock phrase 2")

    def test_canGetResultsAfterACompletedThreePlayerGame_DifferentSubmissionOrder(self):
        self.addKirkBonesAndSpock()

        self.post_phrase('Kirk', 'Ever dance with the devil in the pale moonlight?')
        self.post_phrase('Spock', 'The devil went down to Georgia.')
        self.post_phrase('Bones', 'That is devilishly clever.')
        self.post_image("Kirk", "kirk image")
        self.post_image("Spock", "spock image")
        self.post_image("Bones", "bones image")

        self.add_second_phrases_for_kirk_bones_and_spock()
        response = self.get_results()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]['originator'], "Kirk")
        self.assertEqual(response.get_json()[0]['submissions'][0],
                         "Ever dance with the devil in the pale moonlight?")
        self.assertEqual(response.get_json()[0]['submissions'][1], "spock image")
        self.assertEqual(response.get_json()[0]['submissions'][2], "Bones phrase 2")
        self.assertEqual(response.get_json()[1]['originator'], "Spock")
        self.assertEqual(response.get_json()[1]['submissions'][0], "The devil went down to Georgia.")
        self.assertEqual(response.get_json()[1]['submissions'][1], "bones image")
        self.assertEqual(response.get_json()[1]['submissions'][2], "Kirk phrase 2")
        self.assertEqual(response.get_json()[2]['originator'], "Bones")
        self.assertEqual(response.get_json()[2]['submissions'][0], "That is devilishly clever.")
        self.assertEqual(response.get_json()[2]['submissions'][1], "kirk image")
        self.assertEqual(response.get_json()[2]['submissions'][2], "Spock phrase 2")

    def test_threePlayerGameInWhichPhrasesAreCorrectlyGuessed(self):
        self.addKirkBonesAndSpock()
        self.addPhrasesForKirkBonesAndSpock()
        self.addImagesForKirkBonesAndSpock()
        self.post_phrase('Bones', 'Ever dance with the devil in the pale moonlight?')
        self.post_phrase('Kirk', 'The devil went down to Georgia.')
        self.post_phrase('Spock', 'That is devilishly clever.')
        response = self.get_results()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]['originator'], "Kirk")
        self.assertEqual(response.get_json()[0]['submissions'][0],
                         "Ever dance with the devil in the pale moonlight?")
        self.assertEqual(response.get_json()[0]['submissions'][1], "spock image")
        self.assertEqual(response.get_json()[0]['submissions'][2], "Ever dance with the devil in the pale moonlight?")
        self.assertEqual(response.get_json()[1]['originator'], "Spock")
        self.assertEqual(response.get_json()[1]['submissions'][0], "The devil went down to Georgia.")
        self.assertEqual(response.get_json()[1]['submissions'][1], "bones image")
        self.assertEqual(response.get_json()[1]['submissions'][2], "The devil went down to Georgia.")
        self.assertEqual(response.get_json()[2]['originator'], "Bones")
        self.assertEqual(response.get_json()[2]['submissions'][0], "That is devilishly clever.")
        self.assertEqual(response.get_json()[2]['submissions'][1], "kirk image")
        self.assertEqual(response.get_json()[2]['submissions'][2], "That is devilishly clever.")

    def test_canConductTwoGamesAtOnce(self):
        self.addKirkAndSpock()
        self.add_obrien_and_worf()
        self.addPhrasesForKirkAndSpock()
        self.assertPlayerStatus('SUBMIT_IMAGE', 'Kirk')
        self.assertPlayerStatus('SUBMIT_INITIAL_PHRASE', 'Obrien', 'NCC-1701D')
        self.addImagesForKirkAndSpock()
        self.assertPlayerStatus("GAME_OVER", "Kirk")
        self.assertPlayerStatus('SUBMIT_INITIAL_PHRASE', 'Obrien', 'NCC-1701D')
        self.add_phrases_for_obrien_and_worf()
        self.add_images_for_obrien_and_worf()
        self.assertPlayerStatus("GAME_OVER", "Worf", "NCC-1701D")

    def test_canPlayAFivePlayerGame(self):
        self.addKirkBonesAndSpock()
        self.add_obrien_and_worf(game='NCC-1701')
        self.addPhrasesForKirkBonesAndSpock()
        self.add_phrases_for_obrien_and_worf(game='NCC-1701')
        self.assertPlayersStatus(["Kirk", "Spock", "Bones", "Obrien", "Worf"], "SUBMIT_IMAGE")
        self.addImagesForKirkBonesAndSpock()
        self.assertPlayerStatus("WAIT", "Spock")
        self.add_images_for_obrien_and_worf(game='NCC-1701')
        self.assertPlayerStatus('SUBMIT_PHRASE', 'Bones')
        self.add_second_phrases_for_kirk_bones_and_spock()
        self.add_second_phrases_for_obrien_and_worf(game='NCC-1701')
        self.assertPlayerStatus("SUBMIT_IMAGE", "Worf")
        self.add_second_images_for_kirk_bones_and_spock()
        self.add_second_images_for_obrien_and_worf(game='NCC-1701')
        self.assertPlayersStatus(["Kirk", "Spock", "Bones", "Obrien", "Worf"], "SUBMIT_PHRASE")
        self.add_third_phrases_for_kirk_spock_bones_obrien_and_worf()
        self.assertPlayersStatus(["Kirk", "Spock", "Bones", "Obrien", "Worf"], "GAME_OVER")

    def assertPlayersStatus(self, players, status):
        for player in players:
            self.assertPlayerStatus(status, player)

    def add_images_for_obrien_and_worf(self, game='NCC-1701D'):
        self.post_image("Worf", "worf image", game)
        self.post_image("Obrien", "obrien image", game)

    def add_second_images_for_obrien_and_worf(self, game='NCC-1701D'):
        self.post_image("Worf", "worf image 2", game)
        self.post_image("Obrien", "obrien image 2", game)

    def add_phrases_for_obrien_and_worf(self, game='NCC-1701D'):
        self.post_phrase('Obrien', 'Only Keiko calls me Miles', game)
        self.post_phrase('Worf', 'A warrior\'s drink!', game)

    def add_second_phrases_for_obrien_and_worf(self, game='NCC-1701D'):
        self.post_phrase('Obrien', 'Darn Cardies', game)
        self.post_phrase('Worf', 'What is this prune juice?', game)

    def add_obrien_and_worf(self, game='NCC-1701D'):
        self.app.post('/join', json={'username': 'Obrien', 'game': game})
        self.app.post('/join', json={'username': 'Worf', 'game': game})

    def addKirkAndSpock(self):
        self.app.post('/join', json={'username': 'Kirk', 'game': 'NCC-1701'})
        self.app.post('/join', json={'username': 'Spock', 'game': 'NCC-1701'})

    def addKirkBonesAndSpock(self):
        self.addKirkAndSpock()
        self.app.post('/join', json={'username': 'Bones', 'game': 'NCC-1701'})

    def addPhrasesForKirkAndSpock(self):
        self.post_phrase('Kirk', 'Ever dance with the devil in the pale moonlight?')
        self.post_phrase('Spock', 'The devil went down to Georgia.')

    def addPhrasesForKirkBonesAndSpock(self):
        self.addPhrasesForKirkAndSpock()
        self.post_phrase('Bones', 'That is devilishly clever.')

    def add_second_phrases_for_kirk_bones_and_spock(self):
        self.post_phrase('Spock', 'Spock phrase 2')
        self.post_phrase('Bones', 'Bones phrase 2')
        self.post_phrase('Kirk', 'Kirk phrase 2')

    def addImagesForKirkAndSpock(self):
        self.post_image("Kirk", "kirk image")
        self.post_image("Spock", "spock image")

    def addImagesForKirkBonesAndSpock(self):
        self.addImagesForKirkAndSpock()
        self.post_image("Bones", "bones image")

    def add_second_images_for_kirk_bones_and_spock(self):
        self.post_image("Kirk", "kirk image 2")
        self.post_image("Spock", "spock image 2")
        self.post_image("Bones", "bones image 2")

    def add_third_phrases_for_kirk_spock_bones_obrien_and_worf(self):
        self.post_phrase('Spock', 'Spock phrase 3')
        self.post_phrase('Bones', 'Bones phrase 3')
        self.post_phrase('Kirk', 'Kirk phrase 3')
        self.post_phrase('Obrien', 'Obrien phrase 3')
        self.post_phrase('Worf', 'Worf phrase 3')
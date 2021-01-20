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

    def tear_down(self):
        pass

    # region integration_tests

    def test_hello_world_endpoint(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'This is the Arktika API base URL.  Please add an endpoint '
                                                        'name to your request to get started.')

    def test_can_join_by_posting_username_and_game_code(self):
        response = self.app.post('/join', json={'username': 'Mikey', 'game': 'gamey'})
        self.assertEqual(response.status_code, 200)

    def test_cannot_join_without_a_post_body(self):
        response = self.app.get('/join')
        self.assertEqual(response.status_code, 405)

    def test_can_erase_the_game(self):
        response = self.app.post('/join', json={'username': 'Mikey', 'game': 'gamey'})
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/restart')
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/game/gamey/player/Mikey')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json and 'error' in response.json.keys())
        self.assertEqual(response.json['error'], 'No such game: "gamey".')

    def test_cannot_join_without_a_username(self):
        response = self.app.post('/join', json={'game': 'XYZORG'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot join game: Missing username.")

    def test_cannot_join_without_posting_a_game_name(self):
        response = self.app.post('/join', json={'username': 'Jimmy'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot join game: Missing game.")

    def test_cannot_get_status_without_a_username(self):
        self.add_players_kirk_and_spock()
        self.assert_status_error(error_message="Cannot get player status: missing username.", username="", game="NCC-1701")

    def test_cannot_get_status_without_a_game_name(self):
        self.add_players_kirk_and_spock()
        self.assert_status_error(error_message="Cannot get player status for Kirk: missing game code.", username="Kirk")

    def test_can_join_and_ask_game_for_next_step(self):
        self.add_players_kirk_and_spock()
        self.assert_player_status("SUBMIT_INITIAL_PHRASE", "Kirk")

    def test_get_next_step_says400_if_you_have_not_joined(self):
        self.assert_status_error('No such game: "abc".', "Mikey", "abc")

    def test_status_endpoint_correctly_identifies_players_before_and_after_you_2player(self):
        self.add_players_kirk_and_spock()
        self.assert_player_status(username="Kirk", player_before="Spock", player_after="Spock")
        self.assert_player_status(username="Spock", player_before="Kirk", player_after="Kirk")

    def test_status_endpoint_correctly_identifies_players_before_and_after_you_3player(self):
        self.add_players_kirk_bones_and_spock()
        self.assert_player_status(username="Kirk", player_before="Bones", player_after="Spock")
        self.assert_player_status(username="Spock", player_before="Kirk", player_after="Bones")
        self.assert_player_status(username="Bones", player_before="Spock", player_after="Kirk")

    def test_status_endpoint_correctly_identifies_players_before_and_after_you_5player(self):
        self.add_players_kirk_bones_and_spock()
        self.add_players_obrien_and_worf(game='NCC-1701')
        self.assert_player_status(username="Kirk", player_before="Worf", player_after="Spock")
        self.assert_player_status(username="Spock", player_before="Kirk", player_after="Bones")
        self.assert_player_status(username="Bones", player_before="Spock", player_after="Obrien")
        self.assert_player_status(username="Obrien", player_before="Bones", player_after="Worf")
        self.assert_player_status(username="Worf", player_before="Obrien", player_after="Kirk")

    def test_summary_endpoint_can_summarize_at_game_start(self):
        self.add_players_kirk_bones_and_spock()
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

    def test_summary_endpoint_can_summarize_mid_round(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_bones_and_spock()
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

    def test_summary_endpoint_can_summarize_at_game_end(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_bones_and_spock()
        self.add_images_for_kirk_bones_and_spock()
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

    def test_summary_includes_only_status_descriptions_not_full_statuses(self):
        self.add_players_kirk_bones_and_spock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.json['players'][0]['status'].keys()), ['description'])

    def test_summary_reports_joinable_game_positively_at_start(self):
        self.add_players_kirk_bones_and_spock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canJoin'], True)

    def test_summary_reports_one_person_is_not_enough_to_start(self):
        response = self.app.post('/join', json={'username': 'Kirk', 'game': 'NCC-1701'})
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canStart'], False)

    def test_summary_reports_two_people_is_enough_to_start(self):
        self.add_players_kirk_bones_and_spock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canStart'], True)

    def test_summary_a_started_game_gannot_start(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_bones_and_spock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canStart'], False)

    def test_summary_reports_joinable_game_negatively_after_phase_one(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_bones_and_spock()
        response = self.app.get('/game/NCC-1701')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['canJoin'], False)
        self.assertEqual(response.json['phaseNumber'], 2)

    def test_summary_requires_game_name(self):
        self.add_players_kirk_bones_and_spock()
        response = self.app.get('/game')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot get current summary: missing game code.")

    def test_summary_warns_of_invalid_game_name(self):
        self.add_players_kirk_bones_and_spock()
        response = self.app.get('/game/NCC-1701C')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], 'No such game: "NCC-1701C".')

    def test_can_post_initial_phrase(self):
        self.add_players_kirk_and_spock()
        response = self.post_phrase("Kirk", 'Ever dance with the devil in the pale moonlight?')
        self.assertEqual(response.status_code, 200)
        self.assert_player_status("WAIT", "Kirk")

    def test_prompt_for_image_after_all_players_submit_initial_phrase(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.assert_player_status("SUBMIT_IMAGE", "Kirk")
        self.assert_player_status("SUBMIT_IMAGE", "Spock")

    def test_cannot_join_after_all_players_submit_initial_phrase(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        response = self.app.post('/join', json={'username': 'Mikey', 'game': 'NCC-1701'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], "Cannot join a game in progress.")

    def test_can_join_again_after_game_over(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.add_images_for_kirk_and_spock()
        response = self.app.post('/join', json={'username': 'Mikey', 'game': 'NCC-1701'})
        self.assertEqual(response.status_code, 200)

    def test_image_prompts_include_proper_phrase(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_bones_and_spock()
        self.assert_player_status("SUBMIT_IMAGE", "Kirk", prompt='That is devilishly clever.', status_code=200)
        self.assert_player_status("SUBMIT_IMAGE", "Spock", prompt='Ever dance with the devil in the pale moonlight?', status_code=200)
        self.assert_player_status("SUBMIT_IMAGE", "Bones", prompt='The devil went down to Georgia.', status_code=200)

    def test_cannot_submit_phrase_when_it_is_image_time(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        response = self.post_phrase("Spock", 'The devil is in the details.')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'],
                         "Cannot submit phrase: it is not Spock's turn to submit a phrase.")

    def test_cannot_submit_phrase_without_a_username(self):
        self.add_players_kirk_and_spock()
        response = self.app.post('/phrase', json={'username': '', 'phrase': 'The devil is in the details.'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'],
                         "Cannot submit phrase: Missing username.")

    def test_cannot_submit_image_when_it_is_phrase_time(self):
        self.add_players_kirk_and_spock()
        response = self.post_image("Spock", "spock image")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'],
                         "Cannot submit image: it is not Spock's turn to submit an image.")

    def test_cannot_submit_image_without_username(self):
        self.add_players_kirk_and_spock()
        response = self.app.post('/image', json={'username': '',
                                                 'image': 'spock image'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'],
                         "Cannot submit image: Missing username.")

    def test_cannot_submit_phrase_without_game_name(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.assert_post_phrase_error("Kirk", "roll the dice", error="Cannot submit phrase: Missing game.")

    def test_cannot_submit_image_without_game_name(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.assert_post_image_error("Kirk", "pix", error="Cannot submit image: Missing game.")

    def test_submit_image_warns_of_invalid_game_name(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.assert_post_image_error("Kirk", "an image", "NCC-1701C", 'No such game: "NCC-1701C".')

    def test_submit_phrase_warns_of_invalid_game_name(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.assert_post_phrase_error("Kirk", "the devils of our nature", "NCC-1701C", 'No such game: "NCC-1701C".')

    def test_phrase_prompts_include_proper_image(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_bones_and_spock()
        self.add_images_for_kirk_bones_and_spock()

        self.assert_player_status("SUBMIT_PHRASE", "Kirk", prompt='bones image')

    def test_status_is_game_over_for_everyone_after_one_submission_per_player(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.add_images_for_kirk_and_spock()
        self.assert_player_status("GAME_OVER", "Kirk")
        self.assert_player_status("GAME_OVER", "Spock")

    def test_cannot_get_results_prior_to_game_being_over(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.assert_results_error('Cannot get results: game not over.')

    def test_cannot_get_results_without_game_code(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.add_images_for_kirk_and_spock()
        self.assert_results_error('Cannot get results: missing game code.', '')

    def test_cannot_get_results_without_valid_game_code(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.add_images_for_kirk_and_spock()
        self.assert_results_error('Cannot get results.  No such game: "NCC-1701C".', 'NCC-1701C')

    def test_can_get_results_after_completed_two_player_game(self):
        self.add_players_kirk_and_spock()
        self.add_phrases_for_kirk_and_spock()
        self.add_images_for_kirk_and_spock()
        response = self.get_results()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]['originator'], "Kirk")
        self.assertEqual(response.get_json()[0]['submissions'][0], "Ever dance with the devil in the pale moonlight?")
        self.assertEqual(response.get_json()[0]['submissions'][1], "spock image")

        self.assertEqual(response.get_json()[1]['originator'], "Spock")
        self.assertEqual(response.get_json()[1]['submissions'][0], "The devil went down to Georgia.")
        self.assertEqual(response.get_json()[1]['submissions'][1], "kirk image")

    def test_can_get_results_after_completed_three_player_game(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_bones_and_spock()
        self.add_images_for_kirk_bones_and_spock()
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

    def test_can_get_results_after_a_completed_three_player_game_with_different_submission_order(self):
        self.add_players_kirk_bones_and_spock()

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

    def test_three_player_game_in_which_phrases_are_correctly_guessed(self):
        self.add_players_kirk_bones_and_spock()
        self.add_phrases_for_kirk_bones_and_spock()
        self.add_images_for_kirk_bones_and_spock()
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

    def test_can_conduct_two_games_at_once(self):
        self.add_players_kirk_and_spock()
        self.add_players_obrien_and_worf()
        self.add_phrases_for_kirk_and_spock()
        self.assert_player_status('SUBMIT_IMAGE', 'Kirk')
        self.assert_player_status('SUBMIT_INITIAL_PHRASE', 'Obrien', 'NCC-1701D')
        self.add_images_for_kirk_and_spock()
        self.assert_player_status("GAME_OVER", "Kirk")
        self.assert_player_status('SUBMIT_INITIAL_PHRASE', 'Obrien', 'NCC-1701D')
        self.add_phrases_for_obrien_and_worf()
        self.add_images_for_obrien_and_worf()
        self.assert_player_status("GAME_OVER", "Worf", "NCC-1701D")

    def test_can_play_a_five_player_game(self):
        self.add_players_kirk_bones_and_spock()
        self.add_players_obrien_and_worf(game='NCC-1701')
        self.add_phrases_for_kirk_bones_and_spock()
        self.add_phrases_for_obrien_and_worf(game='NCC-1701')
        self.assert_players_status(["Kirk", "Spock", "Bones", "Obrien", "Worf"], "SUBMIT_IMAGE")
        self.add_images_for_kirk_bones_and_spock()
        self.assert_player_status("WAIT", "Spock")
        self.add_images_for_obrien_and_worf(game='NCC-1701')
        self.assert_player_status('SUBMIT_PHRASE', 'Bones')
        self.add_second_phrases_for_kirk_bones_and_spock()
        self.add_second_phrases_for_obrien_and_worf(game='NCC-1701')
        self.assert_player_status("SUBMIT_IMAGE", "Worf")
        self.add_second_images_for_kirk_bones_and_spock()
        self.add_second_images_for_obrien_and_worf(game='NCC-1701')
        self.assert_players_status(["Kirk", "Spock", "Bones", "Obrien", "Worf"], "SUBMIT_PHRASE")
        self.add_third_phrases_for_kirk_spock_bones_obrien_and_worf()
        self.assert_players_status(["Kirk", "Spock", "Bones", "Obrien", "Worf"], "GAME_OVER")

    # endregion

    # region assertions

    def assert_player_status(self, status_message="", username="", game="NCC-1701", prompt="", player_before="",
                             player_after="", status_code=200):
        response = self.app.get('/game/'+game+'/player/'+username)
        self.assertEqual(response.status_code, status_code)
        if (status_message):
            self.assertEqual(response.get_json()['description'], status_message)
        if (prompt):
            self.assertEqual(response.get_json()['prompt'], prompt)
        if (player_before):
            self.assertEqual(response.get_json()['previousPlayerUsername'], player_before)
        if (player_after):
            self.assertEqual(response.get_json()['nextPlayerUsername'], player_after)

    def assert_results_error(self, error, game="NCC-1701", status_code=400):
        response = self.get_results(game)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get_json()['error'], error)

    def assert_post_image_error(self, username="", image="", game="", error="", status_code=400):
        response = self.post_image(username, image, game)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get_json()['error'],
                         error)

    def assert_players_status(self, players, status):
        for player in players:
            self.assert_player_status(status, player)

    def assert_post_phrase_error(self, username="", phrase="", game="", error="", status_code=400):
        response = self.post_phrase(username, phrase, game)
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get_json()['error'], error)

    def assert_status_error(self, error_message="", username="", game=""):
        url = ('/game/' + ((game + '/') if len(game) > 0 else "")) + ('player' + (('/' + username) if len(username) > 0 else ""))
        response = self.app.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error'], error_message)

    # endregion

    # region testutil

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

    def add_players_obrien_and_worf(self, game='NCC-1701D'):
        self.app.post('/join', json={'username': 'Obrien', 'game': game})
        self.app.post('/join', json={'username': 'Worf', 'game': game})

    def add_players_kirk_and_spock(self):
        self.app.post('/join', json={'username': 'Kirk', 'game': 'NCC-1701'})
        self.app.post('/join', json={'username': 'Spock', 'game': 'NCC-1701'})

    def add_players_kirk_bones_and_spock(self):
        self.add_players_kirk_and_spock()
        self.app.post('/join', json={'username': 'Bones', 'game': 'NCC-1701'})

    def add_phrases_for_kirk_and_spock(self):
        self.post_phrase('Kirk', 'Ever dance with the devil in the pale moonlight?')
        self.post_phrase('Spock', 'The devil went down to Georgia.')

    def add_phrases_for_kirk_bones_and_spock(self):
        self.add_phrases_for_kirk_and_spock()
        self.post_phrase('Bones', 'That is devilishly clever.')

    def add_second_phrases_for_kirk_bones_and_spock(self):
        self.post_phrase('Spock', 'Spock phrase 2')
        self.post_phrase('Bones', 'Bones phrase 2')
        self.post_phrase('Kirk', 'Kirk phrase 2')

    def add_images_for_kirk_and_spock(self):
        self.post_image("Kirk", "kirk image")
        self.post_image("Spock", "spock image")

    def add_images_for_kirk_bones_and_spock(self):
        self.add_images_for_kirk_and_spock()
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

    def post_image(self, username="", image="", game="NCC-1701"):
        return self.app.post('/image', json={'username': username, 'image': image, 'game': game})

    def post_phrase(self, username="", phrase="", game="NCC-1701"):
        return self.app.post('/phrase', json={'username': username, 'phrase': phrase, 'game': game})

    def get_results(self, game="NCC-1701"):
        if game:
            return self.app.get("/game/" + game + "/results")
        else:
            return self.app.get("/game/results")

    # endregion

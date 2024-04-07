from datetime import datetime
from unittest import TestCase
from unittest.mock import (patch, MagicMock)
from helpers.email import (EMailClient, get_email_components)

CONST_EMAIL = 'test@example.org'
CONST_SUBJECT = 'Test Email'
CONST_NAME = 'Test User'
CONST_SENDER_EMAIL = 'test_sender@example.com'
CONST_SENDER_NAME = 'Test Sender'
CONST_TEMPLATE_TEXT = 'misconduct.text.jinja'
CONST_TEMPLATE_HTML = 'misconduct.html.jinja'
CONST_TEST_MESSAGE = "This is a test message"
CONST_FROM_EMAIL = "Hanover Soccer Referee <test_sender@example.com>"
CONST_START_MESSAGE = "DEBUG:helpers.email:Starting create message ..."
CONST_END_MESSAGE = "DEBUG:helpers.email:Completed create message ..."
CONST_TEST_USER = "test user"
CONST_DATE_FORMAT = "%m/%d/%Y"

CONST_DATA_NO_MESSAGE = {
    'email': CONST_EMAIL,
    'subject': CONST_SUBJECT,
    'name': CONST_NAME
}

CONST_DATA_MESSAGE = {
    'subject': CONST_SUBJECT,
    'content': {
        'misconducts': [{
        "home_team_score": "0",
        "away_team_score": "4",
        "text": "Player #4 Simpson (Springfield) violently struck AR1 in the 43rd minute after an offside was called.\u00a0 Player was sent off.\u00a0 IDK\u00a0awarded yellow team",
        "html": "<div class=\"trix-content\"> <div>Player #4 Simpson (Springfield) violently struck AR1 in the 43rd minute after an offside was called. Player was sent off. IDK awarded yellow team</div> </div>",
        "officials": [{
            "no_show": "false",
            "position": "Referee",
            "first_name": "Mickey",
            "last_name": "Mouse"
        }],
        "author": "Homer Simpson",
        "game_dt": "2023-10-21T09:15:00.000-04:00",
        "home_team": "Springfield-1",
        "away_team": "Ogdenville-1",
        "venue": "Springfield Elementary School",
        "sub_venue": "Field Four",
        "game_type": "Coastal",
        "age_group": "Grade 5/6",
        "gender": "Boys",
        "home_coach": "Mr. Burns",
        "away_coach": "Mr. Smithers" }]
    }
}

mock_email_response = MagicMock()
mock_email_response.status_code = 200
mock_email_response.json.return_value = {
    "token_type": "Bearer",
    "scope": "read",
    "created_at": 1606420331
}


class TestEmailHelpers(TestCase):
    def test_valid_email_components(self):
        expected_result = {
            'name': CONST_TEST_USER,
            'address': 'test',
            'domain': 'example.org'
        }
        result = get_email_components("<test user>test@example.org")
        self.assertEqual(result, expected_result)

    def test_invalid_email_name(self):
        expected_result = {
            'name': None,
            'address': None,
            'domain': None
        }
        with self.assertLogs(level='DEBUG') as cm:
            result = get_email_components("test usertest@example.org")
        self.assertEqual(cm.output, [
            'ERROR:helpers.email:Could not determine name for test usertest@example.org.'
        ])
        self.assertEqual(result, expected_result)

    def test_invalid_email_address_missing_at(self):
        expected_result = {
            'name': CONST_TEST_USER,
            'address': None,
            'domain': None
        }
        with self.assertLogs(level='DEBUG') as cm:
            result = get_email_components("<test user>testexample.org")
        self.assertEqual(cm.output, [
            'ERROR:helpers.email:Invalid email address: <test user>testexample.org.'
        ])
        self.assertEqual(result, expected_result)

    def test_invalid_email_address_missing_dot(self):
        expected_result = {
            'name': CONST_TEST_USER,
            'address': 'test',
            'domain': None
        }
        with self.assertLogs(level='DEBUG') as cm:
            result = get_email_components("<test user>test@example")
        self.assertEqual(cm.output, [
            'ERROR:helpers.email:Invalid email address: <test user>test@example.'
        ])
        self.assertEqual(result, expected_result)

class TestEMail(TestCase):
    def test_send_email_missing_subject_content(self):
        data = {}

        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   CONST_SENDER_NAME, 'test_password')
        with self.assertLogs(level='DEBUG') as cm:
            result = email_client.send_email(data, CONST_SENDER_EMAIL,
                                             'no_template')
        self.assertEqual(result, 33)
        self.assertEqual(cm.output, [
            "DEBUG:helpers.email:Starting send email ...",
            "ERROR:helpers.email:'content' is required",
            "ERROR:helpers.email:'subject' is required"
        ])

#    def test_send_email_create_is_none(self):
#        data = {
#            'subject': 'Misconduct: 2023-10-01 - 2023-10-31',
#            'content': {
#                'start_date': datetime.date(2023, 10, 1), 
#                'end_date': datetime.date(2023, 10, 31),
#                'misconducts': 
#                [{
#                    'home_team_score': '0', 'away_team_score': '4', 
#                    'text': 'Player #4 White (Hanover) violently struck ' \
#                    'AR1 in the 43rd minute after an offside was called.\xa0' \
#                    ' Player was sent off.\xa0 IDK\xa0awarded yellow team',
#                    'html': '<div class="trix-content"> <div>Player #4 White' \
#                    ' (Hanover) violently struck AR1 in the 43rd minute after ' \
#                    'an offside was called. Player was sent off. IDK awarded ' \
#                    'yellow team</div> </div>', 
#                    'officials':
#                    [{
#                        'no_show': False, 'position': 'Referee', 
#                        'first_name': 'Mickey', 'last_name': 'Mouse'
#                    }],
#                    'author': 'Pluto', 'game_dt': '2023-10-21T09:15:00.000-04:00',
#                    'home_team': 'Orlando-1', 'away_team': 'Miami-1',
#                    'venue': 'Disney World', 'sub_venue': 'Epcot', 
#                    'game_type': 'Coastal', 'age_group': 'Grade 5/6',
#                    'gender': 'Boys', 'home_coach': 'Mr. Burns',
#                    'away_coach': 'Mr. Smithers'
#                }]
#            }
#        }
#
#        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
#                                   CONST_SENDER_NAME, 'test_password')
#        with self.assertLogs(level='DEBUG') as cm:
#            result = email_client.send_email(data, CONST_SENDER_EMAIL,
#                                             'no_template')
#        self.assertEqual(result, 33)
#        self.assertEqual(cm.output, [
#            "DEBUG:helpers.email:Starting send email ...",
#            "ERROR:helpers.email:'content' is required",
#            "ERROR:helpers.email:'subject' is required"
#        ])

    def test_create_message_missing_template(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   CONST_SENDER_NAME, 'test_password')

        with self.assertLogs(level='DEBUG') as cm:
            message = email_client.create_message(CONST_DATA_NO_MESSAGE, 'missing.txt')
        self.assertEqual(cm.output, [
            CONST_START_MESSAGE,
            "ERROR:helpers.email:Missing File: missing.txt",
            CONST_END_MESSAGE
        ])
        self.assertIsNone(message)

    def test_create_message_html_no_misconducts(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   CONST_SENDER_NAME, 'test_password')
        expected_msg = '<p><strong>No Misconducts issued</strong></p>'

        message = email_client.create_message([], CONST_TEMPLATE_HTML)
        self.assertEqual( message, expected_msg)

    def test_create_message_html(self):
        expected_msg = '<h1>Misconduct Report (2020-01-01 - 2021-01-01)</h1><br>\n<b>Reported By:</b> Homer Simpson\n<h2>Game Information</h2>\n<p>Date: 10/21/2023</p>\n<p>Time: 09:15 AM</p>\n<p>Venue: Springfield Elementary School</p>\n<p>Home Team:\n  Springfield-1 Score: 0</p>\n  <strong>Coach:</strong> Mr. Burns\n</p>\n<p>Away Team:\n  Ogdenville-1 Score: 4</p>\n  <strong>Coach:</strong> Mr. Smithers\n<h2>Officials</h2><p>Referee: </p><h2>Details</h2>\n<table>\n  <tr>\n    <th>Result</th>\n    <th>Name</th>\n    <th>Coach/Player</th>\n    <th>Pass Id/#</th>\n    <th>Team</th>\n    <th>Minute</th>\n    <th>Offense</th>\n    <th>Description</th>\n  </tr>\n  <tr></table>'''

        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   CONST_SENDER_NAME, 'test_password')
        CONST_DATA_MESSAGE['content']['start_date'] = \
            datetime.strptime('01/01/2020', CONST_DATE_FORMAT).date()
        CONST_DATA_MESSAGE['content']['end_date'] = \
            datetime.strptime('01/01/2021', CONST_DATE_FORMAT).date()

        message = email_client.create_message(CONST_DATA_MESSAGE['content'],
                                                CONST_TEMPLATE_HTML)
        self.assertEqual(message, expected_msg)

    def test_create_message_text(self):
        expected_msg = 'Misconduct Report (2020-01-01 - 2021-01-01)\n' \
            'Reported By: Homer Simpson\n\nGame Information\n' \
            '  Date: 2023-10-21T09:15:00.000-04:00\n' \
            '  Home Team: Springfield-1 Score: 0\n' \
            '  Away Team: Ogdenville-1 Score: 4\n\n' \
            'Officials\nReferee: Mickey Mouse\n\nNarrative\n' \
            'Player #4 Simpson (Springfield) violently struck AR1 ' \
            'in the 43rd minute after an offside was called.\xa0 ' \
            'Player was sent off.\xa0 IDK\xa0awarded yellow team'
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   CONST_SENDER_NAME, 'test_password')
        CONST_DATA_MESSAGE['content']['start_date'] = \
            datetime.strptime('01/01/2020', CONST_DATE_FORMAT).date()
        CONST_DATA_MESSAGE['content']['end_date'] = \
            datetime.strptime('01/01/2021', CONST_DATE_FORMAT).date()

        with self.assertLogs(level='DEBUG') as cm:
            message = email_client.create_message(CONST_DATA_MESSAGE['content'],
                                                  CONST_TEMPLATE_TEXT)
        self.assertEqual(cm.output, [
            'DEBUG:helpers.email:Starting create message ...',
            'DEBUG:helpers.email:Completed create message ...'
        ])

        self.assertEqual(message, expected_msg)

    def test_create_email_text_single_address(self):
        addresses = "<user one>user.one@example.org"
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   CONST_SENDER_NAME, 'test_password')

        message = email_client.create_email(CONST_DATA_MESSAGE,
                                            CONST_TEMPLATE_HTML,
                                            addresses, False)
        self.assertEqual(message._headers[0][0], 'From')
        self.assertEqual(message._headers[0][1],
            f'{CONST_SENDER_NAME} <{CONST_SENDER_EMAIL}>')
        self.assertEqual(message._headers[1][0], 'To')
        self.assertEqual(message._headers[1][1],
            'user one <user.one@example.org>')
        self.assertEqual(message._headers[2][0], 'Subject')
        self.assertEqual(message._headers[2][1], 'Test Email')
        self.assertEqual(message._headers[3][0], 'Content-Type')
        self.assertEqual(message._headers[3][1],
            'text/plain; charset="utf-8"')

    def test_create_email_text_multiple_addresses(self):
        addresses = "<user one>user.one@example.org,<user two>user.two@example.org"
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   CONST_SENDER_NAME, 'test_password')

        message = email_client.create_email(CONST_DATA_MESSAGE,
                                            CONST_TEMPLATE_HTML,
                                            addresses, False)
        self.assertEqual(message._headers[0][0], 'From')
        self.assertEqual(message._headers[0][1],
            f'{CONST_SENDER_NAME} <{CONST_SENDER_EMAIL}>')
        self.assertEqual(message._headers[1][0], 'To')
        self.assertEqual(message._headers[1][1],
            'user one <user.one@example.org>, user two <user.two@example.org>')
        self.assertEqual(message._headers[2][0], 'Subject')
        self.assertEqual(message._headers[2][1], 'Test Email')
        self.assertEqual(message._headers[3][0], 'Content-Type')
        self.assertEqual(message._headers[3][1],
            'text/plain; charset="utf-8"')

    def test_create_email_html(self):
        addresses = "<user one>user.one@example.org,<user two>user.two@example.org"
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   CONST_SENDER_NAME, 'test_password')

        with self.assertLogs(level='DEBUG') as cm:
            message = email_client.create_email(CONST_DATA_MESSAGE,
                                                CONST_TEMPLATE_HTML,
                                                addresses, True)
        self.assertEqual(cm.output, [
            "DEBUG:helpers.email:Starting create email ...",
            CONST_START_MESSAGE,
            CONST_END_MESSAGE,
            "DEBUG:helpers.email:Completed create email ..."
        ])
        self.assertEqual(message._headers[0][0], 'From')
        self.assertEqual(message._headers[0][1],
             f'{CONST_SENDER_NAME} <{CONST_SENDER_EMAIL}>')
        self.assertEqual(message._headers[1][0], 'To')
        self.assertEqual(message._headers[1][1],
            'user one <user.one@example.org>, user two <user.two@example.org>')
        self.assertEqual(message._headers[2][0], 'Subject')
        self.assertEqual(message._headers[2][1], 'Test Email')
        self.assertEqual(message._headers[3][0], 'Content-Type')
        self.assertEqual(message._headers[3][1],
            'text/html; charset="utf-8"')

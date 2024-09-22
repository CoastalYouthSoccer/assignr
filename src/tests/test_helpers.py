from os import environ
from unittest import TestCase
from unittest.mock import (patch, MagicMock, ANY)
from googleapiclient.errors import HttpError
from helpers import constants
from helpers.helpers import (get_environment_vars, get_spreadsheet_vars,
                             get_email_vars, format_str_hh_mm,
                             format_str_mm_dd_yyyy, load_sheet,
                             rows_to_dict, get_match_count, get_misconducts,
                             get_referees, get_coaches_name)

CONST_GRADE_78 = "Grade 7/8"
CLIENT_SECRET = "client_secret"
CLIENT_ID = "client_id"
CLIENT_SCOPE = "client_scope"
AUTH_URL = "auth_url"
BASE_URL = "base_url"
SPREADSHEET_ID = "spreadsheet_id"
SPREADSHEET_RANGE = "spreadsheet_range"
GOOGLE_CREDENTIALS = "google_credentials"
ADMIN_EMAIL = "admin_email"
MISCONDUCTS_EMAIL = "misconducts_email"
EMAIL_SERVER = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USERNAME = "email_username"
EMAIL_PASSWORD = "email_password"
NOT_ASSIGNED = "Not Assigned"
ASST_REFEREE = "Asst. Referee"

class TestHelpers(TestCase):
    @patch.dict(environ,
        {
            constants.CLIENT_SECRET: CLIENT_SECRET,
            constants.CLIENT_ID: CLIENT_ID,
            constants.CLIENT_SCOPE: CLIENT_SCOPE,
            constants.AUTH_URL: AUTH_URL,
            constants.BASE_URL: BASE_URL
        }, clear=True)
    def test_environment_set(self):
        expected_results = {
            constants.CLIENT_SECRET: CLIENT_SECRET,
            constants.CLIENT_ID: CLIENT_ID,
            constants.CLIENT_SCOPE: CLIENT_SCOPE,
            constants.AUTH_URL: AUTH_URL,
            constants.BASE_URL: BASE_URL
        }
        error, result = get_environment_vars()
        self.assertEqual(error, 0)
        self.assertEqual(result, expected_results)

    @patch.dict(environ,
        {
            constants.CLIENT_ID: CLIENT_ID,
            constants.CLIENT_SCOPE: CLIENT_SCOPE,
            constants.AUTH_URL: AUTH_URL,
            constants.BASE_URL: BASE_URL
        }, clear=True)
    def test_missing_client_secret(self):
        expected_results = {
            constants.CLIENT_SECRET: None,
            constants.CLIENT_ID: CLIENT_ID,
            constants.CLIENT_SCOPE: CLIENT_SCOPE,
            constants.AUTH_URL: AUTH_URL,
            constants.BASE_URL: BASE_URL
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_environment_vars()
        self.assertEqual(cm.output, [
            f'ERROR:helpers.helpers:{constants.CLIENT_SECRET} environment variable is missing'
        ])
        self.assertEqual(error, 66)
        self.assertEqual(result, expected_results)

    @patch.dict(environ, {}, clear=True)
    def test_missing_all_environment(self):
        expected_errors = [
            f'ERROR:helpers.helpers:{constants.CLIENT_SECRET} environment variable is missing',
            f'ERROR:helpers.helpers:{constants.CLIENT_ID} environment variable is missing',
            f'ERROR:helpers.helpers:{constants.CLIENT_SCOPE} environment variable is missing',
            f'ERROR:helpers.helpers:{constants.AUTH_URL} environment variable is missing',
            f'ERROR:helpers.helpers:{constants.BASE_URL} environment variable is missing'
        ]
        expected_results = {
            constants.CLIENT_SECRET: None,
            constants.CLIENT_ID: None,
            constants.CLIENT_SCOPE: None,
            constants.AUTH_URL: None,
            constants.BASE_URL: None
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_environment_vars()
        self.assertEqual(cm.output, expected_errors)
        self.assertEqual(result, expected_results)
        self.assertEqual(error, 66)

    @patch.dict(environ,
        {
            constants.SPREADSHEET_ID: SPREADSHEET_ID,
            constants.SPREADSHEET_RANGE: SPREADSHEET_RANGE,
            constants.GOOGLE_APPLICATION_CREDENTIALS: GOOGLE_CREDENTIALS
        }, clear=True)
    def test_spreadsheet_environments_set(self):
        expected_results = {
            constants.SPREADSHEET_ID: SPREADSHEET_ID,
            constants.SPREADSHEET_RANGE: SPREADSHEET_RANGE,
            constants.GOOGLE_APPLICATION_CREDENTIALS: GOOGLE_CREDENTIALS
        }
        error, result = get_spreadsheet_vars()
        self.assertEqual(error, 0)
        self.assertEqual(result, expected_results)

    @patch.dict(environ,
        {
            constants.SPREADSHEET_RANGE: SPREADSHEET_RANGE,
            constants.GOOGLE_APPLICATION_CREDENTIALS: GOOGLE_CREDENTIALS
        }, clear=True)
    def test_spreadsheet_missing_id(self):
        expected_results = {
            constants.SPREADSHEET_ID: None,
            constants.SPREADSHEET_RANGE: SPREADSHEET_RANGE,
            constants.GOOGLE_APPLICATION_CREDENTIALS: GOOGLE_CREDENTIALS
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_spreadsheet_vars()
        self.assertEqual(cm.output, [
            f'ERROR:helpers.helpers:{constants.SPREADSHEET_ID} environment variable is missing'
        ])
        self.assertEqual(error, 55)
        self.assertEqual(result, expected_results)

    @patch.dict(environ, {}, clear=True)
    def test_missing_all_spreadsheet_vars(self):
        expected_errors = [
            f'ERROR:helpers.helpers:{constants.GOOGLE_APPLICATION_CREDENTIALS} environment variable is missing',
            f'ERROR:helpers.helpers:{constants.SPREADSHEET_ID} environment variable is missing',
            f'ERROR:helpers.helpers:{constants.SPREADSHEET_RANGE} environment variable is missing'
        ]
        expected_results = {
            constants.SPREADSHEET_ID: None,
            constants.SPREADSHEET_RANGE: None,
            constants.GOOGLE_APPLICATION_CREDENTIALS: None
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_spreadsheet_vars()
        self.assertEqual(cm.output, expected_errors)
        self.assertEqual(result, expected_results)
        self.assertEqual(error, 55)

    @patch.dict(environ,
        {
            constants.EMAIL_SERVER: EMAIL_SERVER,
            constants.EMAIL_PORT: f'{EMAIL_PORT}',
            constants.EMAIL_USERNAME: EMAIL_USERNAME,
            constants.EMAIL_PASSWORD: EMAIL_PASSWORD,
            constants.ADMIN_EMAIL: ADMIN_EMAIL,
            constants.MISCONDUCTS_EMAIL: MISCONDUCTS_EMAIL
        }, clear=True)
    def test_email_set(self):
        expected_results = {
            constants.EMAIL_SERVER: EMAIL_SERVER,
            constants.EMAIL_PORT: EMAIL_PORT,
            constants.EMAIL_USERNAME: EMAIL_USERNAME,
            constants.EMAIL_PASSWORD: EMAIL_PASSWORD,
            constants.ADMIN_EMAIL: ADMIN_EMAIL,
            constants.MISCONDUCTS_EMAIL: MISCONDUCTS_EMAIL
        }
        error, result = get_email_vars()
        self.assertEqual(error, 0)
        self.assertEqual(result, expected_results)

    @patch.dict(environ,
        {
            constants.EMAIL_USERNAME: EMAIL_USERNAME,
            constants.EMAIL_PASSWORD: EMAIL_PASSWORD,
            constants.ADMIN_EMAIL: ADMIN_EMAIL,
            constants.MISCONDUCTS_EMAIL: MISCONDUCTS_EMAIL
        }, clear=True)
    def test_email_default_values(self):
        expected_results = {
            constants.EMAIL_SERVER: EMAIL_SERVER,
            constants.EMAIL_PORT: EMAIL_PORT,
            constants.EMAIL_USERNAME: EMAIL_USERNAME,
            constants.EMAIL_PASSWORD: EMAIL_PASSWORD,
            constants.ADMIN_EMAIL: ADMIN_EMAIL,
            constants.MISCONDUCTS_EMAIL: MISCONDUCTS_EMAIL
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_email_vars()
        self.assertEqual(error, 0)
        self.assertEqual(result, expected_results)
        self.assertEqual(cm.output, [
            f'INFO:helpers.helpers:{constants.EMAIL_SERVER} environment variable is missing, defaulting to "{EMAIL_SERVER}"',
            f'INFO:helpers.helpers:{constants.EMAIL_PORT} environment variable is missing, defaulting to {EMAIL_PORT}'
        ])

    @patch.dict(environ,
        {
            constants.EMAIL_SERVER: EMAIL_SERVER,
            constants.EMAIL_PORT: "abc",
            constants.EMAIL_USERNAME: EMAIL_USERNAME,
            constants.EMAIL_PASSWORD: EMAIL_PASSWORD,
            constants.ADMIN_EMAIL: ADMIN_EMAIL,
            constants.MISCONDUCTS_EMAIL: MISCONDUCTS_EMAIL
        }, clear=True)
    def test_email_invalid_port(self):
        expected_results = {
            constants.EMAIL_SERVER: EMAIL_SERVER,
            constants.EMAIL_PORT: EMAIL_PORT,
            constants.EMAIL_USERNAME: EMAIL_USERNAME,
            constants.EMAIL_PASSWORD: EMAIL_PASSWORD,
            constants.ADMIN_EMAIL: ADMIN_EMAIL,
            constants.MISCONDUCTS_EMAIL: MISCONDUCTS_EMAIL
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_email_vars()
        self.assertEqual(cm.output, 
            [f'ERROR:helpers.helpers:{constants.EMAIL_PORT} environment variable is not an integer'])
        self.assertEqual(error, 55)
        self.assertEqual(result, expected_results)

    @patch.dict(environ,
        {
            constants.EMAIL_SERVER: EMAIL_SERVER,
            constants.EMAIL_PORT: f'{EMAIL_PORT}'
        }, clear=True)
    def test_email_missing_values(self):
        expected_results = {
            constants.EMAIL_SERVER: EMAIL_SERVER,
            constants.EMAIL_PORT: EMAIL_PORT,
            constants.EMAIL_USERNAME: None,
            constants.EMAIL_PASSWORD: None,
            constants.ADMIN_EMAIL: None,
            constants.MISCONDUCTS_EMAIL: None
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_email_vars()
        self.assertEqual(cm.output, [
            f'ERROR:helpers.helpers:{constants.EMAIL_USERNAME} environment variable is missing',
            f'ERROR:helpers.helpers:{constants.EMAIL_PASSWORD} environment variable is missing',
            f'ERROR:helpers.helpers:{constants.ADMIN_EMAIL} environment variable is missing',
            f'ERROR:helpers.helpers:{constants.MISCONDUCTS_EMAIL} environment variable is missing'
        ])
        self.assertEqual(error, 55)
        self.assertEqual(result, expected_results)

    def test_format_str_mm_dd_yyyy(self):
        dt = format_str_mm_dd_yyyy("2023-10-14T14:47:31.000-04:00")
        self.assertEqual(dt, "10/14/2023")

    def test_format_str_mm_dd_yyyy_none(self):
        with self.assertLogs(level='INFO') as cm:
            dt = format_str_mm_dd_yyyy(None)
        self.assertIsNone(dt)
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:Unknown error: Parser must be a string or character stream, not NoneType'
        ])

    def test_format_str_mm_dd_yyyy_empty(self):
        with self.assertLogs(level='INFO') as cm:
            dt = format_str_mm_dd_yyyy("")
        self.assertIsNone(dt)
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:Failed to parse date: '
        ])

    def test_format_str_hh_mm(self):
        dt = format_str_hh_mm("2023-10-14T14:47:31.000-04:00")
        self.assertEqual(dt, "02:47 PM")

    def test_format_str_hh_mm_none(self):
        with self.assertLogs(level='INFO') as cm:
            dt = format_str_hh_mm(None)
        self.assertIsNone(dt)
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:Unknown error: Parser must be a string or character stream, not NoneType'
        ])

    def test_format_str_hh_mm_empty(self):
        with self.assertLogs(level='INFO') as cm:
            dt = format_str_hh_mm("")
        self.assertIsNone(dt)
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:Failed to parse date: '
        ])

    @patch('helpers.helpers.build')
    def test_load_sheet_success(self, mock_build):
        mock_spreadsheets = MagicMock()
        mock_values = [['A1', 'B1'], ['A2', 'B2']]  # Sample values
        mock_spreadsheets.values().get().execute.return_value = {'values': mock_values}
        mock_service = MagicMock()
        mock_service.spreadsheets.return_value = mock_spreadsheets
        mock_build.return_value = mock_service

        sheet_id = 'sheet_id'
        sheet_range = 'sheet_range'
        result = load_sheet(sheet_id, sheet_range)

        # Assertions
        self.assertEqual(result, mock_values)

#    @patch('helpers.helpers.build')
#    def test_load_sheet_http_error(self, mock_build):
#        mock_service = MagicMock()
#        mock_service.spreadsheets().values().get().execute.side_effect = \
#            HttpError(resp=MagicMock(status=404, ), content='Not Found')
#        mock_build.return_value = mock_service
#
#        sheet_id = 'sheet_id'
#        sheet_range = 'sheet_range'
#        with self.assertLogs(level='INFO') as cm:
#            result = load_sheet(sheet_id, sheet_range)
#
#        self.assertEqual(result, [])
#        self.assertEqual(cm.output, [
#            'ERROR:helpers.helpers:Failed to parse date: '
#        ])

    def test_rows_to_dict_success(self):
        rows = [
            [CONST_GRADE_78, 'Boys', 'Hanover-1', 'Mickey Mouse'],
            [CONST_GRADE_78, 'Girls', 'Hanover-1', 'Dumbo'],
            ['Grade 5/6', 'Boys', 'Hanover-1', 'Bad Coach']
        ]
        expected_result = {
            CONST_GRADE_78: {
                'Boys': {'Hanover-1': 'Mickey Mouse'}, 
                'Girls': {'Hanover-1': 'Dumbo'}
            },
            'Grade 5/6': {
                'Boys': {'Hanover-1': 'Bad Coach'}
            }
        }
        result = rows_to_dict(rows)
        self.assertEqual(result, expected_result)

#    def test_get_referees(self):
#        payload = [{
#            'id': 12345,
#            'no_show': False,
#            'position_name': 'Referee',
#            'no_show_status': None,
#            '_links': {
#                'official': {
#                    'resource-type': 'user',
#                    'href': 'https://api.assignr.com/api/v2/users/12345.json'
#                },
#                'scheduled_official': {
#                    'resource-type': 'user',
#                    'href': 'https://api.assignr.com/api/v2/users/12345.json'
#                },
#                'assignment': {
#                    'resource-type': 'assignment',
#                    'href': 'https://api.assignr.com/api/v2/assignments/123456.json'
#                }
#            }
#        }, {
#            'id': 23456, 'no_show': False,
#            'position_name': 'Asst. Referee', 'no_show_status': None,
#            'created': '2023-10-22T20:05:55.000-04:00',
#            'updated': '2023-10-22T20:05:55.000-04:00',
#            '_links': {}
#        }, {
#            'id': 3881676, 'no_show': False,
#            'position_name': 'Asst. Referee', 'no_show_status': None,
#            'created': '2023-10-22T20:05:55.000-04:00',
#            'updated': '2023-10-22T20:05:55.000-04:00',
#            '_links': {}
#        }]
#        expected_results = [
#            {'no_show': False, 'position': 'Referee', 'first_name': 'Mickey', 'last_name': 'Mouse'},
#
#        ]
#        assignr_mock = MagicMock()
#        assignr_mock.get_referee_information(return_value = {
#            'first_name': 'Mickey',
#            'last_name': 'Mouse',
#            'email_addresses': 'test@example.com',
#            'official': 'test official',
#            'assignor': 'test assignor',
#            'manager': 'test manager',
#            'active': 'true'           
#        })
#        temp = Assignr('123', '234', '345', BASE_URL,
#                       AUTH_URL)
#        with patch('assignr.assignr.Assignr', return_value=assignr_mock):
#            referees = temp.get_referees(payload)
#        self.assertEqual(referees, expected_results)

#    @patch(ASSIGNR_REQUESTS)
#    def test_valid_get_misconduct(self, mock_requests):
#        mock_requests.post.return_value = mock_auth_response
#
#        mock_response = MagicMock()
#        mock_response.status_code = 500
#        mock_response.json.return_value = {}
#
#        mock_requests.get.return_value = mock_response
#
#        temp = Assignr('123', '234', '345', BASE_URL,
#                       AUTH_URL)
#        temp.site_id = 100
#        result = temp.get_misconducts('01/01/2022', '01/01/2022')
#        self.assertEqual(result, [])

    def test_get_match_count_referees(self):
        pattern = r'\.officials\.\d+\.position'
        payload = {
            ".ageGroup": "Grade 1/2",
            ".awayTeam": "2009A-Bolts-Girls",
            ".homeTeam": "2007A-Bolts-Girls",
            ".ejections": "true",
            ".officials.0.name": "Mickey Mouse",
            ".officials.0.grade": None,
            ".officials.0.position": "Referee",
            ".officials.1.name": "Dumbo",
            ".officials.1.grade": None,
            ".officials.1.position": ASST_REFEREE,
            ".officials.2.name": "Pluto",
            ".officials.2.grade": None,
            ".officials.2.position": ASST_REFEREE,
            ".startTime": "2024-04-05T08:00:00-04:00"
        }

        self.assertEqual(3, get_match_count(payload, pattern))

    def test_get_referees_all(self):
        payload = {
            ".ageGroup": "Grade 1/2",
            ".awayTeam": "2009A-Bolts-Girls",
            ".homeTeam": "2007A-Bolts-Girls",
            ".ejections": "true",
            ".officials.0.name": "Mickey Mouse",
            ".officials.0.grade": None,
            ".officials.0.position": "Referee",
            ".officials.1.name": "Dumbo",
            ".officials.1.grade": None,
            ".officials.1.position": ASST_REFEREE,
            ".officials.2.name": "Pluto",
            ".officials.2.grade": None,
            ".officials.2.position": ASST_REFEREE,
            ".startTime": "2024-04-05T08:00:00-04:00"
        }

        expected_results = [{
            "name": "Mickey Mouse",
            "position": "Referee"
        },{
            "name": "Dumbo",
            "position": ASST_REFEREE
        },{
            "name": "Pluto",
            "position": ASST_REFEREE
        }]

        self.assertEqual(expected_results, get_referees(payload))


    def test_get_referees_missing(self):
        payload = {
            ".ageGroup": "Grade 1/2",
            ".awayTeam": "2009A-Bolts-Girls",
            ".homeTeam": "2007A-Bolts-Girls",
            ".ejections": "true",
            ".officials.0.name": "Mickey Mouse",
            ".officials.0.grade": None,
            ".officials.0.position": "Referee",
            ".officials.1.name": NOT_ASSIGNED,
            ".officials.1.grade": None,
            ".officials.1.position": ASST_REFEREE,
            ".startTime": "2024-04-05T08:00:00-04:00"
        }

        expected_results = [{
            "name": "Mickey Mouse",
            "position": "Referee"
        },{
            "name": NOT_ASSIGNED,
            "position": ASST_REFEREE
        },{
            "name": NOT_ASSIGNED,
            "position": ASST_REFEREE
        }]

        self.assertEqual(expected_results, get_referees(payload))

    def test_get_match_count_misconducts(self):
        pattern = r'\.misconductGrid\.\d+\.name'
        payload = {
            ".ageGroup": "Grade 1/2",
            ".awayTeam": "2009A-Bolts-Girls",
            ".homeTeam": "2007A-Bolts-Girls",
            ".ejections": "true",
            ".misconductGrid.0.name": "Homer Simpson",
            ".misconductGrid.0.role": 'player',
            ".misconductGrid.0.team": "home",
            ".misconductGrid.0.minute": "42",
            ".misconductGrid.0.offense": "PO",
            ".misconductGrid.0.description": "Test",
            ".misconductGrid.0.passIdNumber": None,
            ".misconductGrid.0.cautionSendOff": "caution",
            ".misconductGrid.1.name": "Bart Simpson",
            ".misconductGrid.1.role": 'player',
            ".misconductGrid.1.team": "away",
            ".misconductGrid.1.minute": "60",
            ".misconductGrid.1.offense": "DGF",
            ".misconductGrid.1.description": "This is a Test",
            ".misconductGrid.1.passIdNumber": None,
            ".misconductGrid.1.cautionSendOff": "sendOff",
            ".startTime": "2024-04-05T08:00:00-04:00"
        }

        self.assertEqual(2, get_match_count(payload, pattern))

    def test_misconducts_caution_sendoff(self):
        expected_results = [{
            "name": "Homer Simpson",
            "role": "player",
            "team": "home",
            "minute": "42",
            "offense": "PO",
            "description": "Test",
            "pass_number": None,
            "caution_send_off": "caution"
        },{
            "name": "Bart Simpson",
            "role": "player",
            "team": "away",
            "minute": "60",
            "offense": "DGF",
            "description": "This is a Test",
            "pass_number": None,
            "caution_send_off": "sendOff"
        }]
        payload = {
            ".ageGroup": "Grade 1/2",
            ".awayTeam": "2009A-Bolts-Girls",
            ".homeTeam": "2007A-Bolts-Girls",
            ".ejections": "true",
            ".league": "Springfield",
            ".misconductGrid.0.name": "Homer Simpson",
            ".misconductGrid.0.role": 'player',
            ".misconductGrid.0.team": "home",
            ".misconductGrid.0.minute": "42",
            ".misconductGrid.0.offense": "PO",
            ".misconductGrid.0.description": "Test",
            ".misconductGrid.0.passIdNumber": None,
            ".misconductGrid.0.cautionSendOff": "caution",
            ".misconductGrid.1.name": "Bart Simpson",
            ".misconductGrid.1.role": 'player',
            ".misconductGrid.1.team": "away",
            ".misconductGrid.1.minute": "60",
            ".misconductGrid.1.offense": "DGF",
            ".misconductGrid.1.description": "This is a Test",
            ".misconductGrid.1.passIdNumber": None,
            ".misconductGrid.1.cautionSendOff": "sendOff",
            ".startTime": "2024-04-05T08:00:00-04:00"
        }

        self.assertEqual(expected_results, get_misconducts(payload))

    def test_misconducts_caution(self):
        expected_results = [{
            "name": "Homer Simpson",
            "role": "player",
            "team": "home",
            "minute": "42",
            "offense": "PO",
            "description": "Test",
            "pass_number": None,
            "caution_send_off": "caution"
        }]
        payload = {
            ".ageGroup": "Grade 1/2",
            ".awayTeam": "2009A-Bolts-Girls",
            ".homeTeam": "2007A-Bolts-Girls",
            ".ejections": "true",
            ".league": "Springfield",
            ".misconductGrid.0.name": "Homer Simpson",
            ".misconductGrid.0.role": 'player',
            ".misconductGrid.0.team": "home",
            ".misconductGrid.0.minute": "42",
            ".misconductGrid.0.offense": "PO",
            ".misconductGrid.0.description": "Test",
            ".misconductGrid.0.passIdNumber": None,
            ".misconductGrid.0.cautionSendOff": "caution",
            ".startTime": "2024-04-05T08:00:00-04:00"
        }

        self.assertEqual(expected_results, get_misconducts(payload))

    def test_get_valid_coach_name(self):
        coaches = {
            'Grade 7/8': {
                'Boys': {
                    'Isotopes': 'Mr. Burns',
                    'Springfield': 'Homer Simpson'
                }
            }
        }
        result = get_coaches_name(coaches, 'Grade 7/8', 'Boys', 'Springfield')
        self.assertEqual(result, 'Homer Simpson')

    def test_get_invalid_coach_name(self):
        coaches = {
            'Grade 7/8': {
                'Boys': {
                    'Isotopes': 'Mr. Burns',
                    'Springfield': 'Homer Simpson'
                }
            }
        }
        result = get_coaches_name(coaches, 'Grade 7/8', 'Girls', 'Springfield')
        self.assertEqual(result, 'Unknown')
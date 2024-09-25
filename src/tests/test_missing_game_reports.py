from os import environ
from datetime import (datetime, timedelta)
from helpers import constants
from missing_game_reports import get_arguments, main

from unittest import TestCase
from unittest.mock import (patch, MagicMock)

ERROR_USAGE='ERROR:missing_game_reports:USAGE: missing_game_reports.py -s <start-date>' \
    ' -e <end-date> DATE FORMAT=MM/DD/YYYY -r'
DATE_01012020 = '01/01/2020'
DATE_01012021 = '01/01/2021'
DATE_FORMAT_01012020 = datetime.strptime(DATE_01012020, "%m/%d/%Y").date()
DATE_FORMAT_01012021 = datetime.strptime(DATE_01012021, "%m/%d/%Y").date()
START_DATE = 'start_date'
END_DATE = 'end_date'
REFEREE_REMINDER = 'referee_reminder'
CLIENT_SECRET = "client_secret"
CLIENT_ID = "client_id"
CLIENT_SCOPE = "client_scope"
AUTH_URL = "auth_url"
BASE_URL = "base_url"
ADMIN_EMAIL = "admin_email"
MISCONDUCTS_EMAIL = "misconducts_email"
EMAIL_SERVER = "smtp.gmail.com"
EMAIL_PORT = "587"
EMAIL_USERNAME = "email_username"
EMAIL_PASSWORD = "email_password"

class TestGetArguments(TestCase):
    def test_help(self):
        expected_args = {START_DATE: None, END_DATE: None,
                         REFEREE_REMINDER: False}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_valid_options(self):
        expected_args = {
            START_DATE: DATE_FORMAT_01012020,
            END_DATE: DATE_FORMAT_01012021,
            REFEREE_REMINDER: True
        }
        rc, args = get_arguments(['-s', DATE_01012020, '-e', DATE_01012021, '-r'])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_invalid_options(self):
        expected_args = {START_DATE: None, END_DATE: None, REFEREE_REMINDER: False}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-n'])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 77)
        self.assertEqual(args, expected_args)

    def test_missing_start_date(self):
        start_date = DATE_FORMAT_01012020 - timedelta(days=7)

        expected_args = {
            START_DATE: start_date,
            END_DATE: DATE_FORMAT_01012020,
            REFEREE_REMINDER: True
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-e', DATE_01012020, '-r'])
        self.assertEqual(cm.output, [
            "INFO:missing_game_reports:End Date set to 2020-01-01",
            f"INFO:missing_game_reports:No start date provided, setting to {start_date}",
            f"INFO:missing_game_reports:Start Date set to {start_date}"
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_missing_end_date(self):
        end_date = datetime.now().date()
        expected_args = {
            START_DATE: DATE_FORMAT_01012020,
            END_DATE: end_date,
            REFEREE_REMINDER: True
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', DATE_01012020, '-r'])
        self.assertEqual(cm.output, [
            f'INFO:missing_game_reports:No end date provided, setting to {end_date}',
            f'INFO:missing_game_reports:End Date set to {end_date}',
            'INFO:missing_game_reports:Start Date set to 2020-01-01'
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_missing_referee_reminder(self):
        expected_args = {
            START_DATE: DATE_FORMAT_01012020,
            END_DATE: DATE_FORMAT_01012021,
            REFEREE_REMINDER: False
        }
        rc, args = get_arguments(['-s', DATE_01012020, '-e', DATE_01012021])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_date_value_errors(self):
        expected_args = {
            START_DATE: '01-01-1980',
            END_DATE: '01010101',
            REFEREE_REMINDER: False
        }

        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', '01-01-1980', '-e', '01010101'])
        self.assertEqual(cm.output, [
            'ERROR:missing_game_reports:End Date value, 01010101 is invalid',
            'ERROR:missing_game_reports:Start Date value, 01-01-1980 is invalid'
        ])
        self.assertEqual(rc, 88)
        self.assertEqual(args, expected_args)

    def test_start_date_greater_end_date(self):
        end_date = datetime.strptime(DATE_01012020, "%m/%d/%Y").date()
        start_date = datetime.strptime('01/10/2020', "%m/%d/%Y").date()
        expected_args = {
            START_DATE: start_date,
            END_DATE: end_date,
            REFEREE_REMINDER: True
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', '01/10/2020', '-e', DATE_01012020, '-r'])
        self.assertEqual(cm.output, [
            f'INFO:missing_game_reports:End Date set to {end_date}',
            f'INFO:missing_game_reports:Start Date set to {start_date}',
            f'ERROR:missing_game_reports:Start Date {start_date} is after End Date {end_date}'
        ])
        self.assertEqual(rc, 88)
        self.assertEqual(args, expected_args)


class TestMainFunction(TestCase):
    @patch.dict(environ,
        {
            constants.CLIENT_SECRET: CLIENT_SECRET,
            constants.CLIENT_ID: CLIENT_ID,
            constants.CLIENT_SCOPE: CLIENT_SCOPE,
            constants.AUTH_URL: AUTH_URL,
            constants.BASE_URL: BASE_URL,
            constants.EMAIL_SERVER: EMAIL_SERVER,
            constants.EMAIL_PORT: EMAIL_PORT,
            constants.EMAIL_USERNAME: EMAIL_USERNAME,
            constants.EMAIL_PASSWORD: EMAIL_PASSWORD,
            constants.ADMIN_EMAIL: ADMIN_EMAIL,
            constants.MISCONDUCTS_EMAIL: MISCONDUCTS_EMAIL
        }, clear=True)
    @patch('missing_game_reports.get_arguments')
    @patch('assignr.assignr.Assignr')
    @patch('helpers.helpers.get_assignor_information')
    @patch('helpers.helpers.create_message')
    @patch('missing_game_reports.send_email')
    def test_main_success(self, mock_send_email, mock_create_message,
                          mock_get_assignor_information, mock_assignr,
                          mock_get_arguments):
        # Mock return values
        mock_get_arguments.return_value = (0, {'START_DATE': '2023-09-01',
                                               'END_DATE': '2023-09-22', 
                                               'REFEREE_REMINDER': False})
        
        # Mock Assignr instance
        mock_assignr_instance = MagicMock()
        mock_assignr_instance.get_game_ids.return_value = {
            1: {'cancelled': False, 'game_report_url': None, 'home_roster': True, 'away_roster': False}
        }
        mock_assignr_instance.match_games_to_reports.return_value = mock_assignr_instance.get_game_ids.return_value
        mock_assignr.return_value = mock_assignr_instance

        mock_get_assignor_information.return_value = {
            'association_1': [{'email': 'assignor1@example.com'}, {'email': 'assignor2@example.com'}]
        }
        
        mock_create_message.return_value = 'Email Message'
        mock_send_email.return_value = None  # No error

        main()

        mock_get_arguments.assert_called_once()
        mock_assignr_instance.get_game_ids.assert_called_once_with('2023-09-01', '2023-09-22')
        mock_assignr_instance.match_games_to_reports.assert_called_once_with('2023-09-01', '2023-09-22', mock_assignr_instance.get_game_ids.return_value)
        mock_create_message.assert_called()
        mock_send_email.assert_called()

    @patch('missing_game_reports.get_arguments')
    def test_main_get_arguments_failure(self, mock_get_arguments):
        mock_get_arguments.return_value = (1, None)

        with self.assertRaises(SystemExit) as cm:
            main()

        self.assertEqual(cm.exception.code, 1)
        mock_get_arguments.assert_called_once()

    @patch('missing_game_reports.get_arguments')
    @patch('helpers.helpers.get_environment_vars')
    def test_main_get_environment_vars_failure(self, mock_get_env_vars, mock_get_arguments):
        mock_get_arguments.return_value = (0, {'START_DATE': '2023-09-01', 'END_DATE': '2023-09-22', 'REFEREE_REMINDER': False})
        
        mock_get_env_vars.return_value = (1, None)

        with self.assertRaises(SystemExit) as cm:
            main()

        # Assert that the script exits with the correct return code
        self.assertEqual(cm.exception.code, 1)
        mock_get_arguments.assert_called_once()
        mock_get_env_vars.assert_called_once()

    @patch('missing_game_reports.get_arguments')
    @patch('helpers.helpers.get_environment_vars')
    @patch('helpers.helpers.get_email_vars')
    @patch('assignr.assignr.Assignr')
    @patch('helpers.helpers.get_assignor_information')
    @patch('helpers.helpers.create_message')
    @patch('missing_game_reports.send_email')
    def test_main_no_missing_reports(self, mock_send_email, mock_create_message, mock_get_assignor_information, mock_assignr, mock_get_email_vars, mock_get_env_vars, mock_get_arguments, mock_logger):
        # Mock return values
        mock_get_arguments.return_value = (0, {'START_DATE': '2023-09-01', 'END_DATE': '2023-09-22', 'REFEREE_REMINDER': False})
        mock_get_env_vars.return_value = (0, {
            'CLIENT_ID': 'client_id',
            'CLIENT_SECRET': 'client_secret',
            'CLIENT_SCOPE': 'scope',
            'BASE_URL': 'base_url',
            'AUTH_URL': 'auth_url'
        })
        mock_get_email_vars.return_value = (0, 'email_vars')
        
        # Mock Assignr instance
        mock_assignr_instance = MagicMock()
        mock_assignr_instance.get_game_ids.return_value = {
            1: {'cancelled': False, 'game_report_url': 'http://report_url', 'home_roster': True, 'away_roster': True}
        }
        mock_assignr_instance.match_games_to_reports.return_value = mock_assignr_instance.get_game_ids.return_value
        mock_assignr.return_value = mock_assignr_instance

        mock_get_assignor_information.return_value = {
            'association_1': [{'email': 'assignor1@example.com'}, {'email': 'assignor2@example.com'}]
        }
        
        mock_create_message.return_value = 'Email Message'
        mock_send_email.return_value = None  # No error

        main()

        # Assertions
        mock_send_email.assert_called_once()  # No missing reports, so no second email should be sent
        mock_create_message.assert_called()
        mock_logger.info.assert_called_with("Completed Missing Game Report")

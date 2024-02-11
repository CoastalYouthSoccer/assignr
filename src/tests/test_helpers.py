from os import environ
from unittest import TestCase
from unittest.mock import (patch, MagicMock, ANY)
from googleapiclient.errors import HttpError
from helpers.helpers import (get_environment_vars, get_spreadsheet_vars,
                             get_email_vars, format_date_hh_mm,
                             format_date_mm_dd_yyyy, load_sheet,
                             rows_to_dict)

CONST_GRADE_78 = 'Grade 7/8'

class TestHelpers(TestCase):
    @patch.dict(environ,
        {
            "CLIENT_SECRET": "client_secret",
            "CLIENT_ID": "client_id",
            "CLIENT_SCOPE": "client_scope",
            "AUTH_URL": "auth_url",
            "BASE_URL": "base_url"
        }, clear=True)
    def test_environment_set(self):
        expected_results = {
            'CLIENT_SECRET': 'client_secret',
            'CLIENT_ID': 'client_id',
            'CLIENT_SCOPE': 'client_scope',
            'AUTH_URL': 'auth_url',
            'BASE_URL': 'base_url'
        }
        error, result = get_environment_vars()
        self.assertEqual(error, 0)
        self.assertEqual(result, expected_results)

    @patch.dict(environ,
        {
            "CLIENT_ID": "client_id",
            "CLIENT_SCOPE": "client_scope",
            "AUTH_URL": "auth_url",
            "BASE_URL": "base_url"
        }, clear=True)
    def test_missing_client_secret(self):
        expected_results = {
            'CLIENT_SECRET': None,
            'CLIENT_ID': 'client_id',
            'CLIENT_SCOPE': 'client_scope',
            'AUTH_URL': 'auth_url',
            'BASE_URL': 'base_url'
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_environment_vars()
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:CLIENT_SECRET environment variable is missing'
        ])
        self.assertEqual(error, 66)
        self.assertEqual(result, expected_results)

    @patch.dict(environ, {}, clear=True)
    def test_missing_all_environment(self):
        expected_errors = [
            'ERROR:helpers.helpers:CLIENT_SECRET environment variable is missing',
            'ERROR:helpers.helpers:CLIENT_ID environment variable is missing',
            'ERROR:helpers.helpers:CLIENT_SCOPE environment variable is missing',
            'ERROR:helpers.helpers:AUTH_URL environment variable is missing',
            'ERROR:helpers.helpers:BASE_URL environment variable is missing'
        ]
        expected_results = {
            'CLIENT_SECRET': None,
            'CLIENT_ID': None,
            'CLIENT_SCOPE': None,
            'AUTH_URL': None,
            'BASE_URL': None
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_environment_vars()
        self.assertEqual(cm.output, expected_errors)
        self.assertEqual(result, expected_results)
        self.assertEqual(error, 66)

    @patch.dict(environ,
        {
            "SPREADSHEET_ID": "spreadsheet_id",
            "SPREADSHEET_RANGE": "spreadsheet_range",
            "GOOGLE_APPLICATION_CREDENTIALS": "google_credentials"
        }, clear=True)
    def test_spreadsheet_environments_set(self):
        expected_results = {
            "SPREADSHEET_ID": "spreadsheet_id",
            "SPREADSHEET_RANGE": "spreadsheet_range",
            "GOOGLE_APPLICATION_CREDENTIALS": "google_credentials"
        }
        error, result = get_spreadsheet_vars()
        self.assertEqual(error, 0)
        self.assertEqual(result, expected_results)

    @patch.dict(environ,
        {
            "SPREADSHEET_RANGE": "spreadsheet_range",
            "GOOGLE_APPLICATION_CREDENTIALS": "google_credentials"
        }, clear=True)
    def test_spreadsheet_missing_id(self):
        expected_results = {
            "SPREADSHEET_ID": None,
            "SPREADSHEET_RANGE": "spreadsheet_range",
            "GOOGLE_APPLICATION_CREDENTIALS": "google_credentials"
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_spreadsheet_vars()
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:SPREADSHEET_ID environment variable is missing'
        ])
        self.assertEqual(error, 55)
        self.assertEqual(result, expected_results)

    @patch.dict(environ, {}, clear=True)
    def test_missing_all_spreadsheet_vars(self):
        expected_errors = [
            'ERROR:helpers.helpers:GOOGLE_APPLICATION_CREDENTIALS environment variable is missing',
            'ERROR:helpers.helpers:SPREADSHEET_ID environment variable is missing',
            'ERROR:helpers.helpers:SPREADSHEET_RANGE environment variable is missing'
        ]
        expected_results = {
            "SPREADSHEET_ID": None,
            "SPREADSHEET_RANGE": None,
            "GOOGLE_APPLICATION_CREDENTIALS": None
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_spreadsheet_vars()
        self.assertEqual(cm.output, expected_errors)
        self.assertEqual(result, expected_results)
        self.assertEqual(error, 55)

    @patch.dict(environ,
        {
            "EMAIL_SERVER": "email_server",
            "EMAIL_PORT": "587",
            "EMAIL_USERNAME": "email_username",
            "EMAIL_PASSWORD": "email_password",
            "EMAIL_TO": "email_to"
        }, clear=True)
    def test_email_set(self):
        expected_results = {
            'EMAIL_SERVER': 'email_server',
            'EMAIL_PORT': 587,
            'EMAIL_USERNAME': 'email_username',
            'EMAIL_PASSWORD': 'email_password',
            'EMAIL_TO': 'email_to'
        }
        error, result = get_email_vars()
        self.assertEqual(error, 0)
        self.assertEqual(result, expected_results)

    @patch.dict(environ,
        {
            "EMAIL_USERNAME": "email_username",
            "EMAIL_PASSWORD": "email_password",
            "EMAIL_TO": "email_to"
        }, clear=True)
    def test_email_default_values(self):
        expected_results = {
            'EMAIL_SERVER': 'smtp.gmail.com',
            'EMAIL_PORT': 587,
            'EMAIL_USERNAME': 'email_username',
            'EMAIL_PASSWORD': 'email_password',
            'EMAIL_TO': 'email_to'
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_email_vars()
        self.assertEqual(error, 0)
        self.assertEqual(result, expected_results)
        self.assertEqual(cm.output, [
            'INFO:helpers.helpers:EMAIL_SERVER environment variable is missing, defaulting to "smtp.gmail.com"',
            'INFO:helpers.helpers:EMAIL_PORT environment variable is missing, defaulting to 587'
        ])

    @patch.dict(environ,
        {
            "EMAIL_SERVER": "email_server",
            "EMAIL_PORT": "abc",
            "EMAIL_USERNAME": "email_username",
            "EMAIL_PASSWORD": "email_password",
            "EMAIL_TO": "email_to"
        }, clear=True)
    def test_email_invalid_port(self):
        expected_results = {
            'EMAIL_SERVER': 'email_server',
            'EMAIL_PORT': 587,
            'EMAIL_USERNAME': 'email_username',
            'EMAIL_PASSWORD': 'email_password',
            'EMAIL_TO': 'email_to'
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_email_vars()
        self.assertEqual(cm.output, 
            ['ERROR:helpers.helpers:EMAIL_PORT environment variable is not an integer'])
        self.assertEqual(error, 55)
        self.assertEqual(result, expected_results)

    @patch.dict(environ,
        {
            "EMAIL_SERVER": "email_server",
            "EMAIL_PORT": "587"
        }, clear=True)
    def test_email_missing_values(self):
        expected_results = {
            'EMAIL_SERVER': 'email_server',
            'EMAIL_PORT': 587,
            'EMAIL_USERNAME': None,
            'EMAIL_PASSWORD': None,
            'EMAIL_TO': None
        }
        with self.assertLogs(level='INFO') as cm:
            error, result = get_email_vars()
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:EMAIL_USERNAME environment variable is missing',
            'ERROR:helpers.helpers:EMAIL_PASSWORD environment variable is missing',
            'ERROR:helpers.helpers:EMAIL_TO environment variable is missing'
        ])
        self.assertEqual(error, 55)
        self.assertEqual(result, expected_results)

    def test_format_date_mm_dd_yyyy(self):
        dt = format_date_mm_dd_yyyy("2023-10-14T14:47:31.000-04:00")
        self.assertEqual(dt, "10/14/2023")

    def test_format_date_mm_dd_yyyy_none(self):
        with self.assertLogs(level='INFO') as cm:
            dt = format_date_mm_dd_yyyy(None)
        self.assertIsNone(dt)
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:Unknown error: Parser must be a string or character stream, not NoneType'
        ])

    def test_format_date_mm_dd_yyyy_empty(self):
        with self.assertLogs(level='INFO') as cm:
            dt = format_date_mm_dd_yyyy("")
        self.assertIsNone(dt)
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:Failed to parse date: '
        ])

    def test_format_date_hh_mm(self):
        dt = format_date_hh_mm("2023-10-14T14:47:31.000-04:00")
        self.assertEqual(dt, "02:47 PM")

    def test_format_date_hh_mm_none(self):
        with self.assertLogs(level='INFO') as cm:
            dt = format_date_hh_mm(None)
        self.assertIsNone(dt)
        self.assertEqual(cm.output, [
            'ERROR:helpers.helpers:Unknown error: Parser must be a string or character stream, not NoneType'
        ])

    def test_format_date_hh_mm_empty(self):
        with self.assertLogs(level='INFO') as cm:
            dt = format_date_hh_mm("")
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

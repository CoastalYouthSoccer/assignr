from os import environ
from unittest import TestCase
from unittest.mock import patch
from helpers.helpers import (get_environment_vars, get_spreadsheet_vars,
                             get_email_vars)


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
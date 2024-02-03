from os import environ
from unittest import TestCase
from unittest.mock import patch
from helpers.helpers import (get_environment_vars, get_spreadsheet_vars)


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
        self.assertEqual(error, [])
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
        error, result = get_environment_vars()
        self.assertEqual(error,
            ['CLIENT_SECRET environment variable is missing'])
        self.assertEqual(result, expected_results)

    @patch.dict(environ, {}, clear=True)
    def test_missing_all_environment(self):
        expected_error = [
            'CLIENT_SECRET environment variable is missing',
            'CLIENT_ID environment variable is missing',
            'CLIENT_SCOPE environment variable is missing',
            'AUTH_URL environment variable is missing',
            'BASE_URL environment variable is missing'
        ]
        expected_results = {
            'CLIENT_SECRET': None,
            'CLIENT_ID': None,
            'CLIENT_SCOPE': None,
            'AUTH_URL': None,
            'BASE_URL': None
        }
        error, result = get_environment_vars_environment_vars()
        self.assertEqual(result, expected_results)
        self.assertEqual(error, expected_error)

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
        self.assertEqual(error, [])
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
        error, result = get_spreadsheet_vars()
        self.assertEqual(error, [
            'SPREADSHEET_ID environment variable is missing'])
        self.assertEqual(result, expected_results)

    @patch.dict(environ, {}, clear=True)
    def test_missing_all_spreadsheet_vars(self):
        expected_error = [
            'GOOGLE_APPLICATION_CREDENTIALS environment variable is missing',
            'SPREADSHEET_ID environment variable is missing',
            'SPREADSHEET_RANGE environment variable is missing'
        ]
        expected_results = {
            "SPREADSHEET_ID": None,
            "SPREADSHEET_RANGE": None,
            "GOOGLE_APPLICATION_CREDENTIALS": None
        }
        error, result = get_spreadsheet_vars()
        self.assertEqual(result, expected_results)
        self.assertEqual(error, expected_error)

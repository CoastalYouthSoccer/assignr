from os import environ
from unittest import TestCase
from unittest.mock import (patch, MagicMock)
from helpers.helpers import check_environment_vars


class TestHelpers(TestCase):
    @patch.dict(environ,
        {
            "CLIENT_SECRET": "client_secret",
            "CLIENT_ID": "client_id",
            "CLIENT_SCOPE": "client_scope",
            "AUTH_URL": "auth_url",
            "BASE_URL": "base_url"
        }, clear=True)
    def test_all_variables_set(self):    
        result = check_environment_vars()
        self.assertEqual(result, [])

    @patch.dict(environ,
        {
            "CLIENT_ID": "client_id",
            "CLIENT_SCOPE": "client_scope",
            "AUTH_URL": "auth_url",
            "BASE_URL": "base_url"
        }, clear=True)
    def test_missing_client_secret(self):    
        result = check_environment_vars()
        self.assertEqual(result,
            ['CLIENT_SECRET environment variable is missing'])

    @patch.dict(environ, {}, clear=True)
    def test_missing_all_variables(self):
        expected_results = [
            'CLIENT_SECRET environment variable is missing',
            'CLIENT_ID environment variable is missing',
            'CLIENT_SCOPE environment variable is missing',
            'AUTH_URL environment variable is missing',
            'BASE_URL environment variable is missing'
        ]   
        result = check_environment_vars()
        self.assertEqual(result, expected_results)

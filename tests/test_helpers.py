from os import environ
from unittest import TestCase
from unittest.mock import (patch, MagicMock)
from helpers.helpers import (authenticate, get_requests, check_environment_vars, get_site_id)


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

    @patch.dict(environ,
        {
            "CLIENT_SECRET": "client_secret",
            "CLIENT_ID": "client_id",
            "CLIENT_SCOPE": "client_scope",
            "AUTH_URL": "auth_url"
        }, clear=True)
    @patch('helpers.helpers.requests')
    def test_valid_authentication(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'valid_token'
        }
        mock_requests.post.return_value = mock_response
        self.assertEqual(authenticate(), 'valid_token')

    @patch.dict(environ,
        {
            "CLIENT_SECRET": "client_secret",
            "CLIENT_ID": "client_id",
            "CLIENT_SCOPE": "client_scope",
            "AUTH_URL": "auth_url",
            "BASE_URL": "base_url"
        }, clear=True)
    @patch('helpers.helpers.requests')
    def test_invalid_authentication(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_requests.post.return_value = mock_response
        with self.assertLogs(level='INFO') as cm:
            token = authenticate()
        self.assertEqual(token, None)
        self.assertEqual(cm.output, ["ERROR:root:Token not found"])

    @patch.dict(environ,{"BASE_URL": "base_url"}, clear=True)
    @patch('helpers.helpers.requests')
    def test_get_requests(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Homer",
            "city": "Springfield"
        }
        mock_requests.get.return_value = mock_response
        rc, response = get_requests('token','some_endpoint')
        self.assertEqual(rc, 200)
        self.assertEqual(response, {"name": "Homer",
            "city": "Springfield"})

    @patch('helpers.helpers.requests')
    @patch.dict(environ,{"BASE_URL": "base_url"}, clear=True)
    def test_valid_site_id(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            '_embedded': {
                'sites': [{
                    "id": "123",
                    "name": "Test",
                    "sports": ["soccer"]
                }]
            }
        }
        mock_requests.get.return_value = mock_response
        self.assertEqual(get_site_id('token'), '123')

    @patch('helpers.helpers.requests')
    @patch.dict(environ,{"BASE_URL": "base_url"}, clear=True)
    def test_invalid_response_code(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            '_embedded': {
                'sites': [{
                    "id": "123",
                    "name": "Test",
                    "sports": ["soccer"]
                }]
            }
        }
        mock_requests.get.return_value = mock_response
        with self.assertLogs(level='INFO') as cm:
            site_id = get_site_id('token')

        self.assertEqual(site_id, None)
        self.assertEqual(cm.output, ["ERROR:root:Response code 500 returned for get_site_id"])

    @patch('helpers.helpers.requests')
    @patch.dict(environ,{"BASE_URL": "base_url"}, clear=True)
    def test_missing_site_id(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            '_embedded': {
                'sites': [{
                    "name": "Test",
                    "sports": ["soccer"]
                }]
            }
        }
        mock_requests.get.return_value = mock_response
        with self.assertLogs(level='INFO') as cm:
            site_id = get_site_id('token')

        self.assertEqual(site_id, None)
        self.assertEqual(cm.output, ["ERROR:root:Site id not found"])

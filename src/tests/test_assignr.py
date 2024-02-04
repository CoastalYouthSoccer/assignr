from unittest import TestCase
from unittest.mock import (patch, MagicMock)
from assignr.assignr import Assignr

ACCESS_TOKEN = "b445409253438a096fc2990740e4f"

mock_auth_response = MagicMock()
mock_auth_response.status_code = 200
mock_auth_response.json.return_value = {
    "access_token": ACCESS_TOKEN,
    "token_type": "Bearer",
    "scope": "read",
    "created_at": 1606420331
}


class TestAssignr(TestCase):
    def test_valid_init(self):
        temp = Assignr('123', '234', '345', 'https://base.com',
                       'https://auth.com')
        self.assertEqual(temp.client_id, '123')
        self.assertEqual(temp.client_secret, '234')
        self.assertEqual(temp.client_scope, '345')
        self.assertEqual(temp.base_url, 'https://base.com')
        self.assertEqual(temp.auth_url, 'https://auth.com')
        self.assertIsNone(temp.site_id)
        self.assertIsNone(temp.token)

    @patch('assignr.assignr.requests')
    def test_valid_authentication(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        temp = Assignr('123', '234', '345', 'https://base.com',
                       'https://auth.com')
        temp.authenticate()
        self.assertEqual(temp.token, ACCESS_TOKEN)

    @patch('assignr.assignr.requests')
    def test_invalid_authentication(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token_type": "Bearer",
            "scope": "read",
            "created_at": 1606420331
        }
        mock_requests.post.return_value = mock_response

        temp = Assignr('123', '234', '345', 'https://base.com',
                       'https://auth.com')
        with self.assertLogs(level='INFO') as cm:
            temp.authenticate()
        self.assertEqual(cm.output, ["ERROR:root:Token not found"])
        self.assertIsNone(temp.token)

    @patch('assignr.assignr.requests')
    def test_valid_site_id(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "page": {
                "records": 1,
                "pages": 1,
                "current_page": 1,
                "limit": 50
            },
            "_embedded": {
                "sites": [
                    {
                        "id": 123456,
                        "name": "Test League",
                        "show_game_requests": "false",
                        "show_unassigned_games": "true",
                        "show_all_games": "false",
                        "show_game_reports": "true",
                        "forms_enabled": "false",
                        "sports": [
                            "soccer"
                        ]
                    }
                ]
            },
            "_links": {
                "self": {
                    "href": "https://api.assignr.com/v2/sites?page=1"
                }
            }
        }

        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', 'https://base.com',
                       'https://auth.com')
        temp.get_site_id()
        self.assertEqual(temp.site_id, 123456)

    @patch('assignr.assignr.requests')
    def test_invalid_site_id(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "page": {
                "records": 1,
                "pages": 1,
                "current_page": 1,
                "limit": 50
            },
            "_links": {
                "self": {
                    "href": "https://api.assignr.com/v2/sites?page=1"
                }
            }
        }

        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', 'https://base.com',
                       'https://auth.com')
        with self.assertLogs(level='INFO') as cm:
            temp.get_site_id()
        self.assertEqual(cm.output, ["ERROR:root:Site id not found"])
        self.assertIsNone(temp.site_id)

    @patch('assignr.assignr.requests')
    def test_valid_referee_information(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1234,
            "last_name": "Mickey",
            "first_name": "Mouse",
            "mobile_phone": "(111) 222-3333",
            "home_phone_is_public": "false",
            "work_phone_is_public": "false",
            "mobile_phone_is_public": "true",
            "official": "true",
            "assignor": "false",
            "manager": "false",
            "active": "true",
            "email_addresses": [
                "mickey.mouse@gmail.com"
            ],
            "created": "2023-11-05T15:07:42.000-05:00",
            "updated": "2024-02-01T19:55:00.000-05:00",
            "_links": {
                "self": {
                    "resource-type": "user",
                    "href": "https://api.assignr.com/api/v2/users/1234.json"
                },
                "avatar_square": {
                    "resource-type": "avatar",
                    "href": "https://app.assignr.com/photo/d16ef976637a7d3d26ec794c6e6eb8987ad4b48618bd83c2929fd7407c77fa0d??size=300"
                },
                "games": {
                    "href": "https://api.assignr.com/api/v2/users/1234/games.json"
                },
                "avatar_original": {
                    "resource-type": "avatar",
                    "href": "https://app.assignr.com/photo/d16ef976637a7d3d26ec794c6e6eb8987ad4b48618bd83c2929fd7407c77fa0d??size=800"
                },
                "avatar_icon": {
                    "resource-type": "avatar",
                    "href": "https://app.assignr.com/photo/d16ef976637a7d3d26ec794c6e6eb8987ad4b48618bd83c2929fd7407c77fa0d??size=64"
                }
            },
            "_embedded": {
                "site": {
                    "id": 1234,
                    "name": "Soccer League",
                    "created": "2023-01-19T19:19:43.000-05:00",
                    "updated": "2024-02-01T00:02:13.000-05:00",
                    "_links": {
                        "self": {
                            "resource-type": "site",
                            "href": "https://api.assignr.com/api/v2/sites/1234.json"
                        }
                    }
                }
            }
        }

        mock_requests.get.return_value = mock_response

        expected_result = {
            "last_name": "Mickey",
            "first_name": "Mouse",
            "active": "true",
            "official": "true",
            "assignor": "false",
            "manager": "false",
            "email_addresses": [
                "mickey.mouse@gmail.com"
            ]
        }
        temp = Assignr('123', '234', '345', 'https://base.com',
                       'https://auth.com')
        result = temp.get_referee_information('referee')
        self.assertEqual(result, expected_result)

    @patch('assignr.assignr.requests')
    def test_invalid_referee_information(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}

        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', 'https://base.com',
                       'https://auth.com')
        with self.assertLogs(level='INFO') as cm:
            result = temp.get_referee_information('referee')
        self.assertEqual(cm.output, ["ERROR:root:Failed to get referee information: 500"])
        self.assertEqual(result, {})

#    @patch('assignr.assignr.requests')
#    def test_valid_get_misconduct(self, mock_requests):
#        mock_requests.post.return_value = mock_auth_response
#
#        mock_response = MagicMock()
#        mock_response.status_code = 500
#        mock_response.json.return_value = {}
#
#        mock_requests.get.return_value = mock_response
#
#        temp = Assignr('123', '234', '345', 'https://base.com',
#                       'https://auth.com')
#        temp.site_id = 100
#        result = temp.get_misconducts('01/01/2022', '01/01/2022')
#        self.assertEqual(result, [])

    @patch('assignr.assignr.requests')
    def test_invalid_get_misconduct(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}

        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', 'https://base.com',
                       'https://auth.com')
        temp.site_id = 100
        with self.assertLogs(level='INFO') as cm:
            result = temp.get_misconducts('01/01/2022', '01/01/2022')
        self.assertEqual(cm.output, ["ERROR:root:Failed to get misconducts: 500"])
        self.assertEqual(result, [])

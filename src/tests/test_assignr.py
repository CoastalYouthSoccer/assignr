from unittest import TestCase
from unittest.mock import (patch, MagicMock)
from assignr.assignr import Assignr

ACCESS_TOKEN = "ACCESS_TOKEN"
BASE_URL = "https://base.com"
AUTH_URL = "https://auth.com"
ASSIGNR_REQUESTS ="assignr.assignr.requests"

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
        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        self.assertEqual(temp.client_id, '123')
        self.assertEqual(temp.client_secret, '234')
        self.assertEqual(temp.client_scope, '345')
        self.assertEqual(temp.base_url, BASE_URL)
        self.assertEqual(temp.auth_url, AUTH_URL)
        self.assertIsNone(temp.site_id)
        self.assertIsNone(temp.token)

    @patch(ASSIGNR_REQUESTS)
    def test_valid_authentication(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        temp.authenticate()
        self.assertEqual(temp.token, ACCESS_TOKEN)

    @patch(ASSIGNR_REQUESTS)
    def test_invalid_authentication(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token_type": "Bearer",
            "scope": "read",
            "created_at": 1606420331
        }
        mock_requests.post.return_value = mock_response

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        with self.assertLogs(level='INFO') as cm:
            temp.authenticate()
        self.assertEqual(cm.output, ["ERROR:root:Token not found"])
        self.assertIsNone(temp.token)

    @patch(ASSIGNR_REQUESTS)
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

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        temp.get_site_id()
        self.assertEqual(temp.site_id, 123456)

    @patch(ASSIGNR_REQUESTS)
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

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        with self.assertLogs(level='INFO') as cm:
            temp.get_site_id()
        self.assertEqual(cm.output, ["ERROR:root:Site id not found"])
        self.assertIsNone(temp.site_id)

    @patch(ASSIGNR_REQUESTS)
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
        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        result = temp.get_referee_information('referee')
        self.assertEqual(result, expected_result)

    @patch(ASSIGNR_REQUESTS)
    def test_invalid_referee_information(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}

        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        with self.assertLogs(level='INFO') as cm:
            result = temp.get_referee_information('referee')
        self.assertEqual(cm.output, ["ERROR:root:Failed to get referee information: 500"])
        self.assertEqual(result, {})

#    def test_get_referees(self):
#        payload = [{
#            'id': 3881670, 'no_show': False,
#            'position_name': 'Referee', 'no_show_status': None,
#            'created': '2023-10-22T20:05:55.000-04:00',
#            'updated': '2023-10-22T20:05:55.000-04:00',
#            '_links': {
#                'officials': {
#                    'resource-type': 'user',
#                    'href': 'https://api.assignr.com/api/v2/users/996657.json'
#                },
#                'scheduled_official': {
#                    'resource-type': 'user',
#                    'href': 'https://api.assignr.com/api/v2/users/996657.json'
#                }
#            }
#        }, {
#            'id': 3881673, 'no_show': False,
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
#        temp = Assignr('123', '234', '345', BASE_URL,
#                       AUTH_URL)
#        referees = temp.get_referees(payload)
#        self.assertIsInstance(referees, list)

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

    @patch(ASSIGNR_REQUESTS)
    def test_invalid_get_misconduct(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}

        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        temp.site_id = 100
        with self.assertLogs(level='INFO') as cm:
            result = temp.get_misconducts('01/01/2022', '01/01/2022')
        self.assertEqual(cm.output, ["ERROR:root:Failed to get misconducts: 500"])
        self.assertEqual(result, [])

    @patch(ASSIGNR_REQUESTS)
    def test_valid_get_availability(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "page": {
                "records": 3,
                "pages": 1,
                "current_page": 1,
                "limit": 200
            },
            "_embedded": {
                "availability": [
                    {
                        "id": 7518668545,
                        "date": "2024-02-10",
                        "all_day": "true",
                        "description": "all day",
                        "created": "2024-02-04T19:52:21.000-05:00"
                    },
                    {
                        "id": 7518669171,
                        "date": "2024-02-17",
                        "all_day": "false",
                        "description": "8a-11a",
                        "start_time": "8:00 AM",
                        "end_time": "11:00 AM",
                        "created": "2024-02-04T19:53:53.000-05:00",
                        "updated": "2024-02-04T19:54:23.000-05:00"
                    },
                    {
                        "id": 75186694755,
                        "date": "2024-02-17",
                        "all_day": "false",
                        "description": "4p-8p",
                        "start_time": "4:00 PM",
                        "end_time": "8:00 PM",
                        "created": "2024-02-04T19:54:23.000-05:00",
                        "updated": "2024-02-04T19:54:23.000-05:00"
                    }
                ]
            },
            "_links": {
                "self": {
                    "href": "https://api.assignr.com/v2/users/12345/availability?page=1&search%5Bend_date%5D=02%2F29%2F2024&search%5Bstart_date%5D=01%2F01%2F2024"
                }
            }
        }

        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        temp.site_id = 100
        result = temp.get_availability(12345, '01/01/2024', '02/28/2024')
        self.assertEqual(result, [
            {'date': '2024-02-10', 'avail': 'ALL DAY'},
            {'date': '2024-02-17', 'avail': '8:00 AM - 11:00 AM'},
            {'date': '2024-02-17', 'avail': '4:00 PM - 8:00 PM'}
        ])

    @patch(ASSIGNR_REQUESTS)
    def test_valid_get_availability_404_code(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {}

        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        temp.site_id = 100
        with self.assertLogs(level='INFO') as cm:
            result = temp.get_availability(123, '01/01/2022', '01/01/2022')
        self.assertEqual(cm.output, ["WARNING:assignr.assignr:User: 123 has no availability"])
        self.assertEqual(result, [])

    @patch(ASSIGNR_REQUESTS)
    def test_valid_get_availability_500_code(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}

        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        temp.site_id = 100
        with self.assertLogs(level='INFO') as cm:
            result = temp.get_availability(123, '01/01/2022', '01/01/2022')
        self.assertEqual(cm.output, ["ERROR:assignr.assignr:Failed return code: 500 for user: 123"])
        self.assertEqual(result, [])

    @patch(ASSIGNR_REQUESTS)
    def test_valid_get_availability_key_error(self, mock_requests):
        mock_requests.post.return_value = mock_auth_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "page": {
                "records": 3,
                "pages": 1,
                "current_page": 1,
                "limit": 200
            },
            "_embedded": {
                "availability": [
                    {
                        "id": 7518668545,
                        "date": "2024-02-10",
                        "description": "all day",
                        "created": "2024-02-04T19:52:21.000-05:00"
                    },
                    {
                        "id": 7518669171,
                        "date": "2024-02-17",
                        "description": "8a-11a",
                        "start_time": "8:00 AM",
                        "end_time": "11:00 AM",
                        "created": "2024-02-04T19:53:53.000-05:00",
                        "updated": "2024-02-04T19:54:23.000-05:00"
                    },
                    {
                        "id": 75186694755,
                        "date": "2024-02-17",
                        "description": "4p-8p",
                        "start_time": "4:00 PM",
                        "end_time": "8:00 PM",
                        "created": "2024-02-04T19:54:23.000-05:00",
                        "updated": "2024-02-04T19:54:23.000-05:00"
                    }
                ]
            },
            "_links": {
                "self": {
                    "href": "https://api.assignr.com/v2/users/12345/availability?page=1&search%5Bend_date%5D=02%2F29%2F2024&search%5Bstart_date%5D=01%2F01%2F2024"
                }
            }
        }
        mock_requests.get.return_value = mock_response

        temp = Assignr('123', '234', '345', BASE_URL,
                       AUTH_URL)
        temp.site_id = 100
        with self.assertLogs(level='INFO') as cm:
            result = temp.get_availability(123, '01/01/2022', '01/01/2022')
        self.assertEqual(cm.output, 
            ["ERROR:assignr.assignr:Key: 'all_day', missing from Availability response"])
        self.assertEqual(result, [])
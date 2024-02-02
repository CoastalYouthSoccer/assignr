from os import environ
import requests
import logging

logger = logging.getLogger(__name__)


class Assignr:
    def __init__(self, client_id, client_secret, client_scope,
                 base_url, auth_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_scope = client_scope
        self.base_url = base_url
        self.auth_url = auth_url
        self.site_id = None
        self.token = None

    def get_site_id(self) -> None:
        rc, response = self.get_requests('/current_account')
        try:
            if rc == 200:
                self.site_id = response['_embedded']['sites'][0]['id']
            else:
                logging.error(f"Response code {rc} returned for get_site_id")     
        except (KeyError, TypeError):
            logging.error('Site id not found')
                                                                                           
    def authenticate(self) -> None:
        form_data = {
            'client_secret': self.client_secret,
            'client_id': self.client_id,
            'scope': self.client_scope,
            'grant_type': 'client_credentials'
        }

        authenticate = requests.post(environ['AUTH_URL'], data=form_data)

        try:
            self.token = authenticate.json()['access_token']
        except (KeyError, TypeError):
            logging.error('Token not found')
            self.token = None


    def get_requests(self, end_point, params=None):
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {self.token}'
        }

        # Logic manages pagination url
        if environ['BASE_URL'] in end_point:
            response = requests.get(end_point, headers=headers, params=params)
        else:
            response = requests.get(f"{environ['BASE_URL']}{end_point}", headers=headers, params=params)
        return response.status_code, response.json()

    def get_referee_information(self, endpoint):
        referee = {}

        status_code, response = self.get_requests(self.token,
                                                  endpoint)

        if status_code != 200:
            logger.error(f'Failed to get referee information: {status_code}')
            return referee

        referee = {
            'first_name': response['first_name'],
            'last_name': response['last_name'],
            'email_addresses': response['email_addresses'],
            'official': response['official'],
            'assignor': response['assignor'],
            'manager': response['manager'],
            'active': response['active']
        }

        return referee

    def get_misconducts(self, start_dt, end_dt):
        misconducts = []

        params = {
            'search[start_date]': start_dt,
            'search[end_date]': end_dt
        }

        status_code, response = self.get_requests(self.token,
                                                  f'sites/{self.site_id}/game_reports',
                                                  params=params)

        if status_code != 200:
            logger.error(f'Failed to get misconducts: {status_code}')
            return misconducts

        try:
            for item in response['_embedded']['game_reports']:
                if item['misconduct']:
                    referees = []
                    for official in item['_embedded']['officials']:
                        ref_info = self.get_referee_information(
                            official['_links']['official']['href'])
                        referees.append({
                            'no_show': official['no_show'],
                            'position': official['position'],
                            'first_name': ref_info['first_name'],
                            'last_name': ref_info['last_name']
                        })
                    misconducts.append({
                        'date': item['date'],
                        'home_team_score': item['home_team_score'],
                        'away_team_score': item['away_team_score'],
                        'text': item['text'],
                        'officials': referees,
                        'author': {
                            'first_name': item["_embedded"]["author"]["first_name"],
                            'last_name': item["_embedded"]["author"]["last_name"]
                        },
                        'game': {
                            'id': item["_embedded"]["game"]["id"],
                            'start_time': item["_embedded"]["game"]["start_time"],
                            'home_team': item["_embedded"]["game"]["home_team"],
                            'away_team': item["_embedded"]["game"]["away_team"],
                            'age_group': item["_embedded"]["game"]["age_group"],
                            'venue': item["_embedded"]["game"]["venue"],
                            'sub_venue': item["_embedded"]["game"]["subvenue"],
                            'game_type': item["_embedded"]["game"]["game_type"]
                        }
                    })

        except KeyError as ke:
            logger.error(f"Key: {ke}, missing from Game Report response")

        return misconducts

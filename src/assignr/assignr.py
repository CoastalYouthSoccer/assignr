import requests
import logging

logger = logging.getLogger(__name__)

def get_game_information(payload):
    return {
        'id': payload["id"],
        'date': payload["localized_date"],
        'time': payload["localized_time"],
        'start_time': payload["start_time"],
        'home_team': payload["home_team"],
        'away_team': payload["away_team"],
        'age_group': payload["age_group"],
        'venue': payload["venue"],
        'sub_venue': payload["subvenue"],
        'game_type': payload["game_type"]
    }


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

    def authenticate(self) -> None:
        form_data = {
            'client_secret': self.client_secret,
            'client_id': self.client_id,
            'scope': self.client_scope,
            'grant_type': 'client_credentials'
        }

        authenticate = requests.post(self.auth_url, data=form_data)

        try:
            self.token = authenticate.json()['access_token']
        except (KeyError, TypeError):
            logging.error('Token not found')
            self.token = None

    def get_site_id(self) -> None:
        rc, response = self.get_requests('/sites')
        try:
            if rc == 200:
                self.site_id = response['_embedded']['sites'][0]['id']
            else:
                logging.error(f"Response code {rc} returned for get_site_id")     
        except (KeyError, TypeError):
            logging.error('Site id not found')

    def get_requests(self, end_point, params=None):
        if not self.token:
            self.authenticate()

        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {self.token}'
        }

        # Logic manages pagination url
        if self.base_url in end_point:
            response = requests.get(end_point, headers=headers, params=params)
        else:
            response = requests.get(f"{self.base_url}{end_point}", headers=headers, params=params)
        return response.status_code, response.json()

    def get_referees(self, payload):
        referees = []
        for official in payload:
            referee = {
                'no_show': official['no_show'],
                'position': official['position_name'],
                'first_name': None,
                'last_name': None
            }
# Checks to see if official was assigned. Usually happens when a full crew
# isn't available. Aka: Only a center is available.
            if 'official' in official['_links']:
                ref_info = self.get_referee_information(
                            official['_links']['official']['href'])
                referee['first_name'] = ref_info['first_name']
                referee['last_name'] = ref_info['last_name']
                referees.append(referee)
        return referees

    def get_referee_information(self, endpoint):
        if not self.token:
            self.authenticate()

        referee = {}

        status_code, response = self.get_requests(endpoint)

        if status_code != 200:
            logging.error(f'Failed to get referee information: {status_code}')
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

        if self.site_id is None:
            self.get_site_id()

        status_code, response = self.get_requests(f'sites/{self.site_id}/game_reports',
                                                  params=params)

        if status_code != 200:
            logging.error(f'Failed to get misconducts: {status_code}')
            return misconducts

        try:
            for item in response['_embedded']['game_reports']:
                if item['misconduct']:
                    referees = self.get_referees(item['_embedded']['officials'])
                    game_info = get_game_information(item["_embedded"]["game"])
                    misconducts.append({
                        'home_team_score': item['home_team_score'],
                        'away_team_score': item['away_team_score'],
                        'text': item['text'],
                        'officials': referees,
                        'author': {
                            'first_name': item["_embedded"]["author"]["first_name"],
                            'last_name': item["_embedded"]["author"]["last_name"]
                        },
                        'game': game_info
                    })

        except KeyError as ke:
            logging.error(f"Key: {ke}, missing from Game Report response")

        return misconducts

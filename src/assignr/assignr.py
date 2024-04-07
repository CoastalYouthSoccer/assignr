from datetime import datetime
import requests
import logging
import re
from helpers.helpers import (format_date_yyyy_mm_dd, set_boolean_value)

logger = logging.getLogger(__name__)

START_TIME = '.startTime'
NOT_ASSIGNED = "Not Assigned"
SEARCH_START_DT = "search[start_date]"
SEARCH_END_DT = "search[end_date]"
ADMIN_REVIEW = ".adminReview"
ADMIN_NARRATIVE = ".adminNarrative"
CREW_CHANGES = ".crewChanges"
NARRATIVE = ".narrative"

def get_match_count(data, match):
    pattern = re.compile(match)

    return sum(1 for key in data.keys() if pattern.match(key))

def get_referees(payload):
    pattern = r'\.officials\.\d+\.position'
    found_cnt = get_match_count(payload, pattern)
    results = []
    for cnt in range(found_cnt):
        results.append({
            "name": payload[f'.officials.{cnt}.name'],
            "position": payload[f'.officials.{cnt}.position']
        })

# Make sure three referees are in the dictionary. Assumes missing positions are ARs
    for cnt in range(found_cnt, 3):
        results.append({
            "name": NOT_ASSIGNED,
            "position": "Asst. Referee"
        })
    return results

def get_misconducts(payload):
    pattern = r'\.misconductGrid\.\d+\.name'
    found_cnt = get_match_count(payload, pattern)
    results = []
    for cnt in range(found_cnt):
        results.append({
            "name": payload[f'.misconductGrid.{cnt}.name'],
            "role": payload[f'.misconductGrid.{cnt}.role'],
            "team": payload[f'.misconductGrid.{cnt}.team'],
            "minute": payload[f'.misconductGrid.{cnt}.minute'],
            "offense": payload[f'.misconductGrid.{cnt}.offense'],
            "description": payload[f'.misconductGrid.{cnt}.description'],
            "pass_number": payload[f'.misconductGrid.{cnt}.passIdNumber'],
            "caution_send_off": payload[f'.misconductGrid.{cnt}.cautionSendOff']
        })

    return results

def get_game_information(payload):
    return {
        'id': payload["id"],
        'date': payload["localized_date"],
        'time': payload["localized_time"],
        'start_time': payload["start_time"],
        'home_team': payload["home_team"],
        'away_team': payload["away_team"],
        'age_group': payload["age_group"],
        'league': payload["league"],
        'venue': payload["venue"],
        'gender': payload["gender"],
        'sub_venue': payload["subvenue"],
        'game_type': payload["game_type"],
    }

def process_game_report(data):
    result = None
    if ADMIN_REVIEW not in data:
        if data[NARRATIVE]:
            data[ADMIN_REVIEW] = 'True'
        else:
            data[ADMIN_REVIEW] = None

    if ADMIN_NARRATIVE not in data:
        data[ADMIN_NARRATIVE] = None

    if CREW_CHANGES not in data:
        data[CREW_CHANGES] = None

    try:
        result = {
            "admin_review": set_boolean_value(data[ADMIN_REVIEW]),
            "misconduct": set_boolean_value(data['.misconductCheckbox']),
            'assignments_correct': set_boolean_value(data['.assignmentsCorrect']),
            'home_team_score': data['.homeTeamScore'],
            'away_team_score': data['.awayTeamScore'],
            'officials': get_referees(data),
            'author': data['.author_name'],
            'game_dt': data[START_TIME],
            'home_team': data['.homeTeam'],
            'away_team': data['.awayTeam'],
            'venue_subvenue': data['.venue'],
            'league': data['.league'],
            'age_group': data['.ageGroup'],
            'gender': data['.gender'],
            'misconducts': get_misconducts(data),
            'home_coach': 'Unknown',
            'away_coach': 'Unknown',
            'narrative': data[NARRATIVE],
            'ejections': set_boolean_value(data['.ejections']),
            'admin_narrative': data[ADMIN_NARRATIVE],
            'crewChanges': data[CREW_CHANGES]
        }

    except KeyError as ke:
        logging.error(f"Key: {ke}, missing from process_game_report")

    return result


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

    def get_referees_by_assignments(self, payload):
        referees = []
        first_name = None
        last_name = None
        for official in payload:
            if '_embedded' in official and \
                'official' in official['_embedded']:
                first_name = official['_embedded']['official']['first_name']
                last_name = official['_embedded']['official']['last_name']
            referees.append({
                'accepted': official['accepted'],
                'position': official['position'],
                'first_name': first_name,
                'last_name': last_name
            })
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

    def get_reports(self, start_dt, end_dt):
        if not self.token:
            self.authenticate()

        misconducts = []
        admin_reports = []
        assignor_reports = []
        page_nbr = 1
        more_rows = True

        reports = {
            "misconducts": misconducts,
            "admin_reports": admin_reports,
            'assignor_reports': assignor_reports
        }

        if self.site_id is None:
            self.get_site_id()

# Change from 108 to 1002 when CYSL game report implemented.
        while more_rows:
            params = {
                'page': page_nbr,
                SEARCH_START_DT: start_dt,
                SEARCH_END_DT: end_dt
            }
            status_code, response = self.get_requests('form/templates/108/submissions',
                                                      params=params)    
            if status_code != 200:
                logging.error(f'Failed to get reports: {status_code}')
                more_rows = False
                return reports

            try:
                total_pages = response['page']['pages']
                for item in response['_embedded']['form_submissions']:
                    data_dict = {}
                    for data in item['_embedded']['values']:
                        data_dict[data['key']] = data['value']

                    data_dict[START_TIME] = datetime.fromisoformat(data_dict[START_TIME])
                    data_dict['.author_name'] = item['author_name']
                    result = process_game_report(data_dict)
                    if result['admin_review']:
                        reports['admin_reports'].append(result)
                    if result['misconduct']:
                        reports['misconducts'].append(result)
                    if result['assignments_correct'] == False:
                        reports['assignor_reports'].append(result)

            except KeyError as ke:
                logging.error(f"Key: {ke}, missing from Game Report response")

            page_nbr += 1
            if page_nbr > total_pages:
                more_rows = False

        return reports

    def get_availability(self, user_id, start_dt, end_dt):
        availability = []
        params = {
           'user_id': user_id,
           SEARCH_START_DT: start_dt,
           SEARCH_END_DT: end_dt
       }

        status_code, response = self.get_requests(
            f'users/{user_id}/availability', params=params)

        if status_code == 404:
            logger.warning(f'User: {user_id} has no availability')
            return availability

        if status_code != 200:
            logger.error(f'Failed return code: {status_code} for user: {user_id}')
            return availability

        try:
            for avail in response['_embedded']['availability']:
                if avail['all_day'] == 'true':
                    availability.append({
                        'date': avail['date'],
                        'avail': 'ALL DAY'                 
                    })
                else:
                    availability.append({
                        'date': avail['date'],
                        'avail': f"{avail['start_time']} - {avail['end_time']}"                 
                    })

        except KeyError as ke:
            logger.error(f"Key: {ke}, missing from Availability response")

        return availability

    def get_league_games(self, league, start_dt, end_dt):
        results = []

        params = {
            SEARCH_START_DT: format_date_yyyy_mm_dd(start_dt),
            SEARCH_END_DT: format_date_yyyy_mm_dd(end_dt)
        }

        if self.site_id is None:
            self.get_site_id()

        status_code, response = self.get_requests(f'sites/{self.site_id}/games',
                                                  params=params)

        if status_code != 200:
            logging.error(f'Failed to get games: {status_code}')
            return results

        try:
            for item in response['_embedded']['games']:
                if item['league'] == league:
                    sub_item = item["_embedded"]
                    assignor = f'{sub_item["assignor"]["first_name"]}' \
                        f' {sub_item["assignor"]["last_name"]}'
                    referees = self.get_referees_by_assignments(sub_item['assignments'])
                    results.append({
                        'officials': referees,
                        'game_date': item["localized_date"],
                        'game_time': item["localized_time"],
                        'home_team': item["home_team"],
                        'away_team': item["away_team"],
                        'venue': sub_item["venue"]["name"],
                        'sub_venue': item["subvenue"],
                        'game_type': item["game_type"],
                        'age_group': item["age_group"],
                        'gender': item["gender"],
                        'assignor': assignor
                    })

        except KeyError as ke:
            logging.error(f"Key: {ke}, missing from Game response")

        return results

    def get_assignors(self):
        results = []
        if not self.token:
            self.authenticate()

        page_nbr = 1
        more_rows = True

        if self.site_id is None:
            self.get_site_id()

        while more_rows:
            status_code, response = self.get_requests(f'sites/{self.site_id}/users',
                                                      params={'page': page_nbr})
            if status_code != 200:
                logging.error(f'Failed to get reports: {status_code}')
                more_rows = False
                return results

            try:
                total_pages = response['page']['pages']
                for item in response['_embedded']['users']:
                    if item['assignor'] and item['active']:
                        results.append({
                            'first_name': item['first_name'],
                            'last_name': item['last_name'],
                            'email': item['email_addresses'][0]
                        })

            except KeyError as ke:
                logging.error(f"Key: {ke}, missing from Game Report response")

            page_nbr += 1
            if page_nbr > total_pages:
                more_rows = False

        return results
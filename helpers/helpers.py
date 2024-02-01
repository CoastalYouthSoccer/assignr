from os import environ
import requests
import logging

def check_environment_vars():
    errors = []

    try:
        _ = environ['CLIENT_SECRET']
    except KeyError:
        errors.append('CLIENT_SECRET environment variable is missing')

    try:
        _ = environ['CLIENT_ID']
    except KeyError:
        errors.append('CLIENT_ID environment variable is missing')

    try:
        _ = environ['CLIENT_SCOPE']
    except KeyError:
        errors.append('CLIENT_SCOPE environment variable is missing')

    try:
        _ = environ['AUTH_URL']
    except KeyError:
        errors.append('AUTH_URL environment variable is missing')

    try:
        _ = environ['BASE_URL']
    except KeyError:
        errors.append('BASE_URL environment variable is missing')

    return errors

def get_site_id(token) -> str:
    site_id = None
    rc, response = get_requests(token, '/current_account')
    try:
        if rc == 200:
            site_id = response['_embedded']['sites'][0]['id']
        else:
            logging.error(f"Response code {rc} returned for get_site_id")     
    except (KeyError, TypeError):
        logging.error('Site id not found')
    return site_id
                                                                                           
def authenticate():
    form_data = {
        'client_secret': environ['CLIENT_SECRET'],
        'client_id': environ['CLIENT_ID'],
        'scope': environ['CLIENT_SCOPE'],
        'grant_type': 'client_credentials'
    }

    authenticate = requests.post(environ['AUTH_URL'], data=form_data)

    try:
        token = authenticate.json()['access_token']
    except (KeyError, TypeError):
        logging.error('Token not found')
        token = None

    return token

def get_requests(token, end_point, params=None):
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}'
    }

# Logic manages pagination url
    if environ['BASE_URL'] in end_point:
        response = requests.get(end_point, headers=headers, params=params)
    else:
        response = requests.get(f"{environ['BASE_URL']}{end_point}", headers=headers, params=params)
    return response.status_code, response.json()

from os import environ
import logging

logger = logging.getLogger(__name__)

def check_environment_vars():
    errors = []
    env_vars = {
        'CLIENT_SECRET': None,
        'CLIENT_ID': None,
        'CLIENT_SCOPE': None,
        'AUTH_URL': None,
        'BASE_URL': None
    }

    try:
        env_vars['CLIENT_SECRET'] = environ['CLIENT_SECRET']
    except KeyError:
        errors.append('CLIENT_SECRET environment variable is missing')

    try:
        env_vars['CLIENT_ID'] = environ['CLIENT_ID']
    except KeyError:
        errors.append('CLIENT_ID environment variable is missing')

    try:
        env_vars['CLIENT_SCOPE'] = environ['CLIENT_SCOPE']
    except KeyError:
        errors.append('CLIENT_SCOPE environment variable is missing')

    try:
        env_vars['AUTH_URL'] = environ['AUTH_URL']
    except KeyError:
        errors.append('AUTH_URL environment variable is missing')

    try:
        env_vars['BASE_URL'] = environ['BASE_URL']
    except KeyError:
        errors.append('BASE_URL environment variable is missing')

    return errors

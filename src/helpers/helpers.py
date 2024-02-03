from os import environ
import logging
from google import auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def load_sheet(sheet_id, sheet_range) -> list:
    credentials, _ = auth.default()
    sheet_values = []

    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=sheet_id, range=sheet_range).execute()
        sheet_values = result.get('values', [])
        logger.info(f"{len(sheet_values)} rows retrieved")
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
    
    return sheet_values

def get_coach_information(spreadsheet_id, sheet_range) -> dict:
    coaches = {}

    temp_values = load_sheet(spreadsheet_id, sheet_range)
    for row in temp_values:
        coaches[row['age_group']][row['gender']][row['team']] = row['coach']
    return coaches

def get_environment_vars():
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

    return errors, env_vars

def get_spreadsheet_vars():
    errors = []
    env_vars = {
        'SPREADSHEET_ID': None,
        'SPREADSHEET_RANGE': None,
        'GOOGLE_APPLICATION_CREDENTIALS': None
    }

    try:
        env_vars['GOOGLE_APPLICATION_CREDENTIALS'] = environ['GOOGLE_APPLICATION_CREDENTIALS']
    except KeyError:
        errors.append('GOOGLE_APPLICATION_CREDENTIALS environment variable is missing')

    try:
        env_vars['SPREADSHEET_ID'] = environ['SPREADSHEET_ID']
    except KeyError:
        errors.append('SPREADSHEET_ID environment variable is missing')

    try:
        env_vars['SPREADSHEET_RANGE'] = environ['SPREADSHEET_RANGE']
    except KeyError:
        errors.append('SPREADSHEET_RANGE environment variable is missing')

    return errors, env_vars

def get_email_vars():
    msgs = []
    env_vars = {
        'EMAIL_SERVER': 'smtp.gmail.com',
        'EMAIL_PORT': 587,
        'EMAIL_USERNAME': None,
        'EMAIL_PASSWORD': None
    }

    try:
        env_vars['EMAIL_SERVER'] = environ['EMAIL_SERVER']
    except KeyError:
        msgs.append('EMAIL_SERVER environment variable is missing, defaulting to "smtp.gmail.com"')

    try:
        env_vars['EMAIL_PORT'] = environ['EMAIL_PORT']
    except KeyError:
        msgs.append('EMAIL_PORT environment variable is missing, defaulting to 587')

    try:
        env_vars['EMAIL_USERNAME'] = environ['EMAIL_USERNAME']
    except KeyError:
        msgs.append('EMAIL_USERNAME environment variable is missing')

    try:
        env_vars['EMAIL_PASSWORD'] = environ['EMAIL_PASSWORD']
    except KeyError:
        msgs.append('EMAIL_PASSWORD environment variable is missing')

    return msgs, env_vars

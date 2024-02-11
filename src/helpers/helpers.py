from os import environ
import dateutil.parser
import logging
from google import auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Jinja template formatters
def format_date_mm_dd_yyyy(date_str) -> str:
    formatted_date = None
    try:
        dt = dateutil.parser.parse(date_str)
        formatted_date = dt.strftime("%m/%d/%Y")
    except dateutil.parser.ParserError:
        logger.error(f"Failed to parse date: {date_str}")
    except dateutil.parser.UnknownTimezoneWarning:
        logger.error(f"Invalid Time zone: {date_str}")
    except Exception as e:
        logger.error(f"Unknown error: {e}")
    return formatted_date

def format_date_hh_mm(date_str) -> str:
    formatted_time = None
    try:
        dt = dateutil.parser.parse(date_str)
        formatted_time = dt.strftime("%I:%M %p")
    except dateutil.parser.ParserError:
        logger.error(f"Failed to parse date: {date_str}")
    except dateutil.parser.UnknownTimezoneWarning:
        logger.error(f"Invalid Time zone: {date_str}")
    except Exception as e:
        logger.error(f"Unknown error: {e}")
    return formatted_time

def load_sheet(sheet_id, sheet_range) -> list:
    credentials, _ = auth.default()
    sheet_values = []

    try:
        service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=sheet_id, range=sheet_range).execute()
        sheet_values = result.get('values', [])
        logger.info(f"{len(sheet_values)} rows retrieved")
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
    
    return sheet_values

def rows_to_dict(rows):
    result = {}

    for row in rows:
        current_level = result
        for key in row[:-2]:
            current_level = current_level.setdefault(key, {})
        current_level[row[-2]] = row[-1]

    return result

def get_coach_information(spreadsheet_id, sheet_range) -> dict:
    rows =  []

    temp_values = load_sheet(spreadsheet_id, sheet_range)
    for row in temp_values:
        if row and 'grade' in row[0].lower():
            rows.append(row)

    return rows_to_dict(rows)

def get_environment_vars():
    rc = 0
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
        logger.error('CLIENT_SECRET environment variable is missing')
        rc = 66

    try:
        env_vars['CLIENT_ID'] = environ['CLIENT_ID']
    except KeyError:
        logger.error('CLIENT_ID environment variable is missing')
        rc = 66

    try:
        env_vars['CLIENT_SCOPE'] = environ['CLIENT_SCOPE']
    except KeyError:
        logger.error('CLIENT_SCOPE environment variable is missing')
        rc = 66

    try:
        env_vars['AUTH_URL'] = environ['AUTH_URL']
    except KeyError:
        logger.error('AUTH_URL environment variable is missing')
        rc = 66

    try:
        env_vars['BASE_URL'] = environ['BASE_URL']
    except KeyError:
        logger.error('BASE_URL environment variable is missing')
        rc = 66

    return rc, env_vars

def get_spreadsheet_vars():
    rc = 0
    env_vars = {
        'SPREADSHEET_ID': None,
        'SPREADSHEET_RANGE': None,
        'GOOGLE_APPLICATION_CREDENTIALS': None
    }

    try:
        env_vars['GOOGLE_APPLICATION_CREDENTIALS'] = environ['GOOGLE_APPLICATION_CREDENTIALS']
    except KeyError:
        logger.error('GOOGLE_APPLICATION_CREDENTIALS environment variable is missing')
        rc = 55

    try:
        env_vars['SPREADSHEET_ID'] = environ['SPREADSHEET_ID']
    except KeyError:
        logger.error('SPREADSHEET_ID environment variable is missing')
        rc = 55

    try:
        env_vars['SPREADSHEET_RANGE'] = environ['SPREADSHEET_RANGE']
    except KeyError:
        logger.error('SPREADSHEET_RANGE environment variable is missing')
        rc = 55

    return rc, env_vars

def get_email_vars():
    rc = 0
    env_vars = {
        'EMAIL_SERVER': 'smtp.gmail.com',
        'EMAIL_PORT': 587,
        'EMAIL_USERNAME': None,
        'EMAIL_PASSWORD': None,
        'EMAIL_TO': None
    }

    try:
        env_vars['EMAIL_SERVER'] = environ['EMAIL_SERVER']
    except KeyError:
        logger.info('EMAIL_SERVER environment variable is missing, defaulting to "smtp.gmail.com"')

    try:
        env_vars['EMAIL_PORT'] = int(environ['EMAIL_PORT'])
    except KeyError:
        logger.info('EMAIL_PORT environment variable is missing, defaulting to 587')
    except ValueError:
        logger.error('EMAIL_PORT environment variable is not an integer')
        rc = 55

    try:
        env_vars['EMAIL_USERNAME'] = environ['EMAIL_USERNAME']
    except KeyError:
        logger.error('EMAIL_USERNAME environment variable is missing')
        rc = 55

    try:
        env_vars['EMAIL_PASSWORD'] = environ['EMAIL_PASSWORD']
    except KeyError:
        logger.error('EMAIL_PASSWORD environment variable is missing')
        rc = 55

    try:
        env_vars['EMAIL_TO'] = environ['EMAIL_TO']
    except KeyError:
        logger.error('EMAIL_TO environment variable is missing')
        rc = 55

    return rc, env_vars

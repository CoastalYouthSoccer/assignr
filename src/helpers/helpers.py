from os import (environ, path)

import dateutil.parser
import logging
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import csv
from google import auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from helpers import constants

logger = logging.getLogger(__name__)

def set_boolean_value(value):
    if value is None:
        return False
    return value.lower() in ['true', '1', 't', 'y', 'yes']

def format_date_yyyy_mm_dd(date) -> str:
    formatted_date = None
    try:
        formatted_date = date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Failed to format date: {date}, error: {e}")
    return formatted_date
    
# Jinja template formatters
def format_str_mm_dd_yyyy(date_str) -> str:
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

def format_str_hh_mm(date_str) -> str:
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

def format_date_mm_dd_yyyy(date) -> str:
    formatted_date = None
    try:
        formatted_date = date.strftime("%m/%d/%Y")
    except dateutil.parser.ParserError:
        logger.error(f"Failed to parse date: {date}")
    except dateutil.parser.UnknownTimezoneWarning:
        logger.error(f"Invalid Time zone: {date}")
    except Exception as e:
        logger.error(f"Unknown error: {e}")
    return formatted_date

def format_date_hh_mm(date) -> str:
    formatted_time = None
    try:
        formatted_time = date.strftime("%I:%M %p")
    except dateutil.parser.ParserError:
        logger.error(f"Failed to parse date: {date}")
    except dateutil.parser.UnknownTimezoneWarning:
        logger.error(f"Invalid Time zone: {date}")
    except Exception as e:
        logger.error(f"Unknown error: {e}")
    return formatted_time

def create_message(content, template_name):
    logger.debug('Starting create message ...')
    message = None
    template_dir = path.join(
            path.dirname(path.realpath(__file__)),
            "templates/")
    jinja_env = Environment(
        autoescape=True,
        loader=FileSystemLoader(template_dir))
    jinja_env.filters['format_mm_dd_yyyy'] = format_date_mm_dd_yyyy
    jinja_env.filters['format_hh_mm'] = format_date_hh_mm
    try:
        template = jinja_env.get_template(template_name)
        message = template.render(content)
    except TemplateNotFound as tf:
        logger.error(f"Missing File: {tf}")

    except Exception as e:
        logger.error(f"Error: {e}")

    logger.debug('Completed create message ...')
    return message

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

def get_assignor_information():
    results = {}

    try:
        with open(environ[constants.ASSIGNOR_CSV_FILE], 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row[0] in results:
                    results[row[0]].append({
                        'name': f'{row[2]} {row[1]}',
                        'email': f'<{row[2]} {row[1]}>{row[3]}'
                    })
                else:
                    results[row[0]] = [{
                        'name': f'{row[2]} {row[1]}',
                        'email': f'<{row[2]} {row[1]}>{row[3]}'
                    }]
    except KeyError:
        logger.error(f"{constants.ASSIGNOR_CSV_FILE} environment variable not provided")
        return results
    except FileNotFoundError:
        logger.error(f"{environ[constants.ASSIGNOR_CSV_FILE]} Not Found!")
        return results

    return results

def get_environment_vars():
    rc = 0
    env_vars = {
        constants.CLIENT_SECRET: None,
        constants.CLIENT_ID: None,
        constants.CLIENT_SCOPE: None,
        constants.AUTH_URL: None,
        constants.BASE_URL: None
    }

    try:
        env_vars[constants.CLIENT_SECRET] = environ[constants.CLIENT_SECRET]
    except KeyError:
        logger.error(f'{constants.CLIENT_SECRET} environment variable is missing')
        rc = 66

    try:
        env_vars[constants.CLIENT_ID] = environ[constants.CLIENT_ID]
    except KeyError:
        logger.error(f'{constants.CLIENT_ID} environment variable is missing')
        rc = 66

    try:
        env_vars[constants.CLIENT_SCOPE] = environ[constants.CLIENT_SCOPE]
    except KeyError:
        logger.error(f'{constants.CLIENT_SCOPE} environment variable is missing')
        rc = 66

    try:
        env_vars[constants.AUTH_URL] = environ[constants.AUTH_URL]
    except KeyError:
        logger.error(f'{constants.AUTH_URL} environment variable is missing')
        rc = 66

    try:
        env_vars[constants.BASE_URL] = environ[constants.BASE_URL]
    except KeyError:
        logger.error(f'{constants.BASE_URL} environment variable is missing')
        rc = 66

    return rc, env_vars

def get_spreadsheet_vars():
    rc = 0
    env_vars = {
        constants.SPREADSHEET_ID: None,
        constants.SPREADSHEET_RANGE: None,
        constants.GOOGLE_APPLICATION_CREDENTIALS: None
    }

    try:
        env_vars[constants.GOOGLE_APPLICATION_CREDENTIALS] = \
            environ[constants.GOOGLE_APPLICATION_CREDENTIALS]
    except KeyError:
        logger.error(f'{constants.GOOGLE_APPLICATION_CREDENTIALS} environment variable is missing')
        rc = 55

    try:
        env_vars[constants.SPREADSHEET_ID] = environ[constants.SPREADSHEET_ID]
    except KeyError:
        logger.error(f'{constants.SPREADSHEET_ID} environment variable is missing')
        rc = 55

    try:
        env_vars[constants.SPREADSHEET_RANGE] = environ[constants.SPREADSHEET_RANGE]
    except KeyError:
        logger.error(f'{constants.SPREADSHEET_RANGE} environment variable is missing')
        rc = 55

    return rc, env_vars

def get_email_vars():
    rc = 0
    env_vars = {
        constants.EMAIL_SERVER: 'smtp.gmail.com',
        constants.EMAIL_PORT: 587,
        constants.EMAIL_USERNAME: None,
        constants.EMAIL_PASSWORD: None,
        constants.ADMIN_EMAIL: None,
        constants.MISCONDUCTS_EMAIL: None
    }

    try:
        env_vars[constants.EMAIL_SERVER] = environ[constants.EMAIL_SERVER]
    except KeyError:
        logger.info(f'{constants.EMAIL_SERVER} environment variable is missing, defaulting to "smtp.gmail.com"')

    try:
        env_vars[constants.EMAIL_PORT] = int(environ[constants.EMAIL_PORT])
    except KeyError:
        logger.info(f'{constants.EMAIL_PORT} environment variable is missing, defaulting to 587')
    except ValueError:
        logger.error(f'{constants.EMAIL_PORT} environment variable is not an integer')
        rc = 55

    try:
        env_vars[constants.EMAIL_USERNAME] = environ[constants.EMAIL_USERNAME]
    except KeyError:
        logger.error(f'{constants.EMAIL_USERNAME} environment variable is missing')
        rc = 55

    try:
        env_vars[constants.EMAIL_PASSWORD] = environ[constants.EMAIL_PASSWORD]
    except KeyError:
        logger.error(f'{constants.EMAIL_PASSWORD} environment variable is missing')
        rc = 55

    try:
        env_vars[constants.ADMIN_EMAIL] = environ[constants.ADMIN_EMAIL]
    except KeyError:
        logger.error(f'{constants.ADMIN_EMAIL} environment variable is missing')
        rc = 55

    try:
        env_vars[constants.MISCONDUCTS_EMAIL] = environ[constants.MISCONDUCTS_EMAIL]
    except KeyError:
        logger.error(f'{constants.MISCONDUCTS_EMAIL} environment variable is missing')
        rc = 55

    return rc, env_vars

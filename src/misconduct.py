from os import environ
from sys import (argv, exit, stdout)
import logging
import csv
from dotenv import load_dotenv
from getopt import (getopt, GetoptError)
from datetime import (datetime, timedelta)

from assignr.assignr import Assignr
from helpers.helpers import (get_environment_vars, get_spreadsheet_vars,
                             get_coach_information, get_email_vars)
from helpers.email import EMailClient

load_dotenv()

log_level = environ.get('LOG_LEVEL', 10)
logging.basicConfig(stream=stdout,
                    level=int(log_level))
logger = logging.getLogger(__name__)


def get_arguments(args):
    arguments = {
        'start_date': None, 'end_date': None
    }

    rc = 0
    USAGE='USAGE: misconduct.py -s <start-date> -e <end-date>' \
    ' DATE FORMAT=MM/DD/YYYY'

    try:
        opts, args = getopt(args,"hs:e:",
                            ["start-date=","end-date="])
    except GetoptError:
        logger.error(USAGE)
        return 77, arguments

    for opt, arg in opts:
        if opt == '-h':
            logger.error(USAGE)
            return 99, arguments
        elif opt in ("-s", "--start-date"):
            arguments['start_date'] = arg
        elif opt in ("-e", "--end-date"):
            arguments['end_date'] = arg

    try:
        if arguments['start_date']:
            arguments['start_date'] = \
                datetime.strptime(arguments['start_date'], "%m/%d/%Y").date()
        else:
            logger.info("No start date provided, setting to today")
            arguments['start_date'] = datetime.now().date()

        logger.info(f"Start Date set to {arguments['start_date']}")           
    except ValueError:
        logger.error(f"Start Date value, {arguments['start_date']} is invalid")
        rc = 88

    try:
        if arguments['end_date']:
            arguments['end_date'] = \
                datetime.strptime(arguments['end_date'], "%m/%d/%Y").date()
        else:
            logger.info(f"No end date provided, setting to 7 days prior to {arguments['start_date']}")
            arguments['end_date'] = arguments['start_date'] - \
                timedelta(days=7)
        logger.info(f"End Date set to {arguments['end_date']}")
    except ValueError:
        logger.error(f"End Date value, {arguments['end_date']} is invalid")
        rc = 88

    return rc, arguments

def send_email(email_vars, misconducts):

    email_client = EMailClient(
        email_vars['EMAIL_SERVER'], email_vars['EMAIL_PORT'],
        email_vars['EMAIL_USERNAME'], email_vars['EMAIL_PASSWORD'])

    return email_client.send_email(misconducts, "misconduct.html", True)

def main():
    rc, args = get_arguments(argv[1:])
    if rc:
        exit(rc)

    errors, env_vars = get_environment_vars()
    if errors:
        for error in errors:
            logger.error(error)
        exit(88)

    errors, spreadsheet_vars = get_spreadsheet_vars()
    if errors:
        for error in errors:
            logger.error(error)
        exit(77)

    errors, email_vars = get_email_vars()
    if errors:
        for error in errors:
            logger.error(error)
        exit(66)


    assignr = Assignr(env_vars['CLIENT_ID'], env_vars['CLIENT_SECRET'],
                      env_vars['CLIENT_SCOPE'], env_vars['BASE_URL'],
                      env_vars['AUTH_URL'])

    coaches = get_coach_information(spreadsheet_vars['spreadsheet_id'],
                                    spreadsheet_vars['sheet_range'])

    misconducts = assignr.get_misconducts(args['start_date'],
                                           args['end_date'])
    
    response = send_email(email_vars, misconducts)
    if response:
        logger.error(response)
        exit(55)


if __name__ == "__main__":
    main()

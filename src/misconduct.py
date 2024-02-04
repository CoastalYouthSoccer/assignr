from os import environ
from sys import (argv, exit, stdout)
import logging
import json
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
        if arguments['end_date']:
            arguments['end_date'] = \
                datetime.strptime(arguments['end_date'], "%m/%d/%Y").date()
        else:
            arguments['end_date'] = datetime.now().date()
            logger.info(f"No end date provided, setting to {arguments['end_date']}")
        logger.info(f"End Date set to {arguments['end_date']}")
    except ValueError:
        logger.error(f"End Date value, {arguments['end_date']} is invalid")
        rc = 88

    try:
        if arguments['start_date']:
            arguments['start_date'] = \
                datetime.strptime(arguments['start_date'], "%m/%d/%Y").date()
        else:
            arguments['start_date'] = arguments['end_date'] - \
                timedelta(days=7)
            logger.info(f"No start date provided, setting to {arguments['start_date']}")

        logger.info(f"Start Date set to {arguments['start_date']}")           
    except ValueError:
        logger.error(f"Start Date value, {arguments['start_date']} is invalid")
        rc = 88

    if arguments['start_date'] > arguments['end_date']:
        logger.error(f"Start Date {arguments['start_date']} is after End Date {arguments['end_date']}")
        rc = 88

    return rc, arguments

def send_email(email_vars, misconducts, send_to):
    email_client = EMailClient(
        email_vars['EMAIL_SERVER'], email_vars['EMAIL_PORT'],
        email_vars['EMAIL_USERNAME'], 'Game Report',
        email_vars['EMAIL_PASSWORD'])

    return email_client.send_email(misconducts, "misconduct.html.jinja",
                                   send_to, True)

def main():
    logger.info("Starting Misconduct Report")
    rc, args = get_arguments(argv[1:])
    if rc:
        exit(rc)

    rc, env_vars = get_environment_vars()
    if rc:
        exit(rc)

    rc, spreadsheet_vars = get_spreadsheet_vars()
    if rc:
        exit(rc)

    rc, email_vars = get_email_vars()
    if rc:
        exit(rc)

    assignr = Assignr(env_vars['CLIENT_ID'], env_vars['CLIENT_SECRET'],
                      env_vars['CLIENT_SCOPE'], env_vars['BASE_URL'],
                      env_vars['AUTH_URL'])

    coaches = get_coach_information(spreadsheet_vars['SPREADSHEET_ID'],
                                    spreadsheet_vars['SPREADSHEET_RANGE'])

    misconducts = assignr.get_misconducts(args['start_date'],
                                           args['end_date'])
    
    for misconduct in misconducts:
        if misconduct['age_group'] in coaches and \
            misconduct['gender'] in coaches[misconduct['age_group']] and \
            misconduct['home_team'] in coaches[misconduct['age_group']][misconduct['gender']]:
            misconduct['coach'] = coaches[misconduct['age_group']] \
        [misconduct['gender']][misconduct['home_team']]

#    with open('misconducts.json') as f_in:
#        misconducts = json.load(f_in)

    email_content = {
        'subject': f'Misconduct: {args["start_date"]} - {args["end_date"]}',
        'content': {
            'start_date': args['start_date'],
            'end_date': args['end_date'],
            'misconducts': misconducts
        }
    }
    response = send_email(email_vars, email_content, email_vars['EMAIL_TO'])
    if response:
        logger.error(response)
        exit(55)

    logger.info("Completed Misconduct Report")


if __name__ == "__main__":
    main()

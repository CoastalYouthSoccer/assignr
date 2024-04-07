from os import environ
from sys import (argv, exit, stdout)
import logging
from dotenv import load_dotenv
from getopt import (getopt, GetoptError)
from datetime import (datetime, timedelta)

from assignr.assignr import Assignr
from helpers.helpers import (get_environment_vars, get_spreadsheet_vars,
                             get_coach_information, get_email_vars,
                             create_message, get_assignor_information)
from helpers.email import EMailClient

env_file = environ.get('ENV_FILE', '.env')
load_dotenv(env_file)

log_level = environ.get('LOG_LEVEL', logging.INFO)
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

def send_email(email_vars, subject, message, send_to):
    email_client = EMailClient(
        email_vars['EMAIL_SERVER'], email_vars['EMAIL_PORT'],
        email_vars['EMAIL_USERNAME'], 'Game Report',
        email_vars['EMAIL_PASSWORD'])

    return email_client.send_email(subject, message,
                                   send_to, True)

def get_coaches_name(coaches, game_data, team):
    try:
        return coaches[game_data['age_group']][game_data['gender']][game_data[team]]
    except KeyError:
        return 'Unknown'

def process_administrator(email_vars, reports, start_date, end_date):
    subject = f'Administrator Game Reports: {start_date.strftime("%m/%d/%Y")}' \
             f' - {end_date.strftime("%m/%d/%Y")}'

    content = {
        'start_date': start_date,
        'end_date': end_date,
        'reports': reports
    }

    message = create_message(content, 'administrator.html.jinja')

    response = send_email(email_vars, subject, message,
                          email_vars['ADMIN_EMAIL'])
    if response:
        logger.error(response)

    logger.info("Completed Administrator Report")

def process_misconducts(email_vars, misconducts, coaches, start_date,
                        end_date):
# Update misconducts with coach's names
    for misconduct in misconducts:
        misconduct['home_coach'] = get_coaches_name(coaches, misconduct, 'home_team')
        misconduct['away_coach'] = get_coaches_name(coaches, misconduct, 'away_team')

    subject = f'Misconduct: {start_date.strftime("%m/%d/%Y")}' \
             f' - {end_date.strftime("%m/%d/%Y")}'
    content = {
        'start_date': start_date,
        'end_date': end_date,
        'misconducts': misconducts
    }

    message = create_message(content, 'misconduct.html.jinja')

    response = send_email(email_vars, subject, message,
                          email_vars['MISCONDUCTS_EMAIL'])

    if response:
        logger.error(response)

    logger.info("Completed Misconduct Report")

def process_assignor_reports(email_vars, reports, start_date, end_date,
                                assignors):
    subject = f'Game Reports Needing Attention: {start_date.strftime("%m/%d/%Y")}' \
             f' - {end_date.strftime("%m/%d/%Y")}'

    for report in reports:
        content = {
            'start_date': start_date,
            'end_date': end_date,
            'report': report
        }

        message = create_message(content, 'assignor.html.jinja')

        response = send_email(email_vars, subject, message,
                              assignors[report['league']][0]['email'])
    
        if response:
            logger.error(response)

    logger.info("Completed Assignors Report")

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
    
    assignors = get_assignor_information()

    reports = assignr.get_reports(args['start_date'],
                                    args['end_date'])
    process_misconducts(email_vars, reports['misconducts'], coaches,
                        args['start_date'], args['end_date'])
    process_administrator(email_vars, reports['admin_reports'],
                        args['start_date'], args['end_date'])
    process_assignor_reports(email_vars, reports['assignor_reports'],
                             args['start_date'], args['end_date'], assignors)

if __name__ == "__main__":
    main()

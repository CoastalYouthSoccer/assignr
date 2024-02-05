from os import environ
from sys import (argv, exit, stdout)
import logging
import csv
from dotenv import load_dotenv
from getopt import (getopt, GetoptError)
from datetime import datetime
from assignr.assignr import Assignr
from helpers.helpers import get_environment_vars

load_dotenv()

log_level = environ.get('LOG_LEVEL', 30)
logging.basicConfig(stream=stdout,
                    level=int(log_level))
logger = logging.getLogger(__name__)

def get_arguments(args):
    arguments = {
        'start_date': None, 'end_date': None
    }

    rc = 0
    USAGE='USAGE: availability.py -s <start-date> -e <end-date>' \
    ' FORMAT=MM/DD/YYYY'

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

    if arguments['start_date'] is None or arguments['end_date'] is None:
        logger.error(USAGE)
        return 99, arguments

    try:
         arguments['start_date'] = datetime.strptime(arguments['start_date'], "%m/%d/%Y").date()
    except ValueError:
        logger.error(f"Start Date value, {arguments['start_date']} is invalid")
        rc = 88
    try:
         arguments['end_date'] = datetime.strptime(arguments['end_date'], "%m/%d/%Y").date()
    except ValueError:
        logger.error(f"End Date value, {arguments['end_date']} is invalid")
        rc = 88

    return rc, arguments

def get_referees():
    referees = []

    try:
        with open(environ['FILE_NAME'], 'r') as csv_file:
            reader = csv.reader(csv_file)
    except KeyError:
        logger.error("FILE_NAME environment variable not provided")
        return referees
    except FileNotFoundError:
        logger.error(f"{environ['FILE_NAME']} Not Found!")
        return referees

    for row in reader:
        referees.append({
            'referee': f"{row[0]} {row[1]}",
            'id': row[2]
        })

    return referees

def main():
    rc, args = get_arguments(argv[1:])
    if rc:
        exit(rc)

    rc, env_vars = get_environment_vars()
    if rc:
        exit(rc)

    assignr = Assignr(env_vars['CLIENT_ID'], env_vars['CLIENT_SECRET'],
                      env_vars['CLIENT_SCOPE'], env_vars['BASE_URL'],
                      env_vars['AUTH_URL'])

    referee_availability = []
    for referee in get_referees():
        response = assignr.get_availability(referee['id'], args['start_date'],
                                    args['end_date'])
        if response:
            for resp in response:
                print(f"{referee['referee']} - {resp['date']} - {resp['avail']}")
        else:
            logger.warning(f"{referee['referee']} isn't Available")

        referee_availability.append({
            'referee': referee['referee'],
            'availability': response
        })

    print(referee_availability)

if __name__ == "__main__":
    main()

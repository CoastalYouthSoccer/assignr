from os import environ
from sys import (argv, exit, stdout)
import logging
import csv
from dotenv import load_dotenv
from getopt import (getopt, GetoptError)
from datetime import datetime

from helpers.helpers import (authenticate, get_requests)

load_dotenv()

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

def get_availability(token, user_id, start_dt, end_dt):
    availability = []
    params = {
        'user_id': user_id,
        'search[start_date]': start_dt,
        'search[end_date]': end_dt
    }

    status_code, response = get_requests(token, f'users/{user_id}/availability', params=params)

#    if status_code != 200:
#        logger.error(f'Failed return code: {status_code} for user: {user_id}')
#        return availability

    if status_code == 404:
        logger.warning(f'User: {user_id} has no availability')
        return availability
    
    try:
        availabilities = response['_embedded']['availability']
        for avail in availabilities:
            if avail['all_day']:
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
    try:
        LOG_LEVEL = environ['LOG_LEVEL']
    except KeyError:
        logger.error('LOG_LEVEL environment variable not found')
        exit(99)

    logging.basicConfig(stream=stdout,
                        level=int(LOG_LEVEL))

    rc, args = get_arguments(argv[1:])
    if rc:
        exit(rc)

    token = authenticate()
    if token is None:
        exit(88)

    referee_availability = []
    for referee in get_referees():
        response = get_availability(token, referee['id'], args['start_date'],
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

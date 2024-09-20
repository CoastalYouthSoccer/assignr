from datetime import (datetime, timedelta)
from unittest import TestCase
from score_sheet import get_arguments

USAGE='USAGE: score_sheet.py -s <start-date> (MM/DD/YYYY) ' \
        '-e <end-date> (MM/DD/YYYY) -g <game type, default "Futsal">' 
ERROR_USAGE=f'ERROR:score_sheet:{USAGE}'
DATE_01012020 = '01/01/2020'
DATE_01012021 = '01/01/2021'
GAME_TYPE = 'Futsal'
DATE_FORMAT_01012020 = datetime.strptime(DATE_01012020, "%m/%d/%Y").date()
DATE_FORMAT_01012021 = datetime.strptime(DATE_01012021, "%m/%d/%Y").date()
class TestGetArguments(TestCase):
    def test_help(self):
        expected_args = {'start_date': None, 'end_date': None,
                         'game_type': None}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_valid_options(self):
        expected_args = {
            'start_date': DATE_FORMAT_01012020,
            'end_date': DATE_FORMAT_01012021,
            'game_type': GAME_TYPE
        }
        rc, args = get_arguments(['-s', DATE_01012020, '-e', DATE_01012021,
                                  '-g', GAME_TYPE])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_invalid_options(self):
        expected_args = {'start_date': None, 'end_date': None,
                         'game_type': None}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-n'])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 77)
        self.assertEqual(args, expected_args)

    def test_missing_start_date(self):
        start_date = None

        expected_args = {
            'start_date': start_date,
            'end_date': '01/01/2020',
            'game_type': GAME_TYPE
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-e', DATE_01012020,'-g', GAME_TYPE])
        self.assertEqual(cm.output, [ERROR_USAGE])

        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_end_date(self):
        end_date = None
        expected_args = {
            'start_date': DATE_01012020,
            'end_date': end_date,
            'game_type': GAME_TYPE
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', DATE_01012020, '-g', GAME_TYPE])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_start_date_greater_end_date(self):
        end_date = datetime.strptime(DATE_01012020, "%m/%d/%Y").date()
        start_date = datetime.strptime(DATE_01012021, "%m/%d/%Y").date()
        expected_args = {
            'start_date': start_date,
            'end_date': end_date,
            'game_type': GAME_TYPE
        }
        error_message = [
            'ERROR:score_sheet:Start Date, 2021-01-01, occurs AFTER End Date:2020-01-01',
            'INFO:score_sheet:Game Type not provided, defaulting to "Futsal"'
        ]
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', DATE_01012021, '-e', DATE_01012020,
                                      '-g', None])
        self.assertEqual(cm.output, error_message)
        self.assertEqual(rc, 77)
        self.assertEqual(args, expected_args)

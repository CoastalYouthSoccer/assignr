from datetime import (datetime, timedelta)
from unittest import TestCase
from missing_game_reports import get_arguments

ERROR_USAGE='ERROR:missing_game_reports:USAGE: missing_game_reports.py -s <start-date>' \
    ' -e <end-date> DATE FORMAT=MM/DD/YYYY -r'
DATE_01012020 = '01/01/2020'
DATE_01012021 = '01/01/2021'
DATE_FORMAT_01012020 = datetime.strptime(DATE_01012020, "%m/%d/%Y").date()
DATE_FORMAT_01012021 = datetime.strptime(DATE_01012021, "%m/%d/%Y").date()
START_DATE = 'start_date'
END_DATE = 'end_date'
REFEREE_REMINDER = 'referee_reminder'

class TestGetArguments(TestCase):
    def test_help(self):
        expected_args = {START_DATE: None, END_DATE: None,
                         REFEREE_REMINDER: False}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_valid_options(self):
        expected_args = {
            START_DATE: DATE_FORMAT_01012020,
            END_DATE: DATE_FORMAT_01012021,
            REFEREE_REMINDER: True
        }
        rc, args = get_arguments(['-s', DATE_01012020, '-e', DATE_01012021, '-r'])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_invalid_options(self):
        expected_args = {START_DATE: None, END_DATE: None, REFEREE_REMINDER: False}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-n'])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 77)
        self.assertEqual(args, expected_args)

    def test_missing_start_date(self):
        start_date = DATE_FORMAT_01012020 - timedelta(days=7)

        expected_args = {
            START_DATE: start_date,
            END_DATE: DATE_FORMAT_01012020,
            REFEREE_REMINDER: True
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-e', DATE_01012020, '-r'])
        self.assertEqual(cm.output, [
            "INFO:missing_game_reports:End Date set to 2020-01-01",
            f"INFO:missing_game_reports:No start date provided, setting to {start_date}",
            f"INFO:missing_game_reports:Start Date set to {start_date}"
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_missing_end_date(self):
        end_date = datetime.now().date()
        expected_args = {
            START_DATE: DATE_FORMAT_01012020,
            END_DATE: end_date,
            REFEREE_REMINDER: True
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', DATE_01012020, '-r'])
        self.assertEqual(cm.output, [
            f'INFO:missing_game_reports:No end date provided, setting to {end_date}',
            f'INFO:missing_game_reports:End Date set to {end_date}',
            'INFO:missing_game_reports:Start Date set to 2020-01-01'
        ])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_missing_referee_reminder(self):
        expected_args = {
            START_DATE: DATE_FORMAT_01012020,
            END_DATE: DATE_FORMAT_01012021,
            REFEREE_REMINDER: False
        }
        rc, args = get_arguments(['-s', DATE_01012020, '-e', DATE_01012021])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_start_date_greater_end_date(self):
        end_date = datetime.strptime(DATE_01012020, "%m/%d/%Y").date()
        start_date = datetime.strptime('01/10/2020', "%m/%d/%Y").date()
        expected_args = {
            START_DATE: start_date,
            END_DATE: end_date,
            REFEREE_REMINDER: True
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', '01/10/2020', '-e', DATE_01012020, '-r'])
        self.assertEqual(cm.output, [
            f'INFO:missing_game_reports:End Date set to {end_date}',
            f'INFO:missing_game_reports:Start Date set to {start_date}',
            f'ERROR:missing_game_reports:Start Date {start_date} is after End Date {end_date}'
        ])
        self.assertEqual(rc, 88)
        self.assertEqual(args, expected_args)

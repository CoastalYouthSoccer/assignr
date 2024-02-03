from os import environ
from datetime import date
from unittest import TestCase
from unittest.mock import (patch, MagicMock)
from misconduct import get_arguments

ERROR_USAGE='ERROR:misconduct:USAGE: misconduct.py -s <start-date>' \
    ' -e <end-date> DATE FORMAT=MM/DD/YYYY'
START_DATE='01/01/2020'

class TestGetArguments(TestCase):
    def test_help(self):
        expected_args = {'start_date': None, 'end_date': None}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_valid_options(self):
        expected_args = {
            'start_date': date(2020, 1, 1),
            'end_date': date(2021, 1, 1)
        }
        rc, args = get_arguments(['-s', START_DATE, '-e', '01/01/2021'])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_invalid_options(self):
        expected_args = {'start_date': None, 'end_date': None}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-n'])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 77)
        self.assertEqual(args, expected_args)

    def test_missing_start_date(self):
        expected_args = {
            'start_date': None,
            'end_date': '01/10/2020'
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-e', '01/10/2020'])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_end_date(self):
        expected_args = {
            'start_date': START_DATE,
            'end_date': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', START_DATE])
        self.assertEqual(cm.output, [ERROR_USAGE])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_invalid_start_date(self):
        expected_args = {
            'start_date': '01/32/2020',
            'end_date': date(2020, 1, 31)
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', '01/32/2020', '-e', '01/31/2020'])
        self.assertEqual(cm.output, [
            'ERROR:misconduct:Start Date value, 01/32/2020 is invalid'
        ])
        self.assertEqual(rc, 88)
        self.assertEqual(args, expected_args)

    def test_invalid_end_date(self):
        expected_args = {
            'start_date': date(2020, 1, 31),
            'end_date': '01/32/2020'
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', '01/31/2020', '-e', '01/32/2020'])
        self.assertEqual(cm.output, [
            'ERROR:misconduct:End Date value, 01/32/2020 is invalid'
        ])
        self.assertEqual(rc, 88)
        self.assertEqual(args, expected_args)
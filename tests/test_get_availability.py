from os import environ, getcwd
from datetime import date
from unittest import (TestCase, mock)
from unittest.mock import (patch, MagicMock)
from availability.availability import (get_arguments, get_referees)

USAGE='USAGE: availability.py -s <start-date> -e <end-date>' \
    ' FORMAT=MM/DD/YYYY'
DATE_11_11_2023 = '11/11/2023'


class TestGetArguments(TestCase):
    def test_help(self):
        expected_args = {
            'start_date': None, 'end_date': None
        }

        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [f"ERROR:availability.availability:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_valid_options(self):
        expected_args = {'start_date': date(2023,11,11),
                         'end_date': date(2023,11,12)
                        }
        rc, args = get_arguments(['-s', DATE_11_11_2023, '-e', '11/12/2023'])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_missing_arguments(self):
        expected_args = {'start_date': DATE_11_11_2023,
                         'end_date': None
                        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', DATE_11_11_2023])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)
        self.assertEqual(cm.output, [f"ERROR:availability.availability:{USAGE}"])

    def test_invalid_start_date(self):
        expected_args = {'start_date': '21/11/2023',
                         'end_date': date(2023,11,12)
                        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', '21/11/2023', '-e', '11/12/2023'])
        self.assertEqual(rc, 88)
        self.assertEqual(args, expected_args)
        self.assertEqual(cm.output,
                         ['ERROR:availability.availability:Start Date value, 21/11/2023 is invalid'])

    def test_invalid_end_date(self):
        expected_args = {'start_date': date(2023,11,11),
                         'end_date': '11/32/2023'
                        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', DATE_11_11_2023, '-e', '11/32/2023'])
        self.assertEqual(rc, 88)
        self.assertEqual(args, expected_args)
        self.assertEqual(cm.output,
                         ['ERROR:availability.availability:End Date value, 11/32/2023 is invalid'])


class TestGetReferees(TestCase):
    @patch('builtins.open')
    @patch('availability.availability.csv.reader')
    def test_valid_file(self, mock_csv_reader, mock_open):
        mock_csv_reader.return_value = [['John', 'Doe', '1'], ['Jane', 'Smith', '2']]
        expected_result = [
            {'referee': 'John Doe', 'id': '1'},
            {'referee': 'Jane Smith', 'id': '2'}
        ]

        with patch.dict(environ, {'FILE_NAME': 'valid_file.csv'}):
            actual_result = get_referees()

        self.assertEqual(actual_result, expected_result)

    @patch.dict(environ,{}, clear=True)
    def test_missing_file_name(self):
        with self.assertLogs(level='INFO') as cm:
            results = get_referees()
        self.assertEqual(cm.output,
                         ['ERROR:availability.availability:FILE_NAME environment variable not provided'])
        self.assertEqual(results, [])

    @patch.dict(environ,{'FILE_NAME': 'valid_file.csv'}, clear=True)
    def test_file_not_found(self):
        with self.assertLogs(level='INFO') as cm:
            results = get_referees()
        self.assertEqual(cm.output,
                         ['ERROR:availability.availability:valid_file.csv Not Found!'])
        self.assertEqual(results, [])

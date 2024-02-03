import unittest
from helpers.email import EMailClient

CONST_EMAIL = 'test@example.org'
CONST_SUBJECT = 'Test Email'
CONST_NAME = 'Test User'
CONST_SENDER_EMAIL = 'test_sender@example.com'
CONST_CONTACT_TXT = 'contact.txt'
CONST_CONTACT_HTML = 'contact.html'
CONST_TEST_MESSAGE = "This is a test message"

CONST_DATA_NO_MESSAGE = {
    'email': CONST_EMAIL,
    'subject': CONST_SUBJECT,
    'name': CONST_NAME
}

CONST_DATA_MESSAGE = {
    'email': CONST_EMAIL,
    'subject': CONST_SUBJECT,
    'name': CONST_NAME,
    'message': CONST_TEST_MESSAGE
}


class TestEMail(unittest.TestCase):
    def test_missing_subject(self):
        data = {
            'email': CONST_EMAIL
        }

        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')
        response = email_client.send_email(data, 'no_template')
        self.assertDictEqual(response,
                         {"message": "email and subject are required fields", "code": 406})

    def test_create_message_missing_template(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')

        with self.assertLogs(level='DEBUG') as cm:
            message = email_client.create_message(CONST_DATA_NO_MESSAGE, 'missing.txt')
        self.assertEqual(cm.output, [
            "DEBUG:helpers.email:Starting create message ...",
            "ERROR:helpers.email:Missing File: missing.txt",
            "DEBUG:helpers.email:Completed create message ..."
        ])
        self.assertEqual(message, None)

    def test_create_message_text_no_message(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')

        expected_msg = 'Message received from test@example.org\n\n\nName: Test User\n\n\nSubject: Test Email\n\n'
        message = email_client.create_message(CONST_DATA_NO_MESSAGE, CONST_CONTACT_TXT)
        self.assertEqual( message, expected_msg)

    def test_create_message_text_message(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')
        message = email_client.create_message(CONST_DATA_MESSAGE, CONST_CONTACT_TXT)
        self.assertEqual(
            message,
            f"Message received from test@example.org\n\n\nName: Test User\n\n\nSubject: Test Email\n\n{CONST_TEST_MESSAGE}")

    def test_create_message_text_message_no_name(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')
        data = {
            'email': CONST_EMAIL,
            'subject': CONST_SUBJECT,
            'message': CONST_TEST_MESSAGE
        }

        message = email_client.create_message(data, CONST_CONTACT_TXT)
        self.assertEqual(
            message,
            f"Message received from test@example.org\n\n\n\nSubject: Test Email\n\n{CONST_TEST_MESSAGE}")

    def test_create_message_html_no_message(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')

        message = email_client.create_message(CONST_DATA_NO_MESSAGE, CONST_CONTACT_HTML)
        self.assertEqual(
            message,
            'Message received from <strong>test@example.org</strong>\n\n\n<p>Name: <strong>Test User</strong></p>\n\n\n<p>Subject: <strong>Test Email</strong></p>\n<br>\n'
        )

    def test_create_message_html_message(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')
        message = email_client.create_message(CONST_DATA_MESSAGE, CONST_CONTACT_HTML)
        self.assertEqual(
            message,
            f"Message received from <strong>test@example.org</strong>\n\n\n<p>Name: <strong>Test User</strong></p>\n\n\n<p>Subject: <strong>Test Email</strong></p>\n<br>\n{CONST_TEST_MESSAGE}")

    def test_create_message_html_message_no_name(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')
        data = {
            'email': CONST_EMAIL,
            'subject': CONST_SUBJECT,
            'message': CONST_TEST_MESSAGE
        }

        message = email_client.create_message(data, CONST_CONTACT_HTML)
        self.assertEqual(
            message,
            f"Message received from <strong>test@example.org</strong>\n\n\n\n<p>Subject: <strong>Test Email</strong></p>\n<br>\n{CONST_TEST_MESSAGE}")

    def test_create_email_text(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')

        with self.assertLogs(level='DEBUG') as cm:
            message = email_client.create_email(CONST_DATA_NO_MESSAGE, 'contact.txt', False)
        self.assertEqual(cm.output, [
            "DEBUG:helpers.email:Starting create email ...",
            "DEBUG:helpers.email:Starting create message ...",
            "DEBUG:helpers.email:Completed create message ...",
            "DEBUG:helpers.email:Completed create email ..."
        ])
        self.assertEqual(message._headers[0][0], 'From')
        self.assertEqual(message._headers[1][0], 'To')
        self.assertEqual(message._headers[2][0], 'Subject')
        self.assertEqual(message._headers[2][1], 'Test Email')

    def test_create_email_html(self):
        email_client = EMailClient('test', 587, CONST_SENDER_EMAIL,
                                   'test_password')

        message = email_client.create_email(CONST_DATA_NO_MESSAGE, CONST_CONTACT_HTML, True)
        self.assertEqual(message._headers[3][0], 'Content-Type')
        self.assertEqual(message._headers[3][1], 'text/html; charset="utf-8"')
        self.assertEqual(message._headers[4][0], 'Content-Transfer-Encoding')
        self.assertEqual(message._headers[4][1], '7bit')
        self.assertEqual(message._headers[5][0], 'MIME-Version')
        self.assertEqual(message._headers[5][1], '1.0')

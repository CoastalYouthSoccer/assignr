from os import path
import logging
from email.message import EmailMessage
from email.headerregistry import Address
import smtplib, ssl

logger = logging.getLogger(__name__)

def get_email_components(email):
    email_components = {
        'name': None,
        'address': None
    }

    start_index = email.find('<') + 1
    end_index = email.find('>')
    if start_index == 0 or end_index == -1:
        logger.error(f"Could not determine name for {email}.")
# No point continuing, as the address is not in the correct format.
        return email_components

    email_components['name'] = email[start_index:end_index]

    try:
        if '@' in email:
            email_components['address'] = email[end_index+1:]
        else:
            logger.error(f"Invalid email address: {email}.")
        if '.' not in email:
            logger.error(f"Invalid email address: {email}.")
    except IndexError as ie:
        logger.error(f"Unable to process {email}: {ie}")
    return email_components

class EMailClient():
    def __init__(self, smtp_server, smtp_port, sender_email,
                 sender_name, password) -> None:
        self.context = ssl.create_default_context()
        self.smtp_server = smtp_server
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.password = password
        self.smtp_port = smtp_port

    def create_email(self, subject, message, send_to, html=True):
        logger.debug('Starting create email ...')

        email = EmailMessage()
        email["From"] = Address(display_name=self.sender_name,
                                addr_spec=self.sender_email
                               )

        if ',' in send_to:
            addresses = []
            for recipient in send_to.split(","):
                addr_components = get_email_components(recipient)
                addresses.append(
                    Address(display_name=addr_components['name'],
                            addr_spec=addr_components['address']
                            ))
            email["To"] = addresses
        else:
            addr_components = get_email_components(send_to)
            email["To"] = Address(display_name=addr_components['name'],
                                  addr_spec=addr_components['address']
                                 )

        email["Subject"] = subject

        if html:
            email.set_content(message, subtype="html")
        else:
            email.set_content(message)

        logger.debug('Completed create email ...')
        return email

    def send_email(self, subject, message, send_to,
                   html=False) -> int:
        rc = 0
        logger.debug('Starting send email ...')
    
        if subject is None:
            logger.error("'subject' is required")
            rc = 22

        if message is None:
            logger.error("'message' is required")
            rc = 22

        if send_to is None:
            logger.error("'addressee' is required")
            rc = 22

        if rc:
            return rc

        email = self.create_email(subject, message, send_to, html)

        if email is None:
            logger.error("Unable to create email")
            return 33

        try:
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls(context=self.context)

            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, self.sender_email,
                            email.as_string())
            logger.debug('Completed send email ...')

        except smtplib.SMTPAuthenticationError as se:
            logger.error(se)
            logger.debug('Completed send email ...')
            rc = 44

        return rc

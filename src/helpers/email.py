from os import path
import logging
from email.message import EmailMessage
from email.headerregistry import Address
import smtplib, ssl

logger = logging.getLogger(__name__)

def get_email_components(email_address):
    # Assuming email_address is a string with name <email@domain.com> format
    if '<' in email_address and '>' in email_address:
        name, address = email_address.split('<')
        name = name.strip()
        address = address.rstrip('>')
    else:
        name = ''
        address = email_address
    return {'name': name, 'address': address}

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
            recipients = []
            for recipient in send_to.split(","):
                addr_components = get_email_components(recipient.strip())
                recipients.append(
                    Address(display_name=addr_components['name'],
                            addr_spec=addr_components['address']
                            ))
            email["To"] = recipients  # Set the list directly to the 'To' field
        else:
            addr_components = get_email_components(send_to.strip())
            email["To"] = [Address(display_name=addr_components['name'],
                                   addr_spec=addr_components['address']
                                  )]

        email["Subject"] = subject
        email.set_content(message)
        if html:
            email.add_alternative(message, subtype="html")

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
            server.send_message(email)
#            server.sendmail(self.sender_email, self.sender_email,
#                            email.as_string())
            logger.debug('Completed send email ...')

        except smtplib.SMTPAuthenticationError as se:
            logger.error(se)
            logger.debug('Completed send email ...')
            rc = 44

        return rc

from os import path
import logging
from email.message import EmailMessage
from email.headerregistry import Address
import smtplib, ssl
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)


class EMailClient():
    def __init__(self, smtp_server, smtp_port, sender_email, password) -> None:
        self.context = ssl.create_default_context()
        self.smtp_server = smtp_server
        self.sender_email = sender_email
        self.password = password
        self.smtp_port = smtp_port
        self.template_dir = path.join(
            path.dirname(path.realpath(__file__)),
            "templates/")                

    def create_message(self, content, template_name):
        logger.debug('Starting create message ...')
        message = None
        environment = Environment(
            autoescape=True,
            loader=FileSystemLoader(self.template_dir))
        try:
            template = environment.get_template(template_name)
            message = template.render(content)
        except TemplateNotFound as tf:
            logger.error(f"Missing File: {tf}")

        logger.debug('Completed create message ...')
        return message

    def create_email(self, content, template_name, html=True):
        logger.debug('Starting create email ...')

        addr_component = self.sender_email.split('@')

        email = EmailMessage()
        email["From"] = Address('Hanover Soccer Referee',
                                addr_component[0],
                                addr_component[1]
                               )
        email["To"] = Address('Hanover Soccer Referee',
                              addr_component[0],
                              addr_component[1]
                             )
        email["Subject"] = content['subject']

        message = self.create_message(content['content'], template_name)

        if html:
            email.set_content(message, subtype="html")
        else:
            email.set_content(message)

        logger.debug('Completed create email ...')
        return email

    def send_email(self, content, template_name, html=False) -> int:
        rc = 0
        logger.debug('Starting send email ...')
    
        if "content" not in content:
            logger.error("'content' is required")
            rc = 33
        if "subject" not in content:
            logger.error("'subject' is required")
            rc = 33
        if rc != 0:
            return rc

        email = self.create_email(content, template_name, html)

        if email is None:
            logger.error("Unable to send email")
            rc = 33

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

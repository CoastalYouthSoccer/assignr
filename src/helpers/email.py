from os import path
import logging
from email.message import EmailMessage
from email.headerregistry import Address
import smtplib, ssl
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)

def get_email_components(email):
    email_components = {
        'name': None,
        'domain': None,
        'address': None
    }

    start_index = email.find('<') + 1
    end_index = email.find('>')
    if start_index == 0 or end_index == -1:
        logger.error(f"Could not determine name for {email}.")
# No point continuing, as the address is not in the correct format.
        return email_components

    email_components['name'] = email[start_index:end_index]
    if '@' in email:
        components = email[end_index+1:].split('@')
        email_components['address'] = components[0]
        if '.' in components[1]:
            email_components['domain'] = components[1]
        else:
            logger.error(f"Invalid email address: {email}.")
    else:
        logger.error(f"Invalid email address: {email}.")

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

        except Exception as e:
            logger.error(f"Error: {e}")
        logger.debug('Completed create message ...')
        return message

    def create_email(self, content, template_name, send_to, html=True):
        logger.debug('Starting create email ...')

        addr_component = self.sender_email.split('@')

        email = EmailMessage()
        email["From"] = Address(self.sender_name,
                                addr_component[0],
                                addr_component[1]
                               )

        if ',' in send_to:
            addresses = []
            for recipient in send_to.split(","):
                addr_components = get_email_components(recipient)
                addresses.append(Address(addr_components['name'],
                                      addr_components['address'],
                                      addr_components['domain']
                                     ))
            email["To"] = addresses
        else:
            addr_components = get_email_components(send_to)
            email["To"] = Address(addr_components['name'],
                                  addr_components['address'],
                                  addr_components['domain']
                                 )

        email["Subject"] = content['subject']

        message = self.create_message(content['content'], template_name)

        if html:
            email.set_content(message, subtype="html")
        else:
            email.set_content(message)

        logger.debug('Completed create email ...')
        return email

    def send_email(self, content, template_name, send_to,
                   html=False) -> int:
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

        email = self.create_email(content, template_name, send_to,
                                  html)

        if email is None:
            logger.error("Unable to create email")
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

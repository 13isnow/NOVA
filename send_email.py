from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import json


class Email_operation:

    def __init__(self, emailSender_config):
        self.email = emailSender_config['email']
        self.token = emailSender_config['token']
        self.sender = emailSender_config['name']
        self.host = emailSender_config['host']
        self.smtp = self.smtp_load()

    def smtp_load(self):
        smtp = smtplib.SMTP_SSL(self.host, 465)
        smtp.starttls()
        smtp.login(self.email, self.token)
        return smtp

    def get_user_and_email(self, user_id):
        with open('members.json', 'r', encoding='utf-8') as file:
            members = json.load(file)
            try:
                return members['users'][f'id={user_id}']['name'], members['users'][f'id={user_id}']['email']
            except KeyError as e:
                raise Exception(f'用户不存在,{e}')

    def extract_html_body(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find('p').get_text(strip=True)

    def send_comment(self, comment_info):
        def format_email():
            nonlocal comment_info
            template = templates.comment_send(templates())
            template = template.replace('$$author$$', comment_info['author'])
            template = template.replace('$$time$$', comment_info['create_time'])
            template = template.replace('$$commenter$$', comment_info['commenter'])
            template = template.replace('$$doc_title$$', comment_info['title'])
            template = template.replace('$$content$$', comment_info['content'])
            template = template.replace('$$sender$$', self.sender)

            return template

        comment_info['author'], comment_info['author_email'] = self.get_user_and_email(comment_info['author_id'])
        comment_info['content'] = self.extract_html_body(comment_info['content'])
        body = format_email()
        message = MIMEMultipart('alternative')
        message['From'] = self.email
        message['To'] = comment_info['author_email']
        message['Subject'] = Header(comment_info['subject'], 'utf-8')
        part = MIMEText(body, 'html', 'utf-8')
        message.attach(part)
        self.smtp.sendmail(self.email, comment_info['author_email'], message.as_string())

    def send_update_doc(self):
        pass


class templates:
    def comment_send(self):
        with open('./email_template/comment_send.html', 'r', encoding='utf-8') as file:
            return file.read()

import smtplib, ssl
from datetime import datetime
import smtplib
import time
import imaplib
import email
import traceback 
from pdb import set_trace
import dateparser
import re
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from logs.base_logger import logger
import pickle
import os


class EmailHandler:
    '''
    Email handler to send and recieve emails
    '''
    
    def __init__(
        self
        ) -> None:
        logger.info('Class EmailHandler has been initialized.')
        self.set_credentials()

    
    def set_credentials(
        self,
        sender_email: str = None, #'brahmidarling69@gmail.com',
        reciever_email: str = None, #'testemail2923@gmail.com',
        sender_password: str = None, #r'#Brahmi69',
        save_changes = False
    ):

        _creds_path = 'utils/credentials.pickle'
        if not os.path.isfile(_creds_path):
            logger.info('Credentials file not found, dummy hash table initialized.')
            creds = {'sender_email': '', 'sender_password': '', 'reciever_email': ''}
            with open(_creds_path, 'wb') as save_file:
                pickle.dump(creds, save_file)

        if save_changes:
            
            if sender_email and reciever_email and sender_password:
                logger.info('Sender email, reciever email and sender password have been updated.')
                with open('utils/credentials.pickle', 'rb') as save_file:
                    creds = pickle.load(save_file)
                
                self.sender_email = sender_email
                self.sender_password = sender_password
                self.reciever_email = reciever_email
                creds['sender_email'] = self.sender_email
                creds['reciever_email'] = self.reciever_email
                creds['sender_password'] = self.sender_password

                with open('utils/credentials.pickle', 'wb') as save_file:
                    pickle.dump(creds, save_file)

            else:
                if sender_email:
                    logger.info('Sender email has been updated.')
                    self.sender_email = sender_email
                    with open('utils/credentials.pickle', 'rb') as save_file:
                        creds = pickle.load(save_file)
                    creds['sender_email'] = self.sender_email
                    with open('utils/credentials.pickle', 'wb') as save_file:
                        pickle.dump(creds, save_file)
                
                if reciever_email:
                    logger.info('Reciever email has been updated.')
                    self.reciever_email = reciever_email
                    with open('utils/credentials.pickle', 'rb') as save_file:
                        creds = pickle.load(save_file)
                    creds['reciever_email'] = self.reciever_email
                    with open('utils/credentials.pickle', 'wb') as save_file:
                        pickle.dump(creds, save_file)

                if sender_password:
                    logger.info('Sender password has been updated')
                    self.sender_password = sender_password
                    with open('utils/credentials.pickle', 'rb') as save_file:
                        creds = pickle.load(save_file)
                    creds['sender_password'] = self.sender_password
                    with open('utils/credentials.pickle', 'wb') as save_file:
                        pickle.dump(creds, save_file)

                
        else:
            with open('utils/credentials.pickle', 'rb') as save_file:
                creds = pickle.load(save_file)

            self.sender_email = creds['sender_email']
            self.reciever_email = creds['reciever_email']
            self.sender_password = creds['sender_password']
            logger.info('Credentials for EmailHandler have been set, sender_email: {}, reciever_email: {}'.format(self.sender_email, self.reciever_email))

    
    def check_email(
        self
    ) -> bool:
        '''
        Checks if sender email and password are valid
        '''

        port = 465  # For SSL

        # Create a secure SSL context
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
            return True
        except smtplib.SMTPAuthenticationError as e:
            return False
            
    
    
    def send_email(
        self,
        message: str = '',
        send_as_attachment = False
    ):
        print('Sending email now...')
        port = 465  # For SSL

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(self.sender_email, self.sender_password)
            # TODO: Send email here
            
            if send_as_attachment:
                
                msg = MIMEMultipart()
                part1 = MIMEText(message, 'html')
                msg.attach(part1)
                message = msg.as_string()
    
            server.sendmail(self.sender_email, self.reciever_email, message)
            logger.info('Email with message: {} has been sent.'.format(message))
                
                
    def read_email(
        self
    ):
        '''
        Source: https://codehandbook.org/how-to-read-email-from-gmail-using-python/
        https://stackoverflow.com/questions/17874360/python-how-to-parse-the-body-from-a-raw-email-given-that-raw-email-does-not
        '''
        try:
            SMTP_SERVER = "imap.gmail.com"
            mail = imaplib.IMAP4_SSL(SMTP_SERVER)
            mail.login(self.sender_email, self.sender_password)
            mail.select('inbox')
        
            data = mail.search(None, 'ALL')
            mail_ids = data[1]
            id_list = mail_ids[0].split()   
            first_email_id = int(id_list[0])
            latest_email_id = int(id_list[-1])
            
            for i in range(latest_email_id,first_email_id, -1):
            
                data = mail.fetch(str(i), '(RFC822)' )
                for response_part in data:
                    arr = response_part[0]
                    if isinstance(arr, tuple):
                        msg = email.message_from_string(str(arr[1],'utf-8'))
                        email_subject = msg['subject']
                        email_from = msg['from']
                        if re.search(r'[\w\.-]+@[\w\.-]+', email_from).group() != self.reciever_email:
                            logger.info('Found email that has not been sent by the user, ignoring...')
                            continue


                        email_datetime = dateparser.parse(msg['date'])

                        if msg.is_multipart():
                            for payload in msg.get_payload()[:1]:
                                return payload.get_payload(), email_datetime
                        else:
                            return msg.get_payload(), email_datetime  

        except Exception as e:
            logger.info('Exception while reading email: {}'.format(str(e)))
            pass


    def preprocess_email_content(
        self,
        email
    ):
        for index, char in enumerate(email[0]):
            if char == '\n':
                temp, o2 = email[0][:index-1].split(',')
                return temp, o2, email[1]

if __name__ == '__main__':
    obj = EmailHandler()
    obj.send_email('this is a test')
    print(obj.preprocess_email_content(obj.read_email()))
import smtplib, ssl
from datetime import datetime
import smtplib
import time
import imaplib
import email
import traceback 
from pdb import set_trace
from typing import Tuple
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
        '''
        Initalizes EmailHandler
        '''
        logger.info('Class EmailHandler has been initialized.')
        print('INFO: EmailHandler has been initlaized.')
        self.set_credentials()

    
    def set_credentials(
        self,
        sender_email: str = None, #'brahmidarling69@gmail.com',
        reciever_email: str = None, #'testemail2923@gmail.com',
        sender_password: str = None, #r'#Brahmi69',
        save_changes = False
    ) -> None:
        '''
        Sets credentials for the emails and password. If save_changes is True, accepts inputs and saves it, else just reads from saved file
        '''

        _creds_path = 'utils/credentials.pickle'
        if not os.path.isfile(_creds_path):
            # first time starting the app, no creds file found
            # create dummy file
            logger.info('Credentials file not found, dummy hash table initialized.')
            creds = {'sender_email': '', 'sender_password': '', 'reciever_email': ''}
            with open(_creds_path, 'wb') as save_file:
                pickle.dump(creds, save_file)

        if save_changes:
            # accept input and save the changes
            
            if sender_email and reciever_email and sender_password:
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

                logger.info('Sender email, reciever email and sender password have been updated.')
                print('INFO: Sender email, reciever email and sender password have been updated.')

            else:
                if sender_email:
                    self.sender_email = sender_email
                    with open('utils/credentials.pickle', 'rb') as save_file:
                        creds = pickle.load(save_file)
                    creds['sender_email'] = self.sender_email
                    with open('utils/credentials.pickle', 'wb') as save_file:
                        pickle.dump(creds, save_file)
                    logger.info('Sender email has been updated.')
                    print('INFO: Sender email has been updated.')
                
                if reciever_email:
                    self.reciever_email = reciever_email
                    with open('utils/credentials.pickle', 'rb') as save_file:
                        creds = pickle.load(save_file)
                    creds['reciever_email'] = self.reciever_email
                    with open('utils/credentials.pickle', 'wb') as save_file:
                        pickle.dump(creds, save_file)
                    logger.info('Reciever email has been updated.')
                    print('INFO: Reciever email has been updated.')

                if sender_password:
                    self.sender_password = sender_password
                    with open('utils/credentials.pickle', 'rb') as save_file:
                        creds = pickle.load(save_file)
                    creds['sender_password'] = self.sender_password
                    with open('utils/credentials.pickle', 'wb') as save_file:
                        pickle.dump(creds, save_file)
                    logger.info('Sender password has been updated.')
                    print('INFO: Sender password has been updated.')

                
        else:
            # load input

            with open('utils/credentials.pickle', 'rb') as save_file:
                creds = pickle.load(save_file)

            self.sender_email = creds['sender_email']
            self.reciever_email = creds['reciever_email']
            self.sender_password = creds['sender_password']
            logger.info('Credentials for EmailHandler have been set, sender_email: {}, reciever_email: {}'.format(self.sender_email, self.reciever_email))
            print('INFO: Credentials for EmailHandler have been set, sender_email: {}, reciever_email: {}'.format(self.sender_email, self.reciever_email))

    
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

            logger.info('Sender email and password verified.')
            print('INFO: Sender email and password verified.')
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.warn('Invalid credentials for sender email and passsword.')
            print('WARN: Invalid credentials for sender email and passsword.')
            return False
            
    
    
    def send_email(
        self,
        message: str = '',
        send_as_attachment = False
    ) -> None:
        '''
        Sends an email with the passed message.
        If send_as_attachment is true, assume message is in HTML and parses it.
        '''
        logger.info('Sending email with message "{}"'.format(message))
        print('INFO: Sending email with message "{}"'.format(message))
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
            logger.info('Email sent.')
            print('INFO: Email sent.')
                
                
    def read_email(
        self
    ) -> Tuple:
        '''
        Reads the email from inbox.
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
                            logger.info('Found email that has not been sent by the user, ignoring.')
                            print('INFO: Found email that has not been sent by the user, ignoring.')
                            continue


                        email_datetime = dateparser.parse(msg['date'])

                        if msg.is_multipart():
                            for payload in msg.get_payload()[:1]:
                                return payload.get_payload(), email_datetime
                        else:
                            return msg.get_payload(), email_datetime  

        except Exception as e:
            logger.error('Exception while reading email: {}'.format(str(e)))
            print('ERROR: Exception while reading email - {}'.format(str(e)))


    def preprocess_email_content(
        self,
        email: Tuple
    ) -> Tuple:
        print('INFO: Preprocessing email...', end = '')
        for index, char in enumerate(email[0]):
            if char == '\n':
                temp, o2 = email[0][:index-1].split(',')
                print('DONE')
                return temp, o2, email[1]

if __name__ == '__main__':
    obj = EmailHandler()
    obj.send_email('this is a test')
    print(obj.preprocess_email_content(obj.read_email()))
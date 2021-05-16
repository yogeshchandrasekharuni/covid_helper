from email_handler.email_handler import EmailHandler
from data.db_handler import DBHandler
from datetime import datetime
import sqlite3
from pdb import set_trace
from pprint import pprint
from typing import List, Tuple
import dateparser
import pandas as pd
from pdb import set_trace
from logs.base_logger import logger

class App:
    '''
    CovidHelper App class. Loops infinitely to read and send emails.
    '''

    def __init__(
        self
    ) -> None:
        '''
        Initializes the app
        '''

        self.email_handler = EmailHandler()
        self.db_handler = DBHandler(sqlite3.connect('data/readings.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False))
        self.n_reading_reminder_emails: int = 0
        self.n_daily_table_emails: int = 0
        self.n_recieved_reading_emails: int = 0
        print('INFO: App has been initialized.')
        logger.info('App initialized.')
        
    
    def main(
        self,
        frequency: int = 60 * 60 * 2, # seconds * minutes * n_hours
        last_sent: datetime = None, # last sent email
        time_to_send_readings: Tuple[str] = ('1:33 PM', '2 PM') # time to send out readings
    ) -> None:
        '''
        Main function, contains an infinite while loop.
        '''

        def has_been_freq(
            last_sent: datetime
        ) -> bool:
            '''
            Checks if it has been <frequency> seconds from the last sent email.
            '''

            if not last_sent:
                return True
            if (datetime.now() - last_sent).total_seconds() >= frequency:
                return True
            return False
        
        
        
        flag = 2
        while True:
            time_to_send_readings_start = dateparser.parse(time_to_send_readings[0])
            time_to_send_readings_end = dateparser.parse(time_to_send_readings[1])
                     
            if has_been_freq(last_sent = last_sent):
                # send out email every 2 hours
                flag += 1
                self.email_handler.send_email(message = 'Enter your temperature and oxygen saturation in the format of <Temperature, O2-Saturation>')
                self.n_reading_reminder_emails += 1
                last_sent = datetime.now()
                

            # get readings
            temperature, oxy_satch, time = self.email_handler.preprocess_email_content(self.email_handler.read_email())
    
            if not self.db_handler.is_time_in_table(time):
                print('INFO: Recieved new email, saving readings.')
                self.n_recieved_reading_emails += 1
                logger.info('Added row with values {} and {}.'.format(temperature, oxy_satch))
                self.db_handler.set_readings(temp = temperature, o2 = oxy_satch, curr_time = time)
            else:
                print('INFO: Recieved already present email, continuing.')
            

            curr_time = datetime.now()
            if curr_time >= time_to_send_readings_start and curr_time <= time_to_send_readings_end and flag > 1:
                logger.info('Sending an email with the readings.')
                flag = 0
                df = pd.DataFrame(self.get_todays_readings(), columns = ['ID', 'Temperature', 'O2-Saturation', 'Time'])

                def get_readable_time(x):
                    return x.strftime("%I:%M %p - %d/%m/%Y")

                df.Time = df.Time.apply(get_readable_time)
                to_send = '<h2>Readings for today:</h2>\n'  + df.to_html()

                if df.empty:
                    to_send = 'No readings have been recorded today.'
                    
                self.email_handler.send_email(message = to_send, send_as_attachment = True)
                self.n_daily_table_emails += 1                
                
                
    def get_todays_readings(
        self,
    ) -> List[Tuple]:
        '''
        Returns list of readings for today
        '''
        
        def get_only_today(
            vals: List[Tuple]
        ) -> List[Tuple]:
            '''
            Filters out other days' readings
            '''
            
            new_list = []
            
            for index, tuple_i in enumerate(vals):
                if tuple_i[-1].date() == datetime.today().date():
                    new_list.append(tuple_i)
        
            return new_list
        
        vals = get_only_today(self.db_handler.get_all_values())
        return vals

if __name__ == '__main__':
    app = App()
    app.main()
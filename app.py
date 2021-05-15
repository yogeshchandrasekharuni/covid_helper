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

class App:
    def __init__(
        self
    ) -> None:
        self.email_handler = EmailHandler()
        self.db_handler = DBHandler(sqlite3.connect('data/readings.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False))
        self.n_reading_reminder_emails: int = 0
        self.n_daily_table_emails: int = 0
        self.n_recieved_reading_emails: int = 0
        
    
    def main(
        self,
        frequency: int = 10,
        last_sent: datetime = None,
        time_to_send_readings: Tuple[str] = ('1 PM', '1:30 PM')
    ):
        def has_been_freq(
            last_sent: datetime
        ):
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
                print('Sending request email for readings...', end='')
                self.email_handler.send_email(message = '[TEST] Enter your temperature and oxygen saturation')
                temperature, oxy_satch, time = self.email_handler.preprocess_email_content(self.email_handler.read_email())
                self.n_reading_reminder_emails += 1
                last_sent = datetime.now()
                print('DONE')
                
                if self.db_handler.is_time_in_table(time):
                    print('Time already in table - continuing...')
                    continue
                
                self.n_recieved_reading_emails += 1
                print('Setting values {} and {}...'.format(temperature, oxy_satch), end='')
                self.db_handler.set_readings(temp = temperature, o2 = oxy_satch, curr_time = time)
                print('DONE')
                
            
            curr_time = datetime.now()
            if curr_time >= time_to_send_readings_start and curr_time <= time_to_send_readings_end and flag > 1:
                print('Sending readings email...', end='')
                flag = 0
                df = pd.DataFrame(self.get_todays_readings(), columns = ['ID', 'Temperature', 'O2-Saturation', 'Time'])
                to_send = df.to_html()
                
                if df.empty:
                    to_send = 'No readings have been recorded today.'
                    
                self.email_handler.send_email(message = to_send, send_as_attachment = True)
                self.n_daily_table_emails += 1
                print('DONE')
                
                
                
    def get_todays_readings(
        self,
    ) -> List[Tuple]:
        
        def get_only_today(
            vals: List[Tuple]
        ) -> List[Tuple]:
            
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
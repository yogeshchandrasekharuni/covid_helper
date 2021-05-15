import sqlite3
from datetime import date, datetime, timezone, timedelta
from pdb import set_trace
from pprint import pprint
import django.db.backends.sqlite3.base
from typing import List, Tuple
from logs.base_logger import logger

class DBHandler:
    '''
    Handles all the querying from our database
    '''
    
    def __init__(
        self,
        conn: sqlite3.Connection = None
    ) -> None:
        
        logger.info('Class DBHandler has been initialized.')
        self.conn = conn if conn else sqlite3.connect('readings.db', detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()

        self.create_table()
        
    
    def create_table(
        self
    ):
        '''
        Creates a table if does not already exist
        '''
        
        query = '''
        CREATE TABLE IF NOT EXISTS readings(
            id INT PRIMARY KEY,
            temperature FLOAT,
            oxygen INT,
            time TIMESTAMP
        )
        '''
        with self.conn:
            self.cursor.execute(query)

        logger.info('Table has been checked or created.')
        return
            
    
    def get_latest_id(
        self
    ) -> int:
        query = '''
        SELECT MAX(id) FROM readings
        '''
        self.cursor.execute(query)
        max_id = self.cursor.fetchone()[0]
        return max_id + 1 if max_id else 1
            
            
    def set_readings(
        self,
        temp: float,
        o2: int,
        curr_time: datetime
    ) -> None:
        '''
        Inserts a new row with the given readings
        '''
        
        curr_id = self.get_latest_id()
        
        query = f'''
        INSERT INTO readings VALUES(
            {curr_id},
            {temp},
            {o2},
            '{curr_time}'
        )
        '''
        
        with self.conn:
            self.cursor.execute(query)

        logger.info('Readings with id: {} has been inserted into the table.'.format(curr_id))
        return
            
    def get_n_latest_readings(
        self,
        n_readings: int,
    ) -> list:
        '''
        Retrieves n latest readings
        '''
        
        n_readings = min(n_readings, self.get_latest_id())

        query = f'''
        SELECT temperature, oxygen, time FROM readings
        ORDER BY id DESC
        LIMIT {n_readings}
        '''

        self.cursor.execute(query)
        return self.convert_to_local(self.cursor.fetchall())
    
    
    def get_time(self):
        query = '''
        SELECT time as "[timestamp]" FROM readings
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    
    def utc_to_local(self, x):
        return (x[0], x[1], x[2].replace(tzinfo=timezone.utc).astimezone(tz=None))
    
    def convert_to_local(self, outputs):
        return list(
            map(
                self.utc_to_local,
                outputs
            )
        )
    
    
    def is_time_in_table(
        self,
        time: datetime
    ) -> bool:
        
        query = f'''
        SELECT EXISTS (SELECT 1 FROM readings WHERE readings.time = '{time}')
        '''
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    def get_all_values(
        self
    ) -> List[Tuple]:
        
        query = f'''
        SELECT * FROM readings
        '''
        
        self.cursor.execute(query)
        return self.cursor.fetchall()

if __name__ == '__main__':
    conn = sqlite3.connect('readings.db', detect_types=sqlite3.PARSE_DECLTYPES)
    obj = DBHandler()
    
    handler = DBHandler(conn)
    handler.set_readings(temp = 98, o2 = 96, curr_time = datetime.now())
    handler.set_readings(temp = 96, o2 = 94, curr_time = datetime.now())

    pprint(handler.get_n_latest_readings(4))
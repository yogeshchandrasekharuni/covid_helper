import logging
from datetime import datetime

class NotLogging:
    '''
    Turns off logging
    '''
    def __init__(self):
        self.INFO, self.WARN, self.ERROR = None, None, None
        print('Logging has been turned off.')
        return None
    
    def __call__(self, *args, **kwargs):
        return None
    
    def info(self, *args, **kwargs):
        return None
    
    def warn(self, *args, **kwargs):
        return None
    
    def error(self, *args, **kwargs):
        return None
    
    def basicConfig(self, *args, **kwargs):
        return None

logger = logging

_f_name = datetime.now().strftime('logs_%H_%M_%d_%m_%Y.log')
logger.basicConfig(
    filename = 'logs/' + _f_name,
    format = '%(asctime)s - %(levelname)s: %(message)s',
    datefmt = '%m/%d/%Y-%I:%M:%S-%p',
    level = logging.INFO
)

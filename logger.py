import os
import sys


def get_dir(path):
    return '/'.join(path.split('/')[:-1])


class Logger(object):
    def __init__(self, log_file, console=True):
        self.terminal = sys.stdout
        self.log = open(log_file, 'w', encoding='utf-8')
        self.console = console
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        if self.console:
            self.terminal.flush()
            self.log.flush()
            
    def flush(self):
        pass


def set_logger(log_file, console=True):
    # redirect print function to logger
    dir_ = get_dir(log_file)
    os.makedirs(dir_, exist_ok=True)
    logger = Logger(log_file, console)
    sys.stdout = logger

def reset_logger():
    sys.stdout = sys.__stdout__

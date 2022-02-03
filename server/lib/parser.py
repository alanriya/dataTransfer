from lib.config import DEFAULT_PATH
from lib.publisher import Publisher
from lib.utils import *
from multiprocessing import Process, Lock, Queue
import sys, os

sys.path.append(os.getcwd())

class Parser:
    def __init__(self, publisher: Publisher, file: str) -> None:
        self.publisher = publisher
        self.file = file
        self.queue = Queue()
    
    def process(self) -> None:
        # main event loop
        count = 1
        start_message = True
        with open(f"{DEFAULT_PATH}{self.file}", "rb") as f:
            while True:
                flag = f.read(1)
                if flag == b'':
                    break
                if start_message == True:
                    start_message = False 
                    if flag == b'\x11':
                        bytes_read = f.read(39)
                        current_status = read_header(bytes_read, self.file)
                        self.publisher.publish(current_status)
                elif start_message == False:
                    if flag == b'\x12' or flag == b'\x13': 
                        tag = f.read(2).decode('utf8')
                        tag_data = self.decipher(f, tag)
                        self.publisher.publish(tag_data)
                    elif flag == b'\x11': # End of message
                        start_message = True
                count+=1



    @staticmethod
    def decipher(context , tag : str):
        if tag == 'NO':
            return get_NO_message(context,tag)
        elif tag == '1P':
            return get_1P_message(context,tag)
        elif tag == 'ST': 
            return get_ST_message(context,tag)
        elif tag == 'VL':
            return get_VL_message(context, tag)
        elif tag == 'VA':
            return get_VA_message(context, tag)
        elif tag == 'QS':
            return get_QS_message(context, tag)
        elif tag == 'QB':
            return get_QB_message(context, tag)
        elif tag == 'SC': 
            return get_SC_message(context, tag)
        elif tag == 'BC':
            return get_BC_message(context, tag)
        elif tag == 'LC':
            return get_LC_message(context, tag)



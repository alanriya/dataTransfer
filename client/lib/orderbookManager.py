from time import strftime
from lib.orderbook import OrderBook
from collections import defaultdict
import pdb


class OrderBookManager:
    def __init__(self) -> None:
        self.symbols_orderbook = defaultdict()
        self.symbols_sequence_num = defaultdict(lambda : 1)
        self.symbols_status = defaultdict()
        self.current_header = defaultdict()
        self.current_datetime = None
        self.current_date = None
        self.current_symbol = None
        self.current_timestamp_messages = []
        
    def add(self, msg) -> None:
        if msg["tag"] == "H":
            self.current_header = msg
            self.current_date = self.process_current_date(msg)
            self.current_symbol = msg.get("issuecode")
        elif msg["tag"] == "NO":
            pass
        elif msg["tag"] == "ST":
            self.update_status(msg)
            if msg["tradingstatus"] == '40':
                self.symbols_orderbook[self.current_symbol].funari_orders = list()
        else:
            time_name = self.decipher_time_field(msg["tag"])
            datetime_now = self.process_current_datetime(msg, time_name)
            if (self.current_datetime is not None 
                and self.current_datetime != datetime_now 
                and len(self.current_timestamp_messages) != 0):
                m = self.current_timestamp_messages[0]
                self.symbols_orderbook[m["symbol"]].load_message(self.current_timestamp_messages)
                self.current_timestamp_messages = list()
            msg["messagetime"] = datetime_now
            self.current_datetime = datetime_now
            msg["seqno"] = self.symbols_sequence_num[self.current_symbol]
            msg["symbol"] = self.current_symbol 
            self.seq_no_increment(self.current_symbol)
            if self.current_symbol not in self.symbols_orderbook:
                self.symbols_orderbook[self.current_symbol] = OrderBook(self.current_symbol)    
            self.current_timestamp_messages.append(msg)
        
    def update_status(self, msg) -> None:
        self.symbols_status[self.current_symbol] = msg["tradingstatus"]

    def seq_no_increment(self, symbol):
        self.symbols_sequence_num[symbol] += 1

    @staticmethod
    def process_current_date(msg: dict) -> str:
        date_str = msg["date"]
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

    def process_current_datetime(self, msg: dict, time_name: str) -> str:
        time = msg[time_name]
        return f"{self.current_date} {time[0:2]}:{time[2:4]}:{time[4:6]}.{time[6:]}+09"

    @staticmethod
    def decipher_time_field(tag: str) -> str:
        if tag == "ST":
            return "issuestatustime"
        else: 
            return "messagetime"
            


        

    
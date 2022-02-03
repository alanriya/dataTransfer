from collections import defaultdict
from lib.publisher import DisplayPublisher
from sortedcontainers import SortedDict
import numpy as np
from lib.config import display_conn
import copy
import pdb
class OrderBook:
    def __init__(self, symbol):
        self.symbol = symbol
        self.bid_levels = SortedDict()
        self.ask_levels = SortedDict()
        self.on_close_bid_levels = SortedDict()
        self.on_close_ask_levels = SortedDict()
        self.bid_market_level = [0,0]
        self.ask_market_level = [0,0]
        self.on_close_bid_market_level = [0,0]
        self.on_close_ask_market_level = [0,0]
        self.trade_info = [0] * 3
        self.current_time = None
        self.funari_orders = list()
        self.bid_level_prev = defaultdict(lambda : [0,0])
        self.ask_level_prev = defaultdict(lambda : [0,0])
        self.on_close_bid_market_prev = [0,0]
        self.on_close_ask_market_prev = [0,0]
        self.microprice = None
        self.mergedbook = SortedDict()
        self.mergedbook[float("inf")] = [0, 0]
        self.mergedbook[-float("inf")] = [0, 0] 
    
    @staticmethod
    def get_level_info(price, qty, no):
        price = float(price)
        qty = qty
        if qty == '':
            qty = 0
        else:
            qty = int(qty)
        no = no
        if no == "":
            no = 0
        else:
            no = int(no)

        return price, qty, no
    
    def itayose(self):
        limits = np.array(self.mergedbook.values())
        bid_cum = np.cumsum(np.flip(limits[:,0]))
        ask_cum = np.cumsum(limits[:,1])
        prices = list(self.mergedbook)
        tipping_vol = bid_cum - ask_cum
        for i in range(1, len(tipping_vol)):
            if tipping_vol[i-1] < 0 and tipping_vol[i] == 0:
                self.microprice = prices[i]
            elif tipping_vol[i-1] < 0 and tipping_vol[i] > 0:
                self.microprice = (prices[i-1] + prices[i]) /2 


    def update_level(self, message:dict, orderbookside: SortedDict):
        price, qty, no = self.get_level_info(message.get("price"), message.get("qty"), message.get("no"))
        orderbookside[price] = [qty, no]

    def modify_market_level(self, message:dict, orderbookside: list):
        _, qty, no = self.get_level_info("0", message.get("qty"), message.get("no"))
        orderbookside[:] = [qty, no]
    
    def modify_trade_price(self, message:dict, orderbookside: list):
        orderbookside[0] = message.get("price")

    def modify_trade_qty(self, message:dict, orderbookside: list):
        orderbookside[1] = message.get("totalvolume")
    
    def modify_turnover_qty(self, message:dict, orderbookside: list):
        orderbookside[2] = message.get("turnovervalue") 

    def add_mb(self, message:dict):
        price, qty, _ = self.get_level_info(message.get("price"), message.get("qty"), message.get("no"))
        if price not in self.mergedbook:
            # bid and ask volume
            self.mergedbook[price] = [0,0]    
        if message["tag"] == "QB":
            self.update(price, qty, 0, self.on_close_bid_levels)
        elif message["tag"] == "QS":
            self.update(price, qty, 1, self.on_close_ask_levels)
        elif message["tag"] == "BC":
            self.update(price, qty, 0, self.bid_levels)
        elif message["tag"] == "SC":
            self.update(price, qty, 1, self.ask_levels)
    
    def delete_mb(self, message:dict):
        price, _ , _ = self.get_level_info(message.get("price"), message.get("qty"), message.get("no"))
        if price not in self.mergedbook:
            # bid and ask volume
            self.mergedbook[price] = [0,0]    
        if message["tag"] == "QB":
            self.update(price, 0, 0, self.on_close_bid_levels)
        elif message["tag"] == "QS":
            self.update(price, 0, 1, self.on_close_ask_levels)
        elif message["tag"] == "BC":
            self.update(price, 0, 0, self.bid_levels)
        elif message["tag"] == "SC":
            self.update(price, 0, 1, self.ask_levels)

    def update(self, price: float, qty: int, pos: int, orderbookside):
        if price in orderbookside:
            self.mergedbook[price][pos] = qty + copy.deepcopy(orderbookside[price][0])
        else:
            self.mergedbook[price][pos] = qty

    def add_market_mb(self, message:dict):
        qty = int(message.get("qty"))
        price = None
        if message["tag"] in ["QB", "BC"]:
            price = float("inf")
        if message["tag"] in ["QS", "SC"]:
            price = -float("inf")
        if message["tag"] == "QB":
            self.mergedbook[price][0] = qty + self.on_close_bid_market_level[0]
        elif message["tag"] == "BC":
            self.mergedbook[price][0] = qty + self.bid_market_level[0]
        elif message["tag"] == "QS":
            self.mergedbook[price][1] = qty + self.on_close_ask_market_level[0]
        elif message["tag"] == "SC":
            self.mergedbook[price][1] = qty + self.ask_market_level[0]

    def delete_market_mb(self, message:dict):
        price = None
        qty = 0
        if message["tag"] in ["QB", "BC"]:
            price = float("inf")
        if message["tag"] in ["QS", "SC"]:
            price = -float("inf")
        if message["tag"] == "QB":
            self.mergedbook[price][0] = qty + self.on_close_bid_market_level[0]
        elif message["tag"] == "BC":
            self.mergedbook[price][0] = qty + self.bid_market_level[0]
        elif message["tag"] == "QS":
            self.mergedbook[price][1] = qty + self.on_close_ask_market_level[0]
        elif message["tag"] == "SC":
            self.mergedbook[price][1] = qty + self.ask_market_level[0]
        
    def update_merged_book(self, message: dict):
        if message.get("tag") in ["QB", "QS", "BC", "SC"] and message.get("price") != "" and message.get("qty") != "0":
            self.add_mb(message)
        elif message.get("tag") in ["QB", "QS", "BC", "SC"] and message.get("price") != "" and message.get("qty") == "0":
            self.delete_mb(message)
        elif message.get("tag") in ["QB", "QS", "BC", "SC"] and message.get("price") == "" and message.get("qty") != "0":    
            self.add_market_mb(message)
        elif message.get("tag") in ["QB", "QS", "BC", "SC"] and message.get("price") == "" and message.get("qty") == "0":    
            self.delete_market_mb(message)
        

    def message_update(self, message: dict):
        self.current_time = message.get("messagetime")
        if message.get("tag") == "QB" and message.get("price") != '':
            self.update_level(message, self.bid_levels)
            self.bid_level_prev[float(message.get("price"))] = copy.deepcopy(self.bid_levels[float(message.get("price"))])
            self.update_merged_book(message)
        elif message.get("tag") == "QB" and message.get("price") == '':
            self.modify_market_level(message, self.bid_market_level)
            self.update_merged_book(message)
        elif message.get("tag") == "QS" and message.get("price") != '':
            self.update_level(message, self.ask_levels)
            self.ask_level_prev[float(message.get("price"))] = copy.deepcopy(self.ask_levels[float(message.get("price"))])
            self.update_merged_book(message)
        elif message.get("tag") == "QS" and message.get("price") == '':
            self.modify_market_level(message, self.ask_market_level)
            self.update_merged_book(message)
        elif message.get("tag") == "SC" and message.get("price") != '':
            self.update_level(message, self.on_close_ask_levels)
            self.update_merged_book(message)
        elif message.get("tag") == "BC" and message.get("price") != '':
            self.update_level(message, self.on_close_bid_levels)
            self.update_merged_book(message)
        elif message.get("tag") == "SC" and message.get("price") == '':
            self.modify_market_level(message, self.on_close_ask_market_level)
            self.on_close_ask_market_prev = copy.deepcopy(self.on_close_ask_market_level)
            self.update_merged_book(message)
        elif message.get("tag") == "BC" and message.get("price") == '':
            self.modify_market_level(message, self.on_close_bid_market_level)
            self.on_close_bid_market_prev = copy.deepcopy(self.on_close_bid_market_level)
            self.update_merged_book(message)
        elif message.get("tag") == "1P":
            self.modify_trade_price(message, self.trade_info)
        elif message.get("tag") == "VL":
            self.modify_trade_qty(message, self.trade_info)
        elif message.get("tag") == "VA":
            self.modify_turnover_qty(message, self.trade_info)
        else:
            pass
        print(self.__str__())

    def load_message(self, messages: list) -> None:
        on_close = []
        limit = []
        final = []
        if len(messages) == 1:
            self.message_update(messages[0])
        else:
            # separate the on-close with limit orders.
            # if the on-close delta and the limit order delta is same. funari order happen 
            # and remove the order from the on-market orders.
            # reset the funari when the session ends.
            for m in messages:
                if m["tag"] in ["1P", "VL", "VA"]:
                    final.append(m)
                elif m["tag"] in ["QB", "QS"]:
                    if m.get("price") != "": 
                        m_delta = self.add_on_delta(m, m.get("tag"))
                        limit.append(m_delta)
                    else:
                        final.append(m)
                elif m["tag"] in ["BC", "SC"]:
                    if m.get("price") == "":
                        m_delta = self.add_on_delta(m, m.get("tag"))
                        on_close.append(m_delta)
                    else:
                        final.append(m)

        remove_moc_idx = []
        remove_limit_idx = []
        on_close_final = []
        for moc_idx in range(len(on_close)):
            for limit_order_idx in range(len(limit)):
                if (limit_order_idx not in remove_limit_idx 
                and remove_moc_idx not in remove_moc_idx 
                and on_close[moc_idx]["qty_delta"] == limit[limit_order_idx]["qty_delta"] 
                and on_close[moc_idx]["no_delta"] == limit[limit_order_idx]["no_delta"]):
                    self.funari_orders.append(limit_order_idx)
                    remove_moc_idx.append(moc_idx) 
                    remove_limit_idx.append(limit_order_idx)
        for idx in range(len(on_close)):
            if idx not in remove_moc_idx:
                on_close_final.append(on_close[idx])

        for message in final + limit + on_close_final :
            self.message_update(message)

    def add_on_delta(self, message:dict, tag: str) -> dict:
        qty = int(message["qty"])
        no = int(message["no"])
        if tag == "QB":
            message["qty_delta"] = qty - self.bid_level_prev[float(message["price"])][0]
            message["no_delta"] = no - self.bid_level_prev[float(message["price"])][1]
        elif tag == "QS":
            message["qty_delta"] = qty - self.ask_level_prev[float(message["price"])][0]
            message["no_delta"] = no - self.ask_level_prev[float(message["price"])][1]
        elif tag == "BC":
            message["qty_delta"] = qty - self.on_close_bid_market_prev[0]
            message["no_delta"] = no - self.on_close_bid_market_prev[1]
        elif tag == "SC":
            message["qty_delta"] = qty - self.on_close_ask_market_prev[0]
            message["no_delta"] = no - self.on_close_ask_market_prev[1]
        return message

    def __repr__(self):
        return f"orderbook instance of a single symbol for {self.symbol}"

    def __str__(self):
        """
        Print the order book.
        """
        content = f'''
        symbol: {self.symbol}
        time : {self.current_time} 
        ------------show orderbook--------------
        merged book: {self.mergedbook}
        trade information : {self.trade_info}
        ----------------------------------------
        '''
        return content
        

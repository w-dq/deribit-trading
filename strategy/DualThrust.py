
import logging
import asyncio
import websockets
import json
from datetime import datetime

# logging.basicConfig(filename='../run.log', level=logging.INFO,format='[%(asctime)s][DualThrust]: %(message)s')

from .Signal import Signal

MAX_P = 10000000
MIN_P = 0

class DualThrust():
    def __init__(self,logger, instrument_name, k1 = 0.5, k2=0.5, period = 5,):
        self.instrument = instrument_name
        self._k1 = k1
        self._k2 = k2
        self._period = period

        self.data_list = [None] * period
        self.head_idx = -1

        self.latest_timestamp = int(datetime.now().timestamp() * 1000)
        self.lates_data = dict()
        self.last_close = 0

        self.thrust_range = 0
        self.position = 0
        self.buy_level = 0
        self.sell_level = 0

        self.logger = logger
    
    def get_subscribe_channles(self):
        return ["chart.trades.BTC-PERPETUAL.1"]
    
    def push_new_data(self,data):
        if self.head_idx > self._period:
            new_price  = data["close"]
            if not self.position:
                if new_price > self.buy_level:
                    return Signal("buy",new_price,1000,"market",self.instrument,self.logger)
            elif new_price < self.sell_level:
                return Signal("close",new_price,self.position,"market",self.instrument,self.logger)
        return None
    
    def update_list(self,data):
        self.head_idx += 1
        self.data_list[self.head_idx % self._period] = self.lates_data
        self.last_close = data["close"]
        print(self.head_idx,self._period)
        self.logger.info(f"head is at:{self.head_idx}, waiting period: {self._period}")
        if self.head_idx > self._period:
            high = MIN_P
            low = MAX_P
            for d in self.data_list:
                if high < d["high"]:
                    high = d["high"]
                if low > d["low"]:
                    low = d["low"]
            
            self.thrust_range = high - low
            self.buy_level = self.last_close + self._k1 * self.thrust_range
            self.sell_level = self.last_close - self._k2 * self.thrust_range
            self.logger.info("thrust range:{} buy_level:{}, sell_level:{}".format(self.thrust_range,
                                                                              self.buy_level,
                                                                              self.sell_level))
        self.latest_timestamp = data["tick"]
    
    def on_data(self,data):
        if data["tick"] != self.latest_timestamp:
            self.update_list(data)
        self.lates_data = data

        return self.push_new_data(data)
    
    def confirm_msg(self,msg):
        if "error" in msg:
            self.logger.error(msg)
        elif "result" in msg:
            result  = msg["result"]
            for trade in result["trades"]:
                if trade["direction"] == "buy":
                    self.position += trade["amount"]
                else:
                    self.position -= trade["amount"]
                self.logger.info("{} trade confirmed amount:{} price:{} fee:{}{}".format(trade["direction"],
                                                                                     trade["amount"],
                                                                                     trade["price"],
                                                                                     trade["fee"],
                                                                                     trade["fee_currency"]))
        else:
            self.logger.warning(msg)

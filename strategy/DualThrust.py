
import logging

logging.basicConfig(filename='logs/.log', level=logging.INFO,format='[%(asctime)s][%(name)s]: %(message)s')


class DualThrust():
    def __init__(self, instrument_name, k1 = 0.5, k2=0.5, period = 5):
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
    
    def push_new_data(self,data):
        if data["tick"] != self.latest_timestamp:
            self.update_list(data)
        self.lates_data = data

        return self.on_data(data)
    
    def update_list(self,data):
        self.head_idx += 1
        self.data_list[self.head_idx % self._period] = self.lates_data
        self.last_close = data["close"]
        print(self.head_idx,self._period)
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
            # print("thrust range",self.thrust_range,self.buy_level,self.sell_level)
            logging.info("thrust range:{} buy_level:{}, sell_level:{}".format(self.thrust_range,
                                                                              self.buy_level,
                                                                              self.sell_level))

        self.latest_timestamp = data["tick"]
    
    def on_data(self,data):
        if self.head_idx > self._period:
            new_price  = data["close"]
            if not self.position:
                if new_price > self.buy_level:
                    return Signal("buy",new_price,100,"market",self.instrument)
            elif new_price < self.sell_level:
                return Signal("close",new_price,self.position,"market",self.instrument)

        return None
    
    def confirm_msg(self,msg):
        if "error" in msg:
            logging.error(msg)
        elif "result" in msg:
            result  = msg["result"]
            for trade in result["trades"]:
                if trade["direction"] == "buy":
                    self.position += trade["amount"]
                else:
                    self.position -= trade["amount"]
                logging.info("{} trade confirmed amount:{} price:{} fee:{}{}".format(trade["direction"],
                                                                                     trade["amount"],
                                                                                     trade["price"],
                                                                                     trade["fee"],
                                                                                     trade["fee_currency"]))
        else:
            logging.warning(msg)


import asyncio
import websockets
import json
from datetime import datetime

from messages import auth_msg,logout_msg,subscribe_msg

import logging
logging.basicConfig(filename='logs/dt.log', level=logging.INFO,format='[%(asctime)s][%(name)s]: %(message)s')

MAX_P = 10000000
MIN_P = 0

base_wss = 'wss://test.deribit.com/ws/api/v2'

class Signal():
    def __init__(self,direction,price,size,order_type,instrument):
        self.method = direction
        self.price = price
        self.amount = size
        self.order_type = order_type
        self.instrument = instrument
    
    def gen_msg(self):
        msg = {
            "jsonrpc": "2.0",
            "id": 6655
        }
        if self.method == "buy":
            msg["method"] = "private/buy"
            if self.order_type == "market":
                msg["params"] = {
                    "instrument_name": self.instrument,
                    "amount": self.amount,
                    "type": "market"
                }
            elif self.order_type == "limit":
                msg["params"] = {
                    "instrument_name": self.instrument,
                    "amount": self.amount,
                    "type": "limit",
                    "price": self.price
                }
        elif self.method == "close":
            msg["method"] = "private/close_position"
            msg["params"] = {
                "instrument_name": self.instrument,
                "type": "market"
            }
        
        logging.info(f"{self.method} {self.order_type} order sent at price {self.price} and amount {self.amount}")
        return msg

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

        


async def call_api(strategy):
   async with websockets.connect(base_wss) as websocket:
        await websocket.send(json.dumps(auth_msg))
        response = await websocket.recv()
        response = json.loads(response)
        if "error" in response:
            print("ERROR in AUTH")
            return
        access_token = response["result"]["access_token"]
        logout_msg["params"]["access_token"] = access_token

        channels = ["chart.trades.BTC-PERPETUAL.1"]
        subscribe_msg["params"]["channels"] = channels

        await websocket.send(json.dumps(subscribe_msg))
        while websocket.open:
            response = await websocket.recv()
            response = json.loads(response)
            if "id" in response:
                print("id:",response["id"])
            elif response["method"] == "subscription" and response["params"]["channel"] in channels:
                signal = strategy.push_new_data(response["params"]["data"])
                if signal:
                    await websocket.send(json.dumps(signal.gen_msg()))
                    response = await websocket.recv()
                    response = json.loads(response)
                    strategy.confirm_msg(response)
            else:
                print(response)

        await websocket.send(json.dumps(logout_msg))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    strategy = DualThrust("BTC-PERPETUAL",0.2,0.2,1)
    loop.run_until_complete(call_api(strategy))
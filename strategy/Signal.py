
import logging

# logging.basicConfig(filename='../run.log', level=logging.INFO, format='[%(asctime)s][Signal]: %(message)s')

class Signal():
    def __init__(self,direction,price,size,order_type,instrument,logger):
        self.method = direction
        self.price = price
        self.amount = size
        self.order_type = order_type
        self.instrument = instrument

        self.logger = logger
        
    
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
        
        self.logger.info(f"{self.method} {self.order_type} order sent at price {self.price} and amount {self.amount}")
        return msg
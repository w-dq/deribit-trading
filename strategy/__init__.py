
from .DualThrust import DualThrust
from .TestStrategy import TestStrategy

import logging

class BaseStrategy():
    def __init__(self):
        self.logger = logging.getLogger("BASE")
    
    def on_data(self,data):
        self.logger.INFO("New data point recieved")
        return None

    def get_subscribe_channles(self):
        return ["chart.trades.BTC-PERPETUAL.1"]

    def confirm_msg(self,msg):
        self.logger.INFO("Confirm on order placed")
        
    


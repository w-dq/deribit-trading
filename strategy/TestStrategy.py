
import logging

# logging.basicConfig(filename='../run.log', level=logging.INFO,format='[%(asctime)s][TestStrategy]: %(message)s')

from .Signal import Signal

class TestStrategy():
    def __init__(self, instrument_name):
        self.instrument = instrument_name

    def get_subscribe_channles(self):
        return ["chart.trades.BTC-PERPETUAL.1"]
    
    def on_data(self,data):
        logging.info("Recieve Data")
        pass
    
    def confirm_msg(self,msg):
        logging.info("Confirmed Message")
        pass

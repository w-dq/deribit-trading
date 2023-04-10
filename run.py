
import asyncio
import websockets
import json
from datetime import datetime

from messages import auth_msg,logout_msg,subscribe_msg

from 


def call_api(strategy):



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # TODO: load strategy
    strategy = DualThrust("BTC-PERPETUAL",0.2,0.2,1)
    #run strategy
    loop.run_until_complete(call_api(strategy))
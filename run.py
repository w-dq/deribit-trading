
import asyncio
import websockets
import json
from datetime import datetime

from messages import auth_msg,logout_msg,subscribe_msg

from strategy import DualThrust, Signal
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('run.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

base_wss = 'wss://test.deribit.com/ws/api/v2'

async def call_api(strategy):
    async with websockets.connect(base_wss) as websocket:
        await websocket.send(json.dumps(auth_msg))
        response = await websocket.recv()
        response = json.loads(response)
        if "error" in response:
            logger.error("AUTH ERROR!")
            return
        logger.info("Successfully logged on to private method")
        access_token = response["result"]["access_token"]
        logout_msg["params"]["access_token"] = access_token

        channels = strategy.get_subscribe_channles()
        subscribe_msg["params"]["channels"] = channels

        await websocket.send(json.dumps(subscribe_msg))
        logger.info("Subscribe to {}".format(", ".join(channels)))
        while websocket.open:
            response = await websocket.recv()
            response = json.loads(response)
            if "id" in response:
                # TODO: response to non subscribed message
                print("id:",response["id"])
            elif response["method"] == "subscription" and response["params"]["channel"] in channels:
                signal = strategy.on_data(response["params"]["data"])
                if signal:
                    await websocket.send(json.dumps(signal.gen_msg()))
                    response = await websocket.recv()
                    response = json.loads(response)
                    strategy.confirm_msg(response)
            else:
                # TODO: response unexpected message
                print(response)

        await websocket.send(json.dumps(logout_msg))



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # TODO: load strategy
    strategy = DualThrust(logger,"BTC-PERPETUAL",0.2,0.2,1,)
    #run strategy
    loop.run_until_complete(call_api(strategy))
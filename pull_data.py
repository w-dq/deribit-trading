import asyncio
import websockets
import json
from datetime import datetime
from datetime import timedelta
import argparse
import pandas

import pandas as pd

base_wss = 'wss://test.deribit.com/ws/api/v2'


def to_timestamp_in_milliseconds(time_string):
    epoch = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    timestamp_in_milliseconds = int(epoch.timestamp() * 1000)
    return timestamp_in_milliseconds

def to_filename_timestr(stamp_in_milli):
    dt_object = datetime.fromtimestamp(stamp_in_milli/1000)
    dt_string = dt_object.strftime("%Y-%m-%d-%H:%M")
    return dt_string

def get_datetime_col(stamp_in_milli):
    dt_object = datetime.fromtimestamp(stamp_in_milli/1000)
    dt_string = dt_object.strftime("%Y-%m-%d %H:%M")
    return dt_string


async def call_instruments(msg):
    async with websockets.connect(base_wss) as websocket:
        await websocket.send(msg)
        response = await websocket.recv()
        response = json.loads(response)
        try:
            data = response["result"]
            df = pd.DataFrame(data)
            df.insert(0, "instrument_name", df.pop("instrument_name"))
            df.to_csv("instruments.csv", index=False)
        except:
            print("error while dealing with response")

async def call_chart_data(msg):
    async with websockets.connect(base_wss) as websocket:
        await websocket.send(msg)
        response = await websocket.recv()
        response = json.loads(response)
        if "error" in response.keys():
            print(response)
            return _,"error"
        else:
            if response["result"]["status"] == "ok":
                del response["result"]["status"]
                df = pd.DataFrame(response["result"])
                return df,"ok"
            else:
                return df,response["result"]["status"]
        

def get_instruments(currency):
    msg = \
    {
        "jsonrpc" : "2.0",
        "id" : 834,
        "method" : "public/get_instruments",
        "params" : {
            "currency" : currency
        }
    }
    loop = asyncio.get_event_loop()
    loop.run_until_complete(call_instruments(json.dumps(msg)))

def get_data(params):
    msg = \
    {
        "jsonrpc" : "2.0",
        "id" : 833,
        "method" : "public/get_tradingview_chart_data",
        "params" : params
    }
    print(msg)
    loop = asyncio.get_event_loop()
    result_df, status = loop.run_until_complete(call_chart_data(json.dumps(msg)))
    if status == "ok":
        result_df.insert(0,"datetime",result_df['ticks'].apply(get_datetime_col))

        filename = "_".join([params["instrument_name"],
                             to_filename_timestr(result_df["ticks"].iloc[0]),
                             to_filename_timestr(result_df["ticks"].iloc[-1]),
                             params["resolution"]
                            ])

        result_df.to_csv("data/"+filename+".csv", index=False)
    elif status == "no_data":
        print("no data for this set of config! check instrument, time and resolution")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--instruments", action="store_true", help="select to get list of avaliable instruments")
    parser.add_argument("--currency", required=False, default='BTC',
                         help=('Choose related currency: [BTC,ETH,USDC]'))
    args = parser.parse_args()
    if args.instruments:
        # TODO: add kind param
        c = args.currency
        if c not in ["BTC","ETH","USDC"]:
            c = "BTC"
        get_instruments(c)
    else:
        with open("pull_data.json", "r") as f:
            params = json.load(f)
        params["start_timestamp"] = to_timestamp_in_milliseconds(params["start_timestamp"])
        if params["end_timestamp"] == "now":
            params["end_timestamp"] = int(datetime.now().timestamp() * 1000)
        else:
            params["end_timestamp"] = to_timestamp_in_milliseconds(params["end_timestamp"])
        if params["resolution"] in ["1","3","5","10","15","30","60","120","180","360","720","1D"]:
            get_data(params)
        else:
            print("check resolution")
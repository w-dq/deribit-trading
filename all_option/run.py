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
        data = response["result"]
        df = pd.DataFrame(data)
        # df.to_csv("instruments.csv", index=False)
        return list(df["instrument_name"])

async def call_chart_data(msg):
    async with websockets.connect(base_wss) as websocket:
        await websocket.send(msg)
        response = await websocket.recv()
        response = json.loads(response)
        if "error" in response.keys():
            print(response)
            return [],"error"
        else:
            if response["result"]["status"] == "ok":
                del response["result"]["status"]
                df = pd.DataFrame(response["result"])
                return df,"ok"
            else:
                return [],response["result"]["status"]

def get_instruments(currency):
    msg = \
    {
        "jsonrpc" : "2.0",
        "id" : 834,
        "method" : "public/get_instruments",
        "params" : {
            "currency" : currency,
            "kind": "option"
        }
    }
    loop = asyncio.get_event_loop()
    name_list = loop.run_until_complete(call_instruments(json.dumps(msg)))
    return name_list

if __name__ == "__main__":
    all_ins_list = []
    for c in ["BTC","ETH"]:
        temp = get_instruments(c)
        all_ins_list += temp

    msg = \
    {
        "jsonrpc" : "2.0",
        "id" : 833,
        "method" : "public/get_tradingview_chart_data",
        "params" : {
            "instrument_name" : "BTC-29SEP23-28000-C",
            "start_timestamp" : "2018-01-01 00:00:00",
            "end_timestamp" : "now",
            "resolution" : "1D"
        }
    }
    msg["params"]["start_timestamp"] = to_timestamp_in_milliseconds( msg["params"]["start_timestamp"])
    msg["params"]["end_timestamp"] = int(datetime.now().timestamp() * 1000)


    for instrument in all_ins_list:
        print(instrument)
        msg["params"]["instrument_name"] = instrument

        loop = asyncio.get_event_loop()
        result_df, status = loop.run_until_complete(call_chart_data(json.dumps(msg)))

        if status == "ok":
            result_df.insert(0,"datetime",result_df['ticks'].apply(get_datetime_col))
            filename = "_".join([
                                instrument,
                                to_filename_timestr(result_df["ticks"].iloc[0]),
                                to_filename_timestr(result_df["ticks"].iloc[-1]),
                                msg["params"]["resolution"]
                                ])
            result_df.to_csv("all_1D/"+filename+".csv", index=False)
        else:
            print(instrument + ":" + status)

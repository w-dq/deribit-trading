
import asyncio
import websockets
import json
from datetime import datetime
from datetime import timedelta
import argparse
import pandas
from tqdm import tqdm

import csv
import pandas as pd

import requests
import json

ins_url = 'https://history.deribit.com/api/v2/public/get_instruments'

base_url = 'https://history.deribit.com/api/v2/public/get_last_trades_by_instrument'

def run_analysis(name_list,f):
    res = []
    for ins_name in tqdm(name_list[46000:]):
        params = {
            "count": 10000,
            "include_old": True,
            "instrument_name": ins_name
        }
        response = requests.get(base_url, params = params)
        if response.status_code == 200:
            data = json.loads(response.content)
            num_of_trades = len(data["result"]["trades"])
            # print(num_of_trades)
            if num_of_trades > 10:
                first_trade = data["result"]["trades"][-1]
                last_trade = data["result"]["trades"][0]
                f_dt_object = datetime.fromtimestamp(first_trade["timestamp"]/1000)
                f_dt_string = f_dt_object.strftime("%Y-%m-%d %H:%M:%S")

                l_dt_object = datetime.fromtimestamp(last_trade["timestamp"]/1000)
                l_dt_string = l_dt_object.strftime("%Y-%m-%d %H:%M:%S")
                time_diff = l_dt_object - f_dt_object
                # print(str(time_diff),time_diff.days)
                if time_diff.days > 1:
                    row = { "instrument_name":ins_name,
                            "number_of _trades":num_of_trades,
                            "start_time":f_dt_string,
                            "end_time":l_dt_string,
                            "days":time_diff.days}
                    res.append(row)
                    f.writerow(row.values())

        else:
            print(ins_name,"error")
        
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--instruments", action="store_true", help="select to update the new expired instrument list")
    args = parser.parse_args()

    tag = True
    if args.instruments:
        response = requests.get(ins_url + "?currency=BTC&expired=true")
        if response.status_code == 200:
            data = json.loads(response.content)["result"]
            df = pd.DataFrame(data)
            df_filtered = df.loc[df['kind'] == 'option']
            df_filtered = df_filtered.loc[df_filtered['expiration_timestamp'] < datetime.now().timestamp()*1000]
            df_filtered.to_csv("expired_btc.csv")
            print("BTC data loaded successfully.")
        else:
            tag = False
            print("Failed to load BTC data.")
        
        # response = requests.get(ins_url+"?currency=ETH")
        # if response.status_code == 200:
        #     data = json.loads(response.content)
        #     df = pd.DataFrame(data)
        #     instrument_name = df["instrument_name"]
        #     instrument_name.to_csv("expired_eth.csv")
        #     print("ETH data loaded successfully.")
        # else:
        #     tag = False
        #     print("Failed to load ETH data.")
    
    if tag:
        instrument_name = pd.read_csv("expired_btc.csv")
        
        with open("expired_btc_time_summary.csv", 'a') as f:
            writer = csv.writer(f)
            # writer.writerow(["instrument_name",
            #                 "number_of_trades",
            #                 "start_time",
            #                 "end_time",
            #                 "days"])
            time_data = run_analysis(instrument_name["instrument_name"],writer)
            df = pd.DataFrame(time_data)
        

        df.to_csv("new.csv")

        # instrument_name = pd.read_csv("expired_eth.csv")
        # time_data = run_analysis(instrument_name["instrument_name"])
        # df = pd.DataFrame(summary_data)
        # df.to_csv("time_eth_time_summary.csv")


# deribit-trading

install : `asyncio`, `websockets` and `pandas`

## Pull data

### discover instruments

Run `python pull_data.py -i` to retrieve all available trading instruments in `instruments.csv`.

use `--currency` option to choose currency, default is `"BTC"`

!!! different currentcy has different related products, e.g. `"USDC"` has no optionsonly perpetuals.

```
usage: pull_data.py [-h] [-i] [--currency CURRENCY]

optional arguments:
  -h, --help           show this help message and exit
  -i, --instruments    select to get list of avaliable instruments
  --currency CURRENCY  Choose counter currency: [BTC,ETH,USDC]
```



### get data

Run `python pull_data.py` to get data, data is store under `data/` folder.

Change the `pull_data.json` params to cunstomize the data collected

```json
{
    "instrument_name" : "BTC-PERPETUAL",
    "start_timestamp" : "2023-03-27 23:01:59",
    "end_timestamp" : "now",
    "resolution" : "5"
}
```

Find the `instrument_name` from `instruments.csv` or https://test.deribit.com/api_console/

Do not change the <u>format</u> of `start_timestamp`

`end_timestamp` can be change to fix time, `now` is just an option

Resolution is in minutes and has to be in: `["1","3","5","10","15","30","60","120","180","360","720","1D"]`, note that some data may not have `"1D"` available.



**If start time is earlier than earliest date, system will still work, it will retrieve the <u>maximum data possible</u>** 



> **some notes**
>
> !!! BTC-PERPETUAL goes back to as far as 2018-08-13
>
> !!! BTC-29SEP23-28000-C goes back to as far as 2023-01-25



### All options

run `run.py` in `all_option` folder to download all options historical data





833 - public/get_tradingview_chart_data

834 - public/get_instruments 
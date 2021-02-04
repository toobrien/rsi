from requests import get
from datetime import datetime, timedelta
from math import log
from pandas import DataFrame as df
from statistics import StatisticsError, mean, stdev

def dist(x_, i, j):
    try:
        returns = [
            log(x_[k]["close"] / x_[k - 1]["close"]) for k in range(i + 1, j + 1)
        ]
        if (len(returns) > 1):
            return (mean(returns), stdev(returns))
        else:
            return (0, 1)
    except (StatisticsError, ValueError, ZeroDivisionError):
        raise

def get_candles(security, start_days_ago, end_days_ago):
    now = datetime.now()

    querystring = (
                    f"https://api.tdameritrade.com/v1/marketdata/{security}/pricehistory"
                    "?apikey=NUNBJMU9XQMDAANFOT6G4MQA1I85EG7P"
                    "&periodType=month"
                    "&frequencyType=daily"
                    "&frequency=1"
                    f"&startDate={int((now - timedelta(days = start_days_ago)).timestamp() * 1000)}"
                    f"&endDate={int((now - timedelta(days = end_days_ago)).timestamp() * 1000)}"
                  )

    res = get(querystring)

    if res.status_code != 200:
        print(f"error: {res.status_code}")
        print(res.text)
        result = []
    else:
        result = res.json()["candles"]

    return result

def get_returns(candles, mark):
    precision = 8

    if mark == "close":
        # calculate close as daily return
        return [
            round(log(candles[i]["close"] / candles[i - 1]["close"]), precision)
            for i in range(1, len(candles))
        ]
    elif mark == "volume":
        return [
            round(log(candles[i]["volume"] / candles[i - 1]["volume"]), precision)
            for i in range(1, len(candles))
        ]
    else:
        # calculate open, low, and high relative to same day close
        return [
            round(log(candles[i][mark] / candles[i]["close"]), precision)
            for i in range(1, len(candles))
        ]

def to_dataframe(candles):
    if (isinstance(candles[0]["datetime"], int)):
        for candle in candles:
            candle["datetime"] = datetime.fromtimestamp(candle["datetime"] / 1000)
    else:
        for candle in candles:
            candle["datetime"] = datetime.fromtimestamp(datetime.timestamp(candle["datetime"]) / 1000)

    return df.from_records(candles, index = "datetime")

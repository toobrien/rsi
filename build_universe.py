from json import dumps
from utils import get_candles
from requests import get
import urllib.request as request
from contextlib import closing
from csv import reader

NASDAQ = "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt"
NYSE =  "https://ftp.nyse.com/NYSESymbolMapping/NYSESymbolMapping.txt"
START = 10000   # days ago
END = 0         # days ago
UNIVERSE = []

with request.urlopen(NASDAQ) as nq:
    nq_r = reader(nq.read().decode("utf-8").split('\n'), delimiter = "|")
    for record in nq_r:
        try:
            UNIVERSE.append(record[0])
        except IndexError:
            pass

UNIVERSE = UNIVERSE[1:-1]

print(len(UNIVERSE))

try:
    res = get(NYSE)
    if res.status_code == 200:
        records = res.text.split('\n')
        nyse_r = reader(records, delimiter = "|")
        for record in nyse_r:
            print(record)
            try:
                UNIVERSE.append(record[0])
            except IndexError:
                pass
except Exception as e:
    print(e)

print(len(UNIVERSE))

for security in UNIVERSE:
    try:
        print(security)
        candles = get_candles(security, START, END)
    except Exception as e:
        print(e)
    with open(f"./data/universe/{security}.json", "w") as fd:
        fd.write(dumps(candles))

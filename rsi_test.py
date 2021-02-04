from matplotlib import pyplot
from utils import get_candles, to_dataframe, dist
from rsi import rsi, RsiError
from math import log, exp, floor, sqrt
from statistics import mean, stdev, NormalDist, StatisticsError
from json import dumps, loads
from enum import Enum
from os import listdir
from os.path import isfile, join
from datetime import datetime
from sys import argv
from numpy import percentile

TESTS = [
    { "type": "short", "enter": 70, "exit": 50 },
    { "type": "short", "enter": 80, "exit": 50 },
    { "type": "short", "enter": 90, "exit": 50 },
    { "type": "long", "enter": 30, "exit": 50 },
    { "type": "long", "enter": 20, "exit": 50 },
    { "type": "long", "enter": 10, "exit": 50 }
]

RESULTS_PATH = "./data/results/results.json"
CONTROL_PATH = "./data/results/control_results.json"
SUMMARY_PATH = "./data/results/summary.json"
UNIVERSE_PATH = "./data/universe"

class state(Enum):
    A = 1
    B = 2

def normalize(a, b, c, s):
    try:
        return (a - b) / c
        #return (a - b) / (c * s)
    except ZeroDivisionError as e:
        raise e

def get_summary_ops(type):
    short = (
        lambda r: normalize(
            r["max_price"], r["open_price"], r["open_price"], r["stdev"]
        ),
        lambda r: normalize(
            r["open_price"], r["min_price"], r["open_price"], r["stdev"]
        ),
        lambda r: normalize(
            r["open_price"], r["close_price"], r["open_price"], r["stdev"]
        )
    )

    long = (
        lambda r: normalize(
            r["open_price"], r["min_price"], r["open_price"], r["stdev"]
        ),
        lambda r: normalize(
            r["max_price"], r["open_price"], r["open_price"], r["stdev"]
        ),
        lambda r: normalize(
            r["close_price"], r["open_price"], r["open_price"], r["stdev"]
        )
    )

    if type == "long":
        return long
    else:
        return short

def trim_outliers(x):
    #return x[:x.index(percentile(x, 99))]
    return x[floor(len(x) * 1/100):floor(len(x) * (99 / 100))]

def summarize(results):
    #print(dumps(results, indent = 2))
    precision = 3
    std = NormalDist()
    alpha = 0.01
    bad_records = 0
    summary = {
        "mae": [],
        "mfe": [],
        "pnl": [],
        "duration": []
    }

    operations = ["mae", "mfe", "pnl"]

    for record in results:
        fns = get_summary_ops(record["type"])

        for i in range(len(operations)):
            try:
                summary[operations[i]].append(fns[i](record))
            except (ZeroDivisionError, KeyError):
                bad_records += 1
                continue
            
            summary["duration"].append(
                record["end_index"] - record["start_index"]
            )

    #pyplot.hist(summary["mae"], bins = 100, range = (-10, 10))
    #pyplot.show()

    summary["mae"].sort()
    summary["mfe"].sort()
    summary["pnl"].sort()
    summary["duration"].sort()

    summary["mae"] = trim_outliers(summary["mae"])
    summary["mfe"] = trim_outliers(summary["mfe"])
    summary["pnl"] = trim_outliers(summary["pnl"])
    summary["duration"] = trim_outliers(summary["duration"])

    res = {
        "test": {
            "type": results[0]["type"],
            "enter": results[0]["enter"],
            "exit": results[0]["exit"],
            "samples": len(results)
        },
        "mae": {
            "mean": round(mean(summary["mae"]), precision),
            "stdev": round(stdev(summary["mae"]), precision)
        },
        "mfe": {
            "mean": round(mean(summary["mfe"]), precision),
            "stdev": round(stdev(summary["mfe"]), precision)
        },
        "mfe/mae": {
            "mean": round(
                        mean(summary["mfe"]) / mean(summary["mae"]), precision
                    )
        },
        "pnl": {
            "mean": round(mean(summary["pnl"]), precision),
            "stdev": round(stdev(summary["pnl"]), precision)
        },
        "duration": {
            "mean": round(mean(summary["duration"]), precision),
            "stdev": round(stdev(summary["duration"]), precision)
        },
        "excluded_records": bad_records
    }

    for statistic in [ "mae", "mfe", "pnl" ]:
        E = std.zscore(alpha / 2) * res[statistic]["stdev"] / sqrt(res["test"]["samples"])
        mu = res[statistic]["mean"]
        res[statistic][f"interval({alpha})"] = [ round(mu - E, 2 * precision), round(mu + E, 2 * precision) ]

    return res

def get_state_tests(type, enter, exit):
    tests = {}

    if (type == "short"):
        tests = {
            "enter": lambda i: i >= enter,
            "exit": lambda i: i <= exit
        }
    elif (type == "long"):
        tests = {
            "enter": lambda i: i != 0 and i <= enter,
            "exit": lambda i: i >= exit
        }

    return tests

def get_control(x_):
    seed = x_[0]["close"]
    generated = [
        { "datetime": r["datetime"], "close": r["close"] } for r in x_
    ]
    try:
        (mean_, stdev_) = dist(x_, 0, len(x_) - 1)
    except (StatisticsError, ValueError, ZeroDivisionError):
        mean_, stdev_ = (0, 1)
    
    dist_ = NormalDist(mean_, stdev_)
    samples = dist_.samples(len(x_))

    for i in range(1, len(samples)):
        seed *= round(exp(samples[i]), 2)
        generated[i]["close"] = seed

    control = rsi(generated)

    return (control, generated)
    


def test(security, x_, rsi_, type, enter, exit):
    experiment_state = state.A
    results = []
    bad_records = 0
    state_tests = get_state_tests(type, enter, exit)
    enter_test = state_tests["enter"]
    exit_test = state_tests["exit"]
    #try:
    #    mean, stdev = dist(x_, 0, len(x_) - 1)
    #except (TypeError, ValueError, ZeroDivisionError, StatisticsError) as e:
    #    return []

    for i in range(len(x_)):
        price = x_[i]["close"]
        if experiment_state == state.A:
            if enter_test(rsi_[i]):
                experiment_state = state.B
                results.append({
                    "start_index": i,
                    #"mean": mean,
                    #"stdev": stdev,
                    "stdev": 1,
                    "open_price": price,
                    "max_price": price,
                    "max_index": i,
                    "min_price": price,
                    "min_index": i,
                    "close_price": price,
                    "end_index": i,
                    "security": security,
                    "type": type,
                    "enter": enter,
                    "exit": exit
                })
        elif experiment_state == state.B:
            try:
                if exit_test(rsi_[i]):
                    experiment_state = state.A
                    results[-1]["close_price"] = price
                    results[-1]["end_index"] = i
                    #mean, stdev = dist(x_, results[-1]["start_index"], i)
                    #mean, stdev = dist(x_, 0, i)
                    #results[-1]["mean"] = mean
                    #results[-1]["stdev"] = stdev * sqrt(results[-1]["end_index"] - results[-1]["start_index"])  
                    if x_[i]["high"] > results[-1]["max_price"]:
                        results[-1]["max_price"] = x_[i]["high"]
                        results[-1]["max_index"] = i
                    elif x_[i]["low"] < results[-1]["min_price"]:
                        results[-1]["min_price"] = x_[i]["low"]
                        results[-1]["min_index"] = i
            except (TypeError, ValueError, ZeroDivisionError, StatisticsError):
                # record is invalid; remove and continue
                results = results[:-1]
                bad_records += 1
                continue

    if (bad_records != 0):
        print(f"records discarded ({security}):", bad_records)

    return results

def run_test():
    universe = [ 
        fn for fn in listdir(UNIVERSE_PATH)
        if isfile(join(UNIVERSE_PATH, fn)) 
    ]
    bad_records = 0
    results = []
    control_results = []

    start = datetime.now()

    for security in universe:
        with open(join(UNIVERSE_PATH, security)) as fd:
            try:
                security = security.split('.')[0]
                x_ = loads(fd.read())
                rsi_ = rsi(x_)
                control_, _ = get_control(x_)
                for t in TESTS: 
                    result = test(
                        security, x_, rsi_,
                        t["type"], t["enter"], t["exit"]
                    )
                    if len(result) == 0:
                        print(f"security excluded: {security}")
                        continue
                    else: 
                        results += result   
                        control_results += test(
                            security, x_, control_,
                            t["type"], t["enter"], t["exit"]
                        )
            except (RsiError, UnicodeDecodeError):
                bad_records += 1
                pass

    print("securities excluded:", bad_records)

    with open(RESULTS_PATH, "w") as fd:
        fd.write(dumps(results, indent = 2))
    with open(CONTROL_PATH, "w") as fd:
        fd.write(dumps(control_results, indent = 2))

    print("elapsed:", datetime.now() - start)

def run_summary():
    summaries = []
    
    for path in [ RESULTS_PATH, CONTROL_PATH ]:
        print(path)
        with open(path) as fd:
            results = loads(fd.read())
            for t in TESTS:
                test_set = []
                for r in results:
                    if r["enter"] == t["enter"]:
                        test_set.append(r)
                summaries.append(summarize(test_set))
    
    with open(SUMMARY_PATH, "w") as fd:
        fd.write(dumps(summaries, indent = 2))

if __name__ == "__main__":
    if (argv[1] == "test"):
        run_test()
    elif (argv[1] == "summarize"):
        run_summary()

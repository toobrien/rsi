from statistics import mean

class RsiError(Exception):
    pass

def init_rsi(x):
    if len(x) < 15:
        raise RsiError

    gains = []
    losses = []

    for i in range(1, 15):
        diff = x[i]["close"] - x[i - 1]["close"]

        if diff < 0:
            gains.append(0)
            losses.append(abs(diff))
        elif diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(0)

    avg_gain = mean(gains)
    avg_loss = mean(losses)

    try:
        rsi_ = 100 - (100 / (1 + avg_gain / avg_loss))
    except ZeroDivisionError:
        rsi_ = 100 - (100 / (1 + avg_gain / 0.001))

    return (
                rsi_,
                x[14]["datetime"],
                avg_gain,
                avg_loss
            )

def next_rsi(cur_candle, prev_candle, last_avg_gain, last_avg_loss):
    diff = cur_candle["close"] - prev_candle["close"]

    if diff < 0:
        this_avg_gain = (last_avg_gain * 13 + 0) / 14
        this_avg_loss = (last_avg_loss * 13 + abs(diff)) / 14
    elif diff > 0:
        this_avg_gain = (last_avg_gain * 13 + diff) / 14
        this_avg_loss = (last_avg_loss * 13 + 0) / 14
    else:
        this_avg_gain = last_avg_gain
        this_avg_loss = last_avg_loss

    try:
        rsi_ = 100 - (100 / (1 + this_avg_gain / this_avg_loss))
    except ZeroDivisionError:
        rsi_ = 100 - (100 / (1 + this_avg_gain / 0.01))

    return (
                rsi_,
                cur_candle["datetime"],
                this_avg_gain,
                this_avg_loss
            )

def rsi(x):
    try:
        rsi_, ts, avg_gain, avg_loss = init_rsi(x)
        res = [ 0 for i in range(14) ]
        res.append(int(rsi_))

        for i in range(15, len(x)):
            rsi_, ts, avg_gain, avg_loss = next_rsi(x[i], x[i - 1], avg_gain, avg_loss)
            #res.append({ "datetime": ts, "rsi": int(rsi_) })
            res.append(rsi_)

        return res
    except (TypeError, RsiError) as e:
        raise e

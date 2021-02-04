from rsi_test import get_control
from utils import to_dataframe, get_candles
from rsi import rsi
from mplfinance import plot, make_addplot
from datetime import datetime

def control_test():
    x = get_candles("NOG", 10000, 0)
    x_ = to_dataframe(x)
    rsi_ = rsi(x)
    control, generated = get_control(x)

    # NOG first three samples
    session = [0] * len(x)
    for i in range(14,68):
        session[i] = 50
    session[14] = 25
    session[60] = 75
    for i in range(250,312):
        session[i] = 50
    session[255] = 25
    session[301] = 75
    for i in range(373,404):
        session[i] = 50
    session[376] = 25
    session[398] = 75

    apds = [
        make_addplot(rsi_, panel = 1),
        make_addplot([70] * len(x), panel = 1),
        make_addplot([30] * len(x), panel = 1),
        make_addplot(session, panel = 2)
        #make_addplot([ r["close"] for r in generated ], panel = 2),
        #make_addplot(control, panel = 3),
        #make_addplot([70] * len(x), panel = 3),
        #make_addplot([30] * len(x), panel = 3)
    ]

    plot(x_, type = "candle", addplot = apds)

if __name__=="__main__":
    control_test()

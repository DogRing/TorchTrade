import pyupbit


interval_datas = pyupbit.get_ohlcv("KRW-BTC",interval = "minute3",count=4)
print(interval_datas)

interval_datas.to_csv("./datas/tests.csv")
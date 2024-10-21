import requests
import numpy as np
import pyupbit
import os

url=os.environ['MODEL_URL']
access_key=os.environ['ACCESS_KEY']
secret_key=os.environ['SECRET_KEY']
upbit=pyupbit.Upbit(access_key,secret_key)

def ttrade(x_data):
    data_bytes = x_data.tobytes()
    headers={"Content-Type":"application/octet-stream"}
    response=requests.post(url,data=data_bytes,headers=headers)
    result=np.array(response.json())
    print(f"last: {x_data[0,-3:,1]}")
    print(f"prob: {result[:3,0]}")

    # if buy: 
    #     print(upbit.buy_market_order(ticker, upbit.get_balance("KRW")*0.985))
    # elif sell:
    #     print(upbit.sell_market_order(ticker, upbit.get_balance(ticker)*0.985))
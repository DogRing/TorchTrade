import requests
import numpy as np
import pyupbit
import io

url=os.environ['MODEL_URL']
access_key=os.environ['ACCESS_KEY']
secret_key=os.environ['SECRET_KEY']
upbit=pyupbit.Upbit(access_key,secret_key)

def ttrade(x_data):
    data_bytes=io.BytesIO()
    np.save(data_bytes,x_data)
    data_bytes=data_bytes.getvalue()
    headers={"Content-Type":"application/octet-stream"}
    response=requests.post(url,data=data_bytes,headers=headers)
    print(response.json())
    print(f"prob: {}")
    if buy: 
        print(upbit.buy_market_order(ticker, upbit.get_balance("KRW")*0.985))
    elif sell:
        print(upbit.sell_market_order(ticker, upbit.get_balance(ticker)*0.985))
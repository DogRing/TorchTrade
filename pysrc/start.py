from datetime import datetime
import time
import upbit
import asyncio
data_path = './datas/'

# tickers = upbit.gettickers('KRW')
tickers = ['KRW-BTC','KRW-XRP','KRW-DOGE','KRW-TFUEL','KRW-ETH','KRW-ETC','KRW-SBD','KRW-STRK']

def start():
    while True:
        now = datetime.today()
        if int(now.minute)%3 == 0:
            break
        time.sleep(3)
    now = upbit.setting(data_path,tickers,now)
    return now
        
async def update_3(data_path,tickers,uptime):
    last_time = uptime.minute
    loop = asyncio.get_event_loop()
    while True:
        uptime = datetime.today()
        if int(uptime.minute%3)==0 and uptime.minute !=last_time:
            last_time = uptime.minute
            upbit.update_data(data_path,tickers,uptime)
        await asyncio.sleep(30)

async def tradeTorch():
    loop = asyncio.get_running_loop()
    end_time = loop.time() + 300.0
    while True:
        now = datetime.today()
        print(now)
        if (loop.time() + 1.0) >= end_time:
            break
        await asyncio.sleep(60)

async def main(now):
    update = asyncio.create_task(update_3(data_path,tickers,now))
    aitrade = asyncio.create_task(tradeTorch())
    await update
    await aitrade
    

now = start()

asyncio.run(main(now))
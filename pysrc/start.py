from datetime import datetime
import time
import upbit
import asyncio 
data_path = './datas/'

# tickers = upbit.gettickers('KRW')
tickers = ['KRW-BTC','KRW-XRP','KRW-DOGE','KRW-TFUEL','KRW-ETH','KRW-ETC','KRW-SBD','KRW-STRK']

def start():
    now = datetime.today()
    now = upbit.setting(data_path,tickers,now)
    # Learning before data
    return now
        
async def update_d(data_path,tickers,uptime):
    last_time = uptime
    loop = asyncio.get_event_loop()
    ticks = 12
    next =True
    while True:
        uptime = datetime.today()
        if uptime.day!=last_time.day:
            next=True
        if next==True and uptime.hour==9 and uptime.minute==5:
            upbit.update_day(data_path,tickers,uptime)
            next=False
        if int(uptime.minute%5)==1 and uptime.minute !=last_time.minute:
            last_time = uptime
            ticks = upbit.update_data(data_path,tickers,uptime,ticks)
            
        await asyncio.sleep(10)

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
    update = asyncio.create_task(update_d(data_path,tickers,now))
    aitrade = asyncio.create_task(tradeTorch())
    await update
    await aitrade
    

now = start()

asyncio.run(main(now))
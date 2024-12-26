from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock
import indicators
import pyupbit
import time
import os

zk_host=os.environ.get('ZOOKEEPER_HOST','zk-cs.zookeeper.svc:2181')
zk_node=os.environ.get('ZOOKEEPER_NODE','/ttrade/position')
zk_lock_node=os.environ.get('ZOOKEEPER_LOCK','/locks/position_lock')
access_key=os.environ['ACCESS_KEY']
secret_key=os.environ['SECRET_KEY']
upbit=pyupbit.Upbit(access_key,secret_key)

zk=KazooClient(hosts=zk_host)
zk.start()
lock=Lock(zk,zk_lock_node)

def ttrade(df,tick,idc,params):
    signal = getattr(indicators,idc)(df,params).iloc[-1] 
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(df.iloc[-1]['timestamp']))}] SIGNAL: {signal}")
    if signal == 1:
        if lock.acquire(blocking=False):
            try:
                value,stat = zk.get(zk_node)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(df.iloc[-1]['timestamp']))}] POSITION: {value.decode()}")
                if value.decode() == '-1':
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(df.iloc[-1]['timestamp']))}] SIGNAL: BUY")
                    print(upbit.buy_market_order(tick, upbit.get_balance("KRW")*0.985))
                    zk.set(zk_node,tick.encode())
            finally:
                lock.release()
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(df.iloc[-1]['timestamp']))}] LOCKED BUDGET")
    if signal == -1:
        if lock.acquire(blocking=False):
            try:
                value,stat = zk.get(zk_node)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(df.iloc[-1]['timestamp']))}] POSITION: {value.decode()}")
                if value.decode() == tick:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(df.iloc[-1]['timestamp']))}] SIGNAL: SELL")
                    print(upbit.sell_market_order(tick, upbit.get_balance(tick)*0.985))
                    zk.set(zk_node,b'-1')
            finally:
                lock.release()
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(df.iloc[-1]['timestamp']))}] LOCKED BUDGET")

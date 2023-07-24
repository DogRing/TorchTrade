from datetime import datetime
import websockets
import asyncio
import json

async def upbit_ws_client(q, ticker):
    uri = "wss://api.upbit.com/websocket/v1"

    async with websockets.connect(uri, ping_interval=1440) as websocket:
        subscribe_fmt = [
            {"ticket": "test"},
            {
                "type": "ticker",
                "codes": [ticker],
                "isOnlyRealtime":True
            },
            {"format": "SIMPLE"}
        ]
        subscribe_data = json.dumps(subscribe_fmt)
        await websocket.send(subscribe_data)

        while True:
            data = await websocket.recv()
            data = json.loads(data)
            data = (data['tp'], datetime.fromtimestamp(data['ttms']/1000.0), data['tv'])
            q.put(data)

async def main(q, ticker):
    await upbit_ws_client(q, ticker=ticker)

def update_data(q,ticker):
    asyncio.run(main(q, ticker))
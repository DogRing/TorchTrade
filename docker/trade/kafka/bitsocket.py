import websockets
import asyncio
import json

async def upbit_ws_client(q, ticker):
    uri="wss://api.upbit.com/websocket/v1"
    while True:
        try:
            async with websockets.connect(uri,ping_interval=1440) as websocket:
                subscribe_fmt=[
                    {"ticket": "test"},
                    {
                        "type": "ticker",
                        "codes": [ticker],
                        "isOnlyRealtime":True
                    },
                    {"format": "SIMPLE"}
                ]
                subscribe_data=json.dumps(subscribe_fmt)
                await websocket.send(subscribe_data)
                while True:
                    data=await websocket.recv()
                    data=json.loads(data)
                    data=(data['tp'],data['ttms']/1000.0,data['tv'])
                    q.put(data)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket connection closed: {e}. Retrying...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"An error occurred: {e}. Retrying...")
            await asyncio.sleep(5)
async def main(q,ticker):
    await upbit_ws_client(q,ticker=ticker)
def update_data(q,ticker):
    asyncio.run(main(q,ticker))
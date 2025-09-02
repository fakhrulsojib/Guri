import asyncio
import websockets
import json

async def test_websocket():
    uri = "wss://fakhrulsojib.mooo.com/api/v1/follow/3"
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connected successfully!")
            await websocket.send(json.dumps({"type": "ping"}))
            response = await websocket.recv()
            print(f"Received: {response}")
    except Exception as e:
        print(f"WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())

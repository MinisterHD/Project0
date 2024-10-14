import asyncio
import websockets
import json

async def chat():
    url = "ws://localhost:8000/ws/chat/testroom/"
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps({"message": "Hello, World!"}))
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")

asyncio.get_event_loop().run_until_complete(chat())
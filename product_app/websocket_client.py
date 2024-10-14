import asyncio
import websockets

async def listen():
    url = "ws://localhost:8000/ws/notifications/"
    try:
        async with websockets.connect(url) as websocket:
            # Send a test message
            await websocket.send("Hello, server!")
            print("Sent message: Hello, server!")

            while True:
                try:
                    message = await websocket.recv()
                    print(f"Received message: {message}")
                except websockets.ConnectionClosedError as e:
                    print(f"Connection closed with error: {e}")
                    break
    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")

asyncio.get_event_loop().run_until_complete(listen())
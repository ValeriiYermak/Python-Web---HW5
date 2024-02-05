import asyncio
import websockets


async def connect_to_server():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        print("Connected to the server")

        # Отримуємо та виводимо повідомлення від сервера
        while True:
            response = await websocket.recv()
            print(response)


asyncio.run(connect_to_server())

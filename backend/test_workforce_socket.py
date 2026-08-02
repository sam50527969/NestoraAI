import asyncio
import json

import websockets


async def main():
    uri = "ws://127.0.0.1:8000/realtime/workforce"

    async with websockets.connect(uri) as ws:
        print("✅ Connected")

        data = await ws.recv()

        print("\nSnapshot:")
        print(json.dumps(json.loads(data), indent=2))

        await ws.send("ping")

        response = await ws.recv()

        print("\nPing:")
        print(response)


asyncio.run(main())
import asyncio
import json
import os

import websockets


async def main() -> None:
    token = os.getenv(
        "NESTORA_ACCESS_TOKEN",
        "",
    ).strip()

    if not token:
        raise RuntimeError(
            "Set NESTORA_ACCESS_TOKEN "
            "before running this script."
        )

    uri = (
        "ws://127.0.0.1:8000"
        "/realtime/workforce"
    )

    async with websockets.connect(
        uri
    ) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "event":
                        "socket.authenticate",
                    "token": token,
                }
            )
        )

        authenticated = (
            await websocket.recv()
        )

        print()
        print("Authentication:")
        print(
            json.dumps(
                json.loads(
                    authenticated
                ),
                indent=2,
            )
        )

        snapshot = (
            await websocket.recv()
        )

        print()
        print("Snapshot:")
        print(
            json.dumps(
                json.loads(snapshot),
                indent=2,
            )
        )

        await websocket.send("ping")

        response = (
            await websocket.recv()
        )

        print()
        print("Ping:")
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
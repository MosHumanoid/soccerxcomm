import asyncio
import pathlib
import sys

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent.resolve()))

import src.moshumanoid.sdk as sdk

server = sdk.HttpServer(14514, [""])

async def main():
    await server.register_callback(callback)
    await server.start()
    await asyncio.sleep(60)
    await server.stop()

async def callback(token: str, msg: sdk.Message) -> None:
    print(f'{msg["id"]} from {token}')

    await server.send(sdk.Message(
        {
            "type": "",
            "bound_to": "client",
            "id": msg["id"],
        }
    ), token)

if __name__ == '__main__':
    asyncio.run(main())

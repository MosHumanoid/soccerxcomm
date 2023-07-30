import asyncio

import soccerxcomm as sdk

server = sdk.HttpServer(14514, ["example_client"])

async def main():
    await server.register_callback(callback)
    await server.start()
    await asyncio.sleep(60)
    await server.stop()

async def callback(token: str, msg: sdk.Message) -> None:
    print(f'{msg.to_dict()["id"]} from {token}')

    await server.send(sdk.Message(
        {
            "type": "",
            "bound_to": "client",
            "id": msg.to_dict()["id"],
        }
    ), token)

if __name__ == '__main__':
    asyncio.run(main())

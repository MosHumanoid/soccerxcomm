import asyncio
import datetime

import moshumanoid.sdk as sdk

ID = 1145141919810

async def main():
    client = sdk.HttpClient("localhost", 14514, "example_client")
    await client.register_callback(callback)
    await client.connect()

    start_time = datetime.datetime.now()

    while datetime.datetime.now() - start_time < datetime.timedelta(seconds=60):
        await asyncio.sleep(0.1)

        msg = sdk.Message(
            {
                "type": "",
                "bound_to": "server",
                "id": ID,
            }
        )

        await client.send(msg)

    await client.disconnect()

async def callback(msg: sdk.Message) -> None:
    id = msg.to_dict()['id']

    if id == ID:
        print('Matched!')
    
    else:
        print('Not matched.')

if __name__ == '__main__':
    asyncio.run(main())

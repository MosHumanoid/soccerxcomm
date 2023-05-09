import asyncio
import datetime

import moshumanoid.sdk as sdk

server = sdk.Server(14514, {
    "example_client": sdk.Server.ClientInfo(
        team="example_team", token="example_client")
})

async def main():
    await server.start()

    await server.set_stage(sdk.GameStageKind.READY)
    await server.set_start_time(datetime.datetime.now())
    await server.set_end_time(datetime.datetime.now() + datetime.timedelta(minutes=1))
    await server.set_score("example_team", 114.514)

    await asyncio.sleep(60)

    await server.stop()

if __name__ == '__main__':
    asyncio.run(main())

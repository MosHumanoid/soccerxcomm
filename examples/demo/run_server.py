import asyncio
import datetime

import numpy as np

import soccerxcomm as sdk

server = sdk.Server(14514, 14515, {
    "example_client": sdk.Server.ClientInfo(
        team="example_team", token="example_client")
})

async def main():
    await server.start()

    await server.set_stage(sdk.GameStageKind.READY)
    await server.set_start_time(datetime.datetime.now())
    await server.set_end_time(datetime.datetime.now() + datetime.timedelta(minutes=1))
    await server.set_score("example_team", 114.514)
    await server.set_simulation_rate(1.1)

    await asyncio.sleep(5)

    for i in range(6000):
        await asyncio.sleep(0.01)
        await server.push_captured_image("example_client", np.ones((3, 4), dtype=np.uint8))

    await server.stop()

if __name__ == '__main__':
    asyncio.run(main())
    print("done")

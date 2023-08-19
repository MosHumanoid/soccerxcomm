import asyncio
import datetime

import numpy as np

import soccerxcomm as sdk

server = sdk.Server(14514, 14515, [
    sdk.ClientInfo(
        team="example_team", token="example_client")
])

async def main():
    await server.start()

    await server.set_game_info(game_info=sdk.GameInfo(
        stage=sdk.GameStageKind.READY,
        start_time=datetime.datetime.now(),
        end_time=datetime.datetime.now() + datetime.timedelta(seconds=60),
        score={
            'example_team': 0,
            'another_team': 0
        },
        simulation_rate=1.0))

    await asyncio.sleep(5)

    for i in range(6000):
        await asyncio.sleep(0.01)
        await server.push_captured_image("example_client", np.ones((3, 4), dtype=np.uint8))

    await server.stop()

if __name__ == '__main__':
    asyncio.run(main())
    print("done")

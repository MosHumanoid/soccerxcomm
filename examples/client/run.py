import asyncio

import soccerxcomm as sdk

from datetime import datetime

async def main():
    client = sdk.Client("localhost", 14514, 14515, "example_client")

    await client.connect()

    await asyncio.sleep(5)

    stage = await client.get_stage()
    start_time = await client.get_start_time()
    end_time = await client.get_end_time()
    score = await client.get_score("example_team")

    print(f'stage: {stage}, start_time: {start_time}, end_time: {end_time}, score: {score}, simulation_rate: {await client.get_simulation_rate()}')

    captured_image = await client.get_capture_image()

    print(f'captured_image: {captured_image}')

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
    print("done")


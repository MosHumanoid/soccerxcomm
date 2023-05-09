import asyncio

import moshumanoid.sdk as sdk

async def main():
    client = sdk.Client("localhost", 14514, "example_client")

    await client.connect()

    await asyncio.sleep(1)

    stage = await client.get_stage()
    start_time = await client.get_start_time()
    end_time = await client.get_end_time()
    score = await client.get_score("example_team")

    print(f'stage: {stage}, start_time: {start_time}, end_time: {end_time}, score: {score}')

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())

import asyncio

import soccerxcomm as sdk

async def main():
    client = sdk.Client("localhost", 14514, 14515, "example_client")

    await client.connect()

    await asyncio.sleep(5)

    game_info = await client.get_game_info()

    if game_info is None:
        print("game_info is None")
        return

    stage = game_info.stage
    start_time = game_info.start_time
    end_time = game_info.end_time
    score = game_info.score.get('example_team', None)
    if score is not None:
        score = score.score
    simulation_rate = game_info.simulation_rate

    print(f'stage: {stage}, start_time: {start_time}, end_time: {end_time}, score: {score}, simulation_rate: {simulation_rate}')

    captured_image = await client.get_captured_image()

    print(f'captured_image:\n {captured_image}')

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
    print("done")


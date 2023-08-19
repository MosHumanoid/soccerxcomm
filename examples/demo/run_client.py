import asyncio

import soccerxcomm as sdk

async def main():
    client = sdk.Client("localhost", 14514, 14515, "another_client")

    await client.connect()

    for _ in range(10):
        await asyncio.sleep(5)

        game_info = await client.get_game_info()
        if game_info is not None:
            print("game_info:")
            print(vars(game_info))

        robot_status = await client.get_robot_status()
        if robot_status is not None:
            print("robot_status:")
            print(vars(robot_status))

        captured_image = await client.get_captured_image()
        if captured_image is not None:
            print("captured_image:")
            print(f'shape: {captured_image.shape} mean: {captured_image.mean()}')

        print()

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
    print("done")


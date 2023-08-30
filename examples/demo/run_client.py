import asyncio

import soccerxcomm as sdk

import random


async def topic_message_callback(data: bytes):
    print('Topic message:', data)


async def main():
    client = sdk.Client("localhost", 14514, 14515, "example_client")

    await client.register_topic_message_callback('topic/example', topic_message_callback)

    await client.connect()

    for _ in range(10):
        await asyncio.sleep(1)

        game_info = await client.get_game_info()
        if game_info is not None:
            print("Game information:", vars(game_info))

        robot_status = await client.get_robot_status()
        if robot_status is not None:
            print("Robot status:", vars(robot_status))

        captured_image = await client.get_captured_image()
        if captured_image is not None:
            print("Captured image:", captured_image.shape, captured_image.mean())

        await client.push_robot_control(sdk.RobotControl(
            head=sdk.RobotControl.Head(
                head_angle=random.uniform(-90.0, 90.0),
                neck_angle=random.uniform(-90.0, 90.0)
            ),
            movement=sdk.RobotControl.Movement(
                x=random.uniform(-1.0, 1.0),
                y=random.uniform(-1.0, 1.0),
                omega_z=random.uniform(-1.0, 1.0)
            ),
            kick=sdk.RobotControl.Kick(
                x=random.uniform(-1.0, 1.0),
                y=random.uniform(-1.0, 1.0),
                z=random.uniform(-1.0, 1.0),
                speed=random.uniform(0.0, 1.0),
                delay=random.uniform(0.0, 1.0)
            )
        ))

        await client.push_topic_message("topic/example", f"topic/client:{random.randint(0, 1000000)}".encode())

        resp = await client.call_service('service/example', f'service/request:{random.randint(0, 1000000)}'.encode(), timeout=1.0)
        if resp is not None:
            print(f'Service response: {resp}')
        else:
            print(f'Service timeout')

        print()

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())

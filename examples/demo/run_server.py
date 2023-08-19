import asyncio
import datetime
import random

import numpy as np

import soccerxcomm as sdk

server = sdk.Server(14514, 14515, {
    'example_client': 'example_team',
    'another_client': 'another_team'
})


async def main():
    await server.start()

    await server.set_game_info(game_info=sdk.GameInfo(
        stage=sdk.GameStageKind.READY,
        start_time=datetime.datetime.now(),
        end_time=datetime.datetime.now() + datetime.timedelta(seconds=60),
        score={
            'example_team': random.randint(0, 10),
            'another_team': random.randint(0, 10)
        },
        simulation_rate=1.3))

    for i in range(600):
        await asyncio.sleep(0.1)

        if i % 10 == 0:
            game_info = await server.get_game_info()
            game_info.score['example_team'] += random.randint(0, 10)
            game_info.score['another_team'] += random.randint(0, 10)
            game_info.simulation_rate = random.uniform(0.5, 2.0)

        if i % 1 == 0:
            await server.push_robot_status('example_client', sdk.RobotStatus(
                head_angle=random.uniform(-90.0, 90.0),
                neck_angle=random.uniform(-90.0, 90.0),
                acceleration=np.random.uniform(-10.0, 10.0, size=(3,)),
                angular_velocity=np.random.uniform(-10.0, 10.0, size=(3,)),
                attitude_angle=np.random.uniform(-90.0, 90.0, size=(3,)),
                team='example_team'
            ))

            await server.push_robot_status('another_client', sdk.RobotStatus(
                head_angle=random.uniform(-90.0, 90.0),
                neck_angle=random.uniform(-90.0, 90.0),
                acceleration=np.random.uniform(-10.0, 10.0, size=(3,)),
                angular_velocity=np.random.uniform(-10.0, 10.0, size=(3,)),
                attitude_angle=np.random.uniform(-90.0, 90.0, size=(3,)),
                team='another_team'
            ))

        if i % 1 == 0:
            await server.push_captured_image("example_client", np.random.randint(0, 256, size=(1920, 1080, 3), dtype=np.uint8))
            await server.push_captured_image("another_client", np.random.randint(0, 256, size=(1920, 1080, 3), dtype=np.uint8))

        if i % 10 == 0:
            rb_ctrl = await server.get_robot_control('example_client')
            if rb_ctrl.head is not None:
                print(vars(rb_ctrl.head))
            if rb_ctrl.movement is not None:
                print(vars(rb_ctrl.movement))
            if rb_ctrl.kick is not None:
                print(vars(rb_ctrl.kick))

            print()

    await server.stop()

if __name__ == '__main__':
    asyncio.run(main())

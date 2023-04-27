import asyncio
import pathlib
import sys

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.parent.resolve()))

import src.moshumanoid.sdk as sdk


async def main():
    client = sdk.HttpClient("http://localhost:14514", "")
    await asyncio.sleep(30)


if __name__ == '__main__':
    asyncio.run(main())

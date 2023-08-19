# Overview

SoccerXComm is a Python library for communication between SoccerX platform and the agents.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```shell
pip install soccerxcomm
```

## Usage

To run a simple server, you can use the following code:

```python
import asyncio
import datetime

import numpy as np

import soccerxcomm as sxc

async def main():
    server = sxc.Server(
        port_controller=14514,
        port_streaming=14515, 
        client_team_map={
            'example_client': 'example_team',
            'another_client': 'another_team'})

    await server.start()

    # Your code here

    await server.stop()

if __name__ == '__main__':
    asyncio.run(main())
```

To connect to the server above, you can use the following code:

```python
import asyncio

import soccerxcomm as sxc

async def main():
    client = sxc.Client(
        host="localhost",
        port_controller=14514,
        port_streaming=14515,
        token="example_client")

    await client.connect()

    # Your code here

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT License](https://choosealicense.com/licenses/mit/)

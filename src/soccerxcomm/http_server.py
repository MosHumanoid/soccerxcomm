import asyncio
import re
from typing import Any, Callable, Coroutine, Dict, List

from aiohttp import web

from soccerxcomm.message import Message

from .logger import Logger
from .network_server_interface import INetworkServer


class HttpServer(INetworkServer):
    """The HTTP server to communicate with the client."""

    _MESSAGE_QUEUE_MAX_SIZE = 10

    _logger = Logger("HttpServer")

    def __init__(self, port: int, token_list: List[str]):
        """Initializes a new instance of the HttpServer class.

        Args:
            port: The port of the server.
            token_list: The list of tokens that are allowed to connect to the server.
        """
        self._port: int = port

        self._callback_list: List[Callable[[
            str, Message], Coroutine[Any, Any, None]]] = []
        self._message_queue_dict: Dict[str, asyncio.Queue[Message]] = {
            token: asyncio.Queue(HttpServer._MESSAGE_QUEUE_MAX_SIZE) for token in token_list
        }

        # Initialize the HTTP server.
        self._app = web.Application()
        self._app.add_routes([
            web.get('/', self._on_get),
            web.post('/', self._on_post)
        ])
        self._runner = web.AppRunner(self._app)

    async def broadcast(self, msg: Message) -> None:
        """Broadcasts a message to all clients.

        Args:
            msg: The message to broadcast.
        """

        for token in self._message_queue_dict.keys():
            await self.send(msg, token)

    async def register_callback(self, callback: Callable[[str, Message], Coroutine[Any, Any, None]]) -> None:
        """Registers a callback function to be called when a message is received.

        Args:
            callback: The callback function to register. The arguments are the token of the client and the message.
        """

        self._callback_list.append(callback)

    async def send(self, msg: Message, token: str) -> None:
        """Sends a message to a client.

        Args:
            msg: The message to send.
            token: The token of the client to send the message to.
        """

        if token not in self._message_queue_dict:
            raise Exception("The token is not registered.")
        
        message_queue: asyncio.Queue[Message] = self._message_queue_dict[token]
        
        if message_queue.full():
            # Remove the oldest message.
            message_queue.get_nowait()
        
        await self._message_queue_dict[token].put(msg)

    async def start(self) -> None:
        """Starts the server."""

        await self._runner.setup()
        site = web.TCPSite(self._runner, port=self._port)
        await site.start()

    async def stop(self) -> None:
        """Stops the server."""
        
        await self._runner.cleanup()

    async def _on_get(self, request: web.Request) -> web.Response:
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header is None:
                return web.Response(status=401)

            match_result = re.search(r'Bearer (\w*)', auth_header)
            if match_result is None:
                return web.Response(status=401)

            token = match_result.group(1)

            if token not in self._message_queue_dict:
                return web.Response(status=403)

            if self._message_queue_dict[token].empty():
                return web.Response(status=204)

            msg: Message = await self._message_queue_dict[token].get()
            self._logger.debug(f"Sending message: {msg}")
            return web.Response(body=msg.to_bytes())

        except Exception as e:
            self._logger.error(
                f"Failed to handle GET from {request.remote}: {e}")
            return web.Response(status=400)

    async def _on_post(self, request: web.Request) -> web.Response:
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header is None:
                return web.Response(status=401)

            match_result = re.search(r'Bearer (\w*)', auth_header)
            if match_result is None:
                return web.Response(status=401)

            token = match_result.group(1)
            if token not in self._message_queue_dict:
                return web.Response(status=403)

            msg = Message(await request.read())
            self._logger.debug(f"Received message: {msg}")
            for callback in self._callback_list:
                await callback(token, msg)

            return web.Response(status=204)

        except Exception as e:
            self._logger.error(
                f"Failed to handle POST from {request.remote}: {e}")
            return web.Response(status=400)

import asyncio
import re
from typing import Any, Callable, Coroutine, Dict, List

from aiohttp import web

from moshumanoid.sdk.message import Message

from .logger import Logger
from .network_server import INetworkServer


class HttpServer(INetworkServer):
    """The HTTP server to communicate with the client."""

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
        self._message_queue_dict: Dict[str, asyncio.Queue] = {
            token: asyncio.Queue() for token in token_list
        }

        # Initialize the HTTP server.
        self._app = web.Application()
        self._app.add_routes([
            web.get('/', self._on_get),
            web.post('/', self._on_post)
        ])
        self._runner = web.AppRunner(self._app)

    async def broadcast(self, msg: Message) -> None:
        for token in self._message_queue_dict.keys():
            await self._message_queue_dict[token].put(msg)

    async def register_callback(self, callback: Callable[[str, Message], Coroutine[Any, Any, None]]) -> None:
        self._callback_list.append(callback)

    async def send(self, msg: Message, token: str) -> None:
        if token not in self._message_queue_dict:
            raise Exception("The token is not registered.")

        await self._message_queue_dict[token].put(msg)

    async def start(self) -> None:
        await self._runner.setup()
        site = web.TCPSite(self._runner, port=self._port)
        await site.start()

    async def stop(self) -> None:
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

            msg = await self._message_queue_dict[token].get()
            return web.json_response(msg.to_dict())

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

            msg = Message(await request.json())
            for callback in self._callback_list:
                await callback(token, msg)

            return web.Response(status=204)

        except Exception as e:
            self._logger.error(
                f"Failed to handle POST from {request.remote}: {e}")
            return web.Response(status=400)

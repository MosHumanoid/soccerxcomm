import asyncio
import re
import threading
from typing import Callable, Dict, List

from flask import Flask, Response, jsonify, request

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

        self._callback_list: List[Callable[[str, Message], None]] = []
        self._message_queue_dict: Dict[str, asyncio.Queue] = {
            token: asyncio.Queue() for token in token_list
        }

        # Initialize the Flask app.
        self._app = Flask(str(id(self)))

        self._app.add_url_rule("/", "get", self._on_get, methods=["GET"])
        self._app.add_url_rule("/", "post", self._on_post, methods=["POST"])

        # Start the server.
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    async def broadcast(self, msg: Message) -> None:
        for token in self._message_queue_dict.keys():
            await self._message_queue_dict[token].put(msg)

    async def register_callback(self, callback: Callable[[str, Message], None]) -> None:
        self._callback_list.append(callback)

    async def send(self, msg: Message, token: str) -> None:
        if token not in self._message_queue_dict:
            raise Exception("The token is not registered.")

        await self._message_queue_dict[token].put(msg)

    def _on_get(self) -> Response:
        token = None

        auth_header = str(request.headers.get('Authorization', type=str))
        if auth_header:
            match_result = re.search(r'Bearer (.*)', auth_header)
            if match_result:
                token = match_result.group(1)

        if token is None:
            return Response(status=401)
        
        if token not in self._message_queue_dict:
            return Response(status=403)

        try:
            msg = self._message_queue_dict[token].get_nowait()
            return jsonify(msg.to_dict())
        
        except asyncio.QueueEmpty:
            return Response(status=404)

    def _on_post(self) -> Response:
        token = None

        auth_header = str(request.headers.get('Authorization', type=str))
        if auth_header:
            match_result = re.search(r'Bearer (.*)', auth_header)
            if match_result:
                token = match_result.group(1)

        if token is None:
            return Response(status=401)
        
        if token not in self._message_queue_dict:
            return Response(status=403)
        
        if not request.is_json:
            return Response(status=400)
        
        try:
            req_msg = Message(request.get_json())
            for callback in self._callback_list:
                callback(token, req_msg)

            return Response(status=200)
        
        except Exception as e:
            self._logger.error(str(e))
            return Response(status=500)

    def _run(self) -> None:
        self._app.run(port=self._port)

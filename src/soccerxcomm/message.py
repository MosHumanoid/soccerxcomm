from __future__ import annotations

from typing import Any, Dict

import bson
import jsonschema


class Message:
    """The message to communicate with servers."""

    _SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "type": {
                "type": "string"
            },
            "bound_to": {
                "type": "string",
                "enum": [
                    "client",
                    "server"
                ]
            }
        },
        "required": [
            "type",
            "bound_to"
        ]
    }

    def __init__(self, payload: Dict[str, Any] | bytes):
        """Initializes the message.

        Args:
            payload: The payload of the message.
        """

        self._payload: Dict[str, Any] = {}

        if isinstance(payload, bytes):
            self._payload = bson.decode(payload)
        elif isinstance(payload, dict):
            self._payload = payload
        else:
            raise TypeError("The payload must be a dictionary or bytes.")

        validator = jsonschema.Draft7Validator(Message._SCHEMA)
        if not validator.is_valid(self._payload):
            raise ValueError("The JSON is not valid.")

    def __str__(self) -> str:
        """Converts the message to a string.

        Returns:
            The string of the message.
        """

        return str(self._payload)

    def to_bytes(self) -> bytes:
        """Converts the message to BSON bytes.

        Returns:
            The BSON bytes of the message.
        """

        return bson.encode(self._payload)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the message to a dictionary.

        Returns:
            The dictionary of the message.
        """

        return self._payload

    def get_bound_to(self) -> str:
        """Gets the direction of the message.

        Returns:
            The direction of the message. "server" if the message is sent to the server, 
            "client" if the message is sent to the client.
        """

        return self._payload["bound_to"]

    def get_type(self) -> str:
        """Gets the type of the message.

        Returns:
            The type of the message.
        """

        return self._payload["type"]

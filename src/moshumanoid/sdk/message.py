import json
from typing import Any, Dict

import jsonschema


class Message:
    """The message to communicate with servers."""

    _JSON_SCHEMA = {
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

    def __init__(self, json_obj: Dict[str, Any]):
        """Initializes the message.

        Args:
            json_obj: The JSON object.
        """

        validator = jsonschema.Draft7Validator(Message._JSON_SCHEMA)
        if not validator.is_valid(json_obj):
            raise ValueError("The JSON is not valid.")

        self._json = json_obj

    def __getitem__(self, key: str) -> Any:
        """Gets the value of the specified key.

        Args:
            key: The key to get the value of.

        Returns:
            The value of the specified key.
        """

        return self._json[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets the value of the specified key.

        Args:
            key: The key to set the value of.
            value: The value to set.
        """

        self._json[key] = value

    def __str__(self) -> str:
        """Converts the message to a string.

        Returns:
            The string of the message.
        """

        return json.dumps(self._json)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the message to a dictionary.

        Returns:
            The dictionary of the message.
        """

        return self._json

    def get_bound_to(self) -> str:
        """Gets the direction of the message.

        Returns:
            The direction of the message. "server" if the message is sent to the server, 
            "client" if the message is sent to the client.
        """

        return self._json["bound_to"]

    def get_type(self) -> str:
        """Gets the type of the message.

        Returns:
            The type of the message.
        """

        return self._json["type"]

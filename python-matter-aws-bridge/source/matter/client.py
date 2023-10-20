import json
from os import getenv

import websocket


class Client:
    def __init__(self, on_initialized, on_message, on_event):
        self._on_initialized = on_initialized
        self._on_message = on_message
        self._on_event = on_event

        self._stored_messages = {}
        self._stored_message_id = 1

        websocket.enableTrace(True)

        self._client = websocket.WebSocketApp(
            "ws://{}:{}/ws".format(getenv("WS_HOST"), getenv("WS_PORT")),
            on_open=self.__on_open,
            on_close=self.__on_close,
            on_message=self.__on_message,
        )

    def __on_open(self, client):
        print("Connected to {}".format(self._client.url))

        self.send_message("start_listening")

    def __on_close(self, client, close_status_code, close_msg):
        self.connect()

    def __on_message(self, client, message):
        json_message = json.loads(message)

        message_id = json_message.get("message_id", None)

        if message_id is not None:
            result = json_message.get("result", [])

            self._on_message(message_id, result)

            callback, message, kargs = self._stored_messages.pop(
                message_id, (None, None, None)
            )

            if callback is not None:
                [
                    kargs.update({key: json_message.get(key, None)})
                    for key in ["error_code", "details"]
                ]

                callback(message, result, kargs)
        else:
            event = json_message.get("event", None)

            if event is not None:
                self._on_event(event, json_message.get("data", {}))
            else:
                [
                    setattr(self, key, json_message.get(key, None))
                    for key in ["compressed_fabric_id", "sdk_version"]
                ]

                self._on_initialized()

    def connect(self):
        print("Connecting to {}".format(self._client.url))

        self._client.run_forever(reconnect=3)

    def send_message(self, command, args=None, callback=None, **kargs):
        message_id = str(self._stored_message_id)

        message = {
            "message_id": command if callback is None else message_id,
            "command": command,
        }

        args is None or message.update({"args": args})

        if callback is not None:
            self._stored_messages.update({message_id: (callback, message, kargs)})

            self._stored_message_id += 1

        self._client.send(json.dumps(message))

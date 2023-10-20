from os import getenv

import websocket


class Connection:
    def __init__(self, on_open, on_message):
        self._on_message = on_message

        def on_close(client, close_status_code):
            self.__connect()

        self._client = websocket.WebSocketApp(
            "ws://{}:{}/ws".format(getenv("WS_HOST"), getenv("WS_PORT")),
            on_message=self._on_message,
            on_open=on_open,
            on_close=on_close,
        )

    def __connect(self):
        print("Connecting to {}".format(self._client.url))

        self._client.run_forever(reconnect=10)

    def connect(self):
        try:
            pass
        except Exception as error:
            print(error)

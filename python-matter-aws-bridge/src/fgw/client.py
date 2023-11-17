import json
import os
import re

import requests


class Client:
    def __init__(self, on_updated):
        self._on_updated = on_updated

    def update(self):
        response = requests.get(
            "http://{}:{}/ss-json/fgw.identity.check.json".format(
                os.getenv("FGW_HOST"), os.getenv("FGW_PORT")
            )
        )

        if response.ok:
            json_response = json.loads(response.text)

            [
                setattr(
                    self,
                    key,
                    "".join(
                        re.findall(
                            "[a-zA-Z0-9_.,@/:#-]*", json_response.get(value, None)
                        )
                    ),
                )
                for key, value in {
                    "model": "eqModel",
                    "version": "swVersion",
                    "serial_number": "serialNumber",
                    "mac_address": "mac",
                }.items()
            ]

            self._on_updated()

            return True

        return False

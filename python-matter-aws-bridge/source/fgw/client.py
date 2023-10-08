import json
import os

import requests

fgw_client_host = os.getenv("FGW_HOST")
fgw_client_port = os.getenv("FGW_PORT")


class Info:
    def __init__(self) -> None:
        response = requests.get(
            "http://{}:{}/ss-json/fgw.identity.check.json".format(
                fgw_client_host, fgw_client_port
            )
        )

        if response.ok:
            json_response = json.loads(response.text)

            [
                setattr(self, key, json_response.get(key, None))
                for key in ["eqModel", "swVersion", "serialNumber", "mac"]
            ]

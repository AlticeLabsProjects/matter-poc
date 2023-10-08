import json
from flask import Flask
import os.path
from getmac import get_mac_address


def get_serial_number():
    file_path = "/sys/firmware/devicetree/base/serial-number"

    if os.path.isfile(file_path):
        f = open(file_path, "r")

        try:
            return f.readline()
        finally:
            f.close()
    else:
        return "NOSERIAL"


app = Flask(__name__)


@app.route("/ss-json/fgw.identity.check.json", methods=["GET"])
def handle_request():
    return (
        json.dumps(
            {
                "eqModel": "GR141DG",
                "swVersion": "3GN8020700r1F",
                "serialNumber": get_serial_number(),
                "mac": get_mac_address(),
                "smartMeshSupport": "0",
                "smartMeshStatus": "0",
                "pad": None,
            }
        ),
        200,
    )

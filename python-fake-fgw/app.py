import json
from flask import Flask

app = Flask(__name__)


@app.route("/ss-json/fgw.identity.check.json", methods=["GET"])
def handle_request():
    return (
        json.dumps(
            {
                "eqModel": "GR141DG",
                "swVersion": "3GN8020700r1F",
                "serialNumber": "5054494EA8DC0C7F",
                "mac": "CC:19:A8:DC:0C:7F",
                "smartMeshSupport": "1",
                "smartMeshStatus": "1",
                "pad": None,
            }
        ),
        200,
    )

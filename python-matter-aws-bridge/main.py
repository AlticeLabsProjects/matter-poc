import websocket
import json
import source.aws.client as aws
import source.matter.normalizer as matter_normalizer
import requests
import hashlib

nodes = {}
message_id = 1
aws_client = None
aws_update_queue = []
fgw_info = None


def node_id_from_key(node_key):
    return next(iter([node_id for node_id in nodes if nodes[node_id] == node_key]))


def on_aws_updated(node_key, values):
    print(values)


def on_aws_getted(node_key, values):
    print(values)


def on_aws_deleted(node_key, values):
    global message_id

    node_id = node_id_from_key(node_key)

    send_websocker_message(
        "remove_node",
        str(message_id),
        args={"node_id": node_id},
    )

    message_id += 1


def on_aws_delta_updated(node_key, delta):
    try:
        node_id = node_id_from_key(node_key)

        allowed_attributes = dict(
            [
                attribute
                for attribute in delta.state.items()
                if matter_normalizer.allowed_attribute(attribute)
            ]
        )

        for attribute in allowed_attributes.items():
            global message_id

            send_websocker_message(
                "device_command",
                str(message_id),
                args=matter_normalizer.command_args_normalize(node_id, attribute),
            )

            message_id += 1

    except Exception as e:
        print(e)


def on_websocket_message(client, message):
    global fgw_info

    try:
        json_payload = json.loads(message)

        message_id = json_payload.get("message_id", None)

        if (
            message_id == "start_listening"
            or message_id == "get_nodes"
            or message_id == "get_node"
        ):
            json_nodes = json_payload.get("result", [])

            json_nodes = [json_nodes] if isinstance(json_nodes, dict) else json_nodes

            if isinstance(json_nodes, list):
                normalized_nodes = [
                    normalized_node
                    for normalized_node in [
                        matter_normalizer.node_normalize(json_node)
                        for json_node in json_nodes
                        if json_node is not None
                    ]
                    if normalized_node is not None
                ]

                for normalized_node in normalized_nodes:
                    node_key, node_id, attributes = normalized_node

                    nodes.setdefault(node_id, node_key)

                    aws_client.update_values(attributes, node_key)
        else:
            event = json_payload.get("event", None)

            if event == "attribute_updated":
                node_id, *attribute = json_payload["data"]

                node_key = nodes.get(node_id, None)

                if node_key is not None and matter_normalizer.allowed_attribute(
                    tuple(attribute)
                ):
                    aws_client.update_values(dict([attribute]), node_key)
            elif event == "node_added" or event == "node_updated":
                json_node = json_payload.get("data", {})

                normalized_node = matter_normalizer.node_normalize(json_node)

                if normalized_node is not None:
                    node_key, node_id, attributes = normalized_node

                    nodes.setdefault(node_id, node_key)

                    aws_client.update_values(attributes, node_key)

            else:
                (
                    controller_compressed_fabric_id,
                    controller_sdk_version,
                    controller_wifi_credentials_set,
                    controller_thread_credentials_set,
                ) = [
                    json_payload.get(key, None)
                    for key in [
                        "compressed_fabric_id",
                        "sdk_version",
                        "wifi_credentials_set",
                        "thread_credentials_set",
                    ]
                ]

                if controller_compressed_fabric_id is not None:
                    response = requests.get(
                        "http://127.0.0.1:5000/ss-json/fgw.identity.check.json"
                    )

                    if response.ok:
                        json_response = json.loads(response.text)

                        fgw_model, fgw_version, fgw_serial_number, fgw_mac = [
                            json_response.get(key, None)
                            for key in ["eqModel", "swVersion", "serialNumber", "mac"]
                        ]

                        fgw_info = {
                            "fgw_model": fgw_model,
                            "fgw_version": fgw_version,
                            "fgw_serial_number": fgw_serial_number,
                            "fgw_mac": fgw_mac,
                            "controller_compressed_fabric_id": controller_compressed_fabric_id,
                            "controller_sdk_version": controller_sdk_version,
                            "controller_wifi_credentials_set": controller_wifi_credentials_set,
                            "controller_thread_credentials_set": controller_thread_credentials_set,
                        }

                        aws_client_connect()
                    else:
                        exit()
                else:
                    print(json_payload)

    except Exception as err:
        pass


def on_websocket_open(client):
    send_websocker_message("start_listening")


def send_websocker_message(command, message_id=None, args=None):
    message = {
        "message_id": message_id or command,
        "command": command,
    }

    if args is not None:
        message.update({"args": args})

    json_message = json.dumps(message)

    print(json_message)

    websocket_client.send(json_message)


def aws_client_connect():
    global aws_client

    def connected():
        aws_client.update_values(fgw_info)

    client_id = "fiber_gateway_{}".format(
        hashlib.sha256(
            "{}{}{}".format(
                fgw_info["fgw_serial_number"],
                fgw_info["fgw_mac"],
                fgw_info["controller_compressed_fabric_id"],
            ).encode()
        ).hexdigest()
    )

    aws_client = aws.Client(
        endpoint="a2qzw5m91hzbht-ats.iot.eu-west-3.amazonaws.com",
        client_id=client_id,
        certificate_id="9cc3bb6c2f624ca25e4589083b30641863ab4be25ff3be1cc6da6670ea92d694",
        on_updated=on_aws_updated,
        on_getted=on_aws_getted,
        on_deleted=on_aws_deleted,
        on_delta_updated=on_aws_delta_updated,
    )

    aws_client.connect(connected)


websocket.enableTrace(True)

websocket_client = websocket.WebSocketApp(
    "ws://192.168.12.204:5580/ws",
    on_message=on_websocket_message,
    on_open=on_websocket_open,
)

websocket_client.run_forever(reconnect=10)

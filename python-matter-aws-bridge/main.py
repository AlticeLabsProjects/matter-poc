import websocket
import paho.mqtt.client as mqtt
import ssl
import json
import source.aws.client as aws

x = aws.Client(
    endpoint="a2qzw5m91hzbht-ats.iot.eu-west-3.amazonaws.com",
    client_id="1234",
    certificate_id="9cc3bb6c2f624ca25e4589083b30641863ab4be25ff3be1cc6da6670ea92d694",
)

def connected():
    print("connected")

x.connect(connected)

exit()

from chip.clusters.ClusterObjects import (
    ALL_ATTRIBUTES,
    ALL_CLUSTERS,
    Cluster,
)
from chip.clusters import Objects as clusters
from chip.clusters.ClusterObjects import ClusterCommand

broker_address = "ci.altice-home.cloud"
broker_port = 1883
topic = "/test"
username = "events-altice-dev:admin"
password = "admin"
message_id = 1

mqtt_client = mqtt.Client()


def on_mqtt_message(client, userdata, message):
    payload = message.payload.decode("utf-8")

    if payload:
        json_payload = json.loads(payload)

        if "command" in json_payload and json_payload["command"] == "device_command":
            websocket_client.send(payload)


def on_websocket_message(client, message):
    payload = message.payload.decode("utf-8")

    if payload:
        json_payload = json.loads(payload)

        if "event" in json_payload and json_payload["event"] == "attribute_updated":
            mqtt_client.publish(topic, message)


def on_websocket_open(client):
    start_listening()


def send_websocker_message(message):
    global message_id

    websocket_client.send(json.dumps({**{"message_id": str(message_id)}, **message}))

    message_id += 1


def start_listening():
    send_websocker_message({"command": "start_listening"})


def send_command(node_id, cluster_id, command_id):
    send_websocker_message({"command": "start_listening"})


def get_class_by_attribute_value(obj, attribute_name: str, attribute_value):
    return next(
        iter(
            [
                value
                for value in vars(obj).values()
                if getattr(value, attribute_name, None) == attribute_value
            ]
        ),
        None,
    )


def get_cluster_by_id(clusters, id: int):
    return get_class_by_attribute_value(clusters, "id", id)


def get_command_by_id(commands, id: int):
    return get_class_by_attribute_value(commands, "command_id", id)


cluster = get_cluster_by_id(clusters, 6)
command = get_command_by_id(cluster.Commands, 1)

cluster = getattr(clusters, "OnOff")
command_cls = getattr(cluster.Commands, "On")

mqtt_client.on_message = on_mqtt_message

mqtt_client.username_pw_set(username, password)

mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)

mqtt_client.connect(broker_address, port=broker_port, keepalive=True)

mqtt_client.subscribe(topic)

mqtt_client.loop_start()

websocket.enableTrace(True)

websocket_client = websocket.WebSocketApp(
    "ws://192.168.12.204:5580/ws",
    on_message=on_websocket_message,
    on_open=on_websocket_open,
)

websocket_client.run_forever(reconnect=True)

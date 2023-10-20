import hashlib

from dotenv import load_dotenv

import source.aws.client as aws
import source.fgw.client as fgw
import source.matter.client as matter
import source.matter.normalizer as matter_normalizer

load_dotenv()

nodes = {}


def node_id_from_shadow_name(shadow_name):
    return next(iter([node_id for node_id in nodes if nodes[node_id] == shadow_name]))


def fgw_updated():
    matter_client.connect()


def aws_on_connected():
    aws_client.update_values(
        {
            "fgwModel": fgw_client.model,
            "fgwVersion": fgw_client.version,
            "fgwSerialNumber": fgw_client.serial_number,
            "fgwMacAddress": fgw_client.mac_address,
            "controllerCompressedFabricId": matter_client.compressed_fabric_id,
            "controllerSdkVersion": matter_client.sdk_version,
        }
    )


def aws_on_command(payload):
    command = payload.get("command", None)

    def on_open_commissioning_window(message, result, kargs):
        pass

    def on_commission_with_code(message, result, kargs):
        pass

    def on_commission_on_network(message, result, kargs):
        pass

    def on_set_wifi_credentials(message, result, kargs):
        code = payload.get("code", None)

        code in None or matter_client.send_message(
            command, {"code": code}, callback=on_commission_with_code
        )

    if "open_commissioning_window" in command:
        node_id = payload.get("nodeId", None)

        node_id is None or matter_client.send_message(
            command, {"node_id": node_id}, callback=on_open_commissioning_window
        )
    if "commission_with_code" in command:
        ssid = payload.get("ssid", None)
        credentials = payload.get("credentials", None)

        ssid is None or credentials is None or matter_client.send_message(
            "set_wifi_credentials",
            {"ssid": ssid, "credentials": credentials},
            callback=on_set_wifi_credentials,
        )
    elif "commission_on_network" in command:
        setup_pin_code = payload.get("setupPinCode", None)

        setup_pin_code in None or matter_client.send_message(
            command,
            {"setup_pin_code": setup_pin_code},
            callback=on_commission_on_network,
        )


def aws_on_updated(shadow_name, values):
    try:
        node_id = node_id_from_shadow_name(shadow_name)

        allowed_attributes = dict(
            [
                attribute
                for attribute in (
                    (values.state.desired or {}).get("attributes", None) or {}
                ).items()
                if matter_normalizer.allowed_attribute(attribute)
            ]
        )

        for attribute in allowed_attributes.items():
            args = matter_normalizer.command_args_normalize(node_id, attribute)

            args is None or matter_client.send_message("device_command", args)

    except Exception as error:
        print(error)


def aws_on_deleted(shadow_name, values):
    node_id = node_id_from_shadow_name(shadow_name)

    matter_client.send_message("remove_node", {"node_id": node_id})


def matter_on_initialized():
    aws_client.connect(
        "fiber_gateway_{}".format(
            hashlib.sha256(
                "{}{}{}".format(
                    fgw_client.serial_number,
                    fgw_client.mac_address,
                    matter_client.compressed_fabric_id,
                ).encode()
            ).hexdigest()
        )
    )


def matter_on_message(message_id, result):
    if message_id in ["start_listening", "get_nodes", "get_node"]:
        normalized_nodes = [
            normalized_node
            for normalized_node in [
                matter_normalizer.node_normalize(node) for node in result
            ]
            if normalized_node is not None
        ]

        for normalized_node in normalized_nodes:
            (
                shadow_name,
                node_id,
                date_commissioned,
                available,
                attributes,
            ) = normalized_node

            try:
                nodes.setdefault(node_id, shadow_name)

                aws_client.update_values(
                    {
                        "commissionedDate": date_commissioned,
                        "available": available,
                        "attributes": attributes,
                    },
                    shadow_name,
                )
            except Exception as error:
                print(error)


def matter_on_event(event, data):
    if event == "attribute_updated":
        node_id, *attribute = data

        shadow_name = nodes.get(node_id, None)

        if shadow_name is not None and matter_normalizer.allowed_attribute(
            tuple(attribute)
        ):
            aws_client.update_values({"attributes": dict([attribute])}, shadow_name)
    elif event in ["node_added", "node_updated"]:
        normalized_node = matter_normalizer.node_normalize(data)

        if normalized_node is not None:
            (
                shadow_name,
                node_id,
                date_commissioned,
                available,
                attributes,
            ) = normalized_node

            nodes.setdefault(node_id, shadow_name)

            aws_client.update_values(
                {
                    "commissionedDate": date_commissioned,
                    "available": available,
                    "attributes": attributes,
                },
                shadow_name,
            )


matter_client = matter.Client(matter_on_initialized, matter_on_message, matter_on_event)

aws_client = aws.Client(
    aws_on_connected, aws_on_command, aws_on_updated, aws_on_deleted
)


fgw_client = fgw.Client(fgw_updated)

if not fgw_client.update():
    print("Cannot connect to the FiberGateway")

    exit(1)

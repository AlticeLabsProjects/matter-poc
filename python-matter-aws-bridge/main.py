import hashlib

from dotenv import load_dotenv

import source.aws.client as aws
import source.fgw.client as fgw
import source.matter.client as matter
import source.matter.normalizer as matter_normalizer

load_dotenv()


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
    uuid = payload.get("uuid", None)

    def check_commissioning_accepted(args):
        error_code = args.get("error_code")

        if error_code is None:
            return True

        aws_client.publish_command_rejected(
            uuid,
            {
                "errorCode": error_code,
                "errorMessage": args.get("error_message", None),
            },
        )

        return False

    def on_open_commissioning_window(message, result, args):
        if check_commissioning_accepted(args):
            code, *args = result

            aws_client.publish_command_accepted(
                uuid,
                {
                    "code": code,
                },
            )

    def on_commissioning(message, result, args):
        if check_commissioning_accepted(args):
            aws_client.publish_command_accepted(
                uuid,
            )

    def on_set_wifi_credentials(message, result, args):
        if check_commissioning_accepted(args):
            matter_client.send_message(
                command, {"code": args.get("code", None)}, on_commissioning
            )

    if "open_commissioning_window" in command:
        shadow_name = payload.get("shadowName", None)

        if shadow_name is not None:
            node_id = matter_normalizer.node_id_from_shadow_name(shadow_name)

            matter_client.send_message(
                command,
                {
                    "node_id": node_id,
                },
                on_open_commissioning_window,
            )

    if "commission_with_code" in command:
        code = payload.get("code", None)

        if code is not None:
            ssid = payload.get("ssid", None)
            credentials = payload.get("credentials", None)

            if ssid is None or credentials is None:
                matter_client.send_message(command, {"code": code}, on_commissioning)
            else:
                matter_client.send_message(
                    "set_wifi_credentials",
                    {
                        "ssid": ssid,
                        "credentials": credentials,
                    },
                    on_set_wifi_credentials,
                    code=code,
                )

    elif "commission_on_network" in command:
        setup_pin_code = payload.get("setupPinCode", None)

        setup_pin_code in None or matter_client.send_message(
            command,
            {
                "setup_pin_code": setup_pin_code,
            },
            on_commissioning,
        )


def aws_on_updated(shadow_name, values):
    try:
        if shadow_name is not None:
            node_id = matter_normalizer.node_id_from_shadow_name(shadow_name)

            allowed_attributes = dict(
                [
                    attribute
                    for attribute in (
                        (values.state.desired or {}).get("attributes", None) or {}
                    ).items()
                    if matter_normalizer.allowed_attribute(attribute)
                ]
            )

            for command in matter_normalizer.command_args_normalize(
                node_id, allowed_attributes
            ):
                matter_client.send_message("device_command", command)

    except Exception as error:
        print(error)


def aws_on_deleted(shadow_name, values):
    node_id = matter_normalizer.node_id_from_shadow_name(shadow_name)

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
                node_id,
                date_commissioned,
                available,
                attributes,
            ) = normalized_node

            try:
                aws_client.update_values(
                    {
                        "commissionedDate": date_commissioned,
                        "available": available,
                        "attributes": attributes,
                    },
                    matter_normalizer.shadow_name_from_node_id(node_id),
                )
            except Exception as error:
                print(error)


def matter_on_event(event, data):
    if event == "attribute_updated":
        node_id, *attribute = data

        if matter_normalizer.allowed_attribute(tuple(attribute)):
            aws_client.update_values(
                {"attributes": dict([attribute])},
                matter_normalizer.shadow_name_from_node_id(node_id),
            )
    elif event in ["node_added", "node_updated"]:
        normalized_node = matter_normalizer.node_normalize(data)

        if normalized_node is not None:
            (
                node_id,
                date_commissioned,
                available,
                attributes,
            ) = normalized_node

            if (event == "node_added") or available:
                aws_client.update_values(
                    {
                        "commissionedDate": date_commissioned,
                        "available": available,
                        "attributes": attributes,
                    },
                    matter_normalizer.shadow_name_from_node_id(node_id),
                )

    elif event == "node_removed":
        aws_client.remove_values(matter_normalizer.shadow_name_from_node_id(data))


matter_client = matter.Client(matter_on_initialized, matter_on_message, matter_on_event)

aws_client = aws.Client(
    aws_on_connected, aws_on_command, aws_on_updated, aws_on_deleted
)


fgw_client = fgw.Client(fgw_updated)

if not fgw_client.update():
    print("Cannot connect to the FiberGateway")

    exit(1)

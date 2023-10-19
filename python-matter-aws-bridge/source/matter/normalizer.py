import hashlib

from chip.clusters import Objects as clusters_objects


def _get_cluster_id(cluster):
    return getattr(cluster, "id", None)


def _get_attribute_id(attribute):
    return getattr(attribute, "attribute_id", None)


_cluster_info_id = 0

_cluster_descriptor_id = _get_cluster_id(clusters_objects.Descriptor)

_attribute_descriptor_vendor_id = _get_attribute_id(
    clusters_objects.BasicInformation.Attributes.VendorID
)
_attribute_descriptor_product_id = _get_attribute_id(
    clusters_objects.BasicInformation.Attributes.ProductID
)
_attribute_descriptor_serial_number_id = _get_attribute_id(
    clusters_objects.BasicInformation.Attributes.SerialNumber
)

_cluster_basic_information_id = _get_cluster_id(clusters_objects.BasicInformation)
_cluster_bridged_device_basic_information_id = _get_cluster_id(
    clusters_objects.BridgedDeviceBasicInformation
)
_cluster_on_off_id = _get_cluster_id(clusters_objects.OnOff)
_cluster_level_control_id = _get_cluster_id(clusters_objects.LevelControl)
_cluster_color_control_id = _get_cluster_id(clusters_objects.ColorControl)

_allowed_clusters = [
    (
        "*",
        _cluster_info_id,
        "*",
    ),
    (
        "*",
        _cluster_descriptor_id,
        _get_attribute_id(clusters_objects.Descriptor.Attributes.DeviceTypeList),
    ),
    (
        "*",
        _cluster_basic_information_id,
        _get_attribute_id(clusters_objects.BasicInformation.Attributes.VendorName),
    ),
    (
        "*",
        _cluster_basic_information_id,
        _attribute_descriptor_vendor_id,
    ),
    (
        "*",
        _cluster_basic_information_id,
        _get_attribute_id(clusters_objects.BasicInformation.Attributes.ProductName),
    ),
    (
        "*",
        _cluster_basic_information_id,
        _attribute_descriptor_product_id,
    ),
    (
        "*",
        _cluster_basic_information_id,
        _get_attribute_id(clusters_objects.BasicInformation.Attributes.NodeLabel),
    ),
    (
        "*",
        _cluster_basic_information_id,
        _get_attribute_id(
            clusters_objects.BasicInformation.Attributes.HardwareVersionString
        ),
    ),
    (
        "*",
        _cluster_basic_information_id,
        _get_attribute_id(
            clusters_objects.BasicInformation.Attributes.SoftwareVersionString
        ),
    ),
    (
        "*",
        _cluster_basic_information_id,
        _get_attribute_id(
            clusters_objects.BridgedDeviceBasicInformation.Attributes.NodeLabel
        ),
    ),
    (
        "*",
        _cluster_bridged_device_basic_information_id,
        _attribute_descriptor_serial_number_id,
    ),
    (
        "*",
        _cluster_on_off_id,
        _get_attribute_id(clusters_objects.OnOff.Attributes.OnOff),
    ),
    (
        "*",
        _cluster_level_control_id,
        _get_attribute_id(clusters_objects.LevelControl.Attributes.CurrentLevel),
    ),
    (
        "*",
        _cluster_level_control_id,
        _get_attribute_id(clusters_objects.LevelControl.Attributes.MinLevel),
    ),
    (
        "*",
        _cluster_level_control_id,
        _get_attribute_id(clusters_objects.LevelControl.Attributes.MaxLevel),
    ),
    (
        "*",
        _cluster_color_control_id,
        _get_attribute_id(clusters_objects.ColorControl.Attributes.CurrentHue),
    ),
    (
        "*",
        _cluster_color_control_id,
        _get_attribute_id(clusters_objects.ColorControl.Attributes.CurrentSaturation),
    ),
    (
        "*",
        _cluster_color_control_id,
        _get_attribute_id(
            clusters_objects.ColorControl.Attributes.ColorTemperatureMireds
        ),
    ),
    (
        "*",
        _cluster_color_control_id,
        _get_attribute_id(clusters_objects.ColorControl.Attributes.ColorMode),
    ),
    (
        "*",
        _cluster_color_control_id,
        _get_attribute_id(
            clusters_objects.ColorControl.Attributes.ColorTempPhysicalMinMireds
        ),
    ),
    (
        "*",
        _cluster_color_control_id,
        _get_attribute_id(
            clusters_objects.ColorControl.Attributes.ColorTempPhysicalMaxMireds
        ),
    ),
]


def allowed_attribute(attribute):
    if not isinstance(attribute, tuple):
        return False

    key, _ = attribute

    endpoint_id, cluster_id, attribute_id = [int(value) for value in key.split("/")]

    return (
        (endpoint_id, cluster_id, attribute_id) in _allowed_clusters
        or ("*", cluster_id, attribute_id) in _allowed_clusters
        or (endpoint_id, cluster_id, "*") in _allowed_clusters
        or ("*", cluster_id, "*") in _allowed_clusters
    )


def node_normalize(node):
    node_id = node.get("node_id", None)
    date_commissioned = node.get("date_commissioned", None)
    available = node.get("available", None)
    attributes = node.get("attributes", {})

    if not (node_id and isinstance(attributes, dict)):
        return None

    vendor_id = attributes.get(
        "0/{}/{}".format(
            _cluster_basic_information_id, _attribute_descriptor_vendor_id
        ),
        None,
    )
    product_id = attributes.get(
        "0/{}/{}".format(
            _cluster_basic_information_id, _attribute_descriptor_product_id
        ),
        None,
    )
    serial_number = attributes.get(
        "0/{}/{}".format(
            _cluster_basic_information_id, _attribute_descriptor_serial_number_id
        ),
        None,
    )

    if vendor_id is None or product_id is None or serial_number is None:
        return None

    allowed_attributes = dict(
        [attribute for attribute in attributes.items() if allowed_attribute(attribute)]
    )

    return (
        hashlib.sha256(
            "{}{}{}{}".format(node_id, vendor_id, product_id, serial_number).encode()
        ).hexdigest(),
        node_id,
        date_commissioned,
        available,
        allowed_attributes,
    )


def command_args_normalize(node_id, attribute):
    key, value = attribute

    endpoint_id, cluster_id, attribute_id = [int(value) for value in key.split("/")]

    if cluster_id == _cluster_info_id:
        return None

    args = {
        "endpoint_id": int(endpoint_id),
        "node_id": node_id,
        "cluster_id": cluster_id,
    }

    def check_cluster_id(cluster):
        return cluster_id == _get_cluster_id(cluster)

    def check_attribute_id(attribute):
        return attribute_id == _get_attribute_id(attribute)

    def args_command(command, payload={}):
        return {"command_name": command.__name__, "payload": payload}

    if check_cluster_id(clusters_objects.OnOff):
        if check_attribute_id(clusters_objects.OnOff.Attributes.OnOff):
            args.update(
                args_command(
                    clusters_objects.OnOff.Commands.On
                    if value
                    else clusters_objects.OnOff.Commands.Off
                )
            )
    elif check_cluster_id(clusters_objects.LevelControl):
        if check_attribute_id(clusters_objects.LevelControl.Attributes.CurrentLevel):
            args.update(
                args_command(
                    clusters_objects.LevelControl.Commands.MoveToLevelWithOnOff,
                    {"level": value},
                )
            )
    elif check_cluster_id(clusters_objects.ColorControl):
        if check_attribute_id(clusters_objects.ColorControl.Attributes.CurrentHue):
            args.update(
                args_command(
                    clusters_objects.ColorControl.Commands.MoveToHue,
                    {"hue": value},
                )
            )
        elif check_attribute_id(
            clusters_objects.ColorControl.Attributes.CurrentSaturation
        ):
            args.update(
                args_command(
                    clusters_objects.ColorControl.Commands.MoveToSaturation,
                    {"saturation": value},
                )
            )
        elif check_attribute_id(
            clusters_objects.ColorControl.Attributes.ColorTemperatureMireds
        ):
            args.update(
                args_command(
                    clusters_objects.ColorControl.Commands.MoveToColorTemperature,
                    {"colorTemperatureMireds": value},
                )
            )

    return args

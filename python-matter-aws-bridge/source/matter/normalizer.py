from chip.clusters import Objects as clusters_objects


def _get_cluster_id(cluster):
    return getattr(cluster, "id", None)


def _get_attribute_id(attribute):
    return getattr(attribute, "attribute_id", None)


def node_id_from_shadow_name(shadow_name):
    return shadow_name.split("_")[1]


def shadow_name_from_node_id(node_id):
    return "node_{}".format(node_id)


_cluster_descriptor_id = _get_cluster_id(clusters_objects.Descriptor)
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
        _get_attribute_id(clusters_objects.BasicInformation.Attributes.VendorID),
    ),
    (
        "*",
        _cluster_basic_information_id,
        _get_attribute_id(clusters_objects.BasicInformation.Attributes.ProductName),
    ),
    (
        "*",
        _cluster_basic_information_id,
        _get_attribute_id(clusters_objects.BasicInformation.Attributes.ProductID),
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
        _get_attribute_id(clusters_objects.BasicInformation.Attributes.SerialNumber),
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

    allowed_attributes = dict(
        [attribute for attribute in attributes.items() if allowed_attribute(attribute)]
    )

    return (
        node_id,
        date_commissioned,
        available,
        allowed_attributes,
    )


def command_args_normalize(node_id, allowed_attributes):
    commands = []
    attributes = {}

    for key, value in allowed_attributes.items():
        endpoint_id, cluster_id, attribute_id = [int(value) for value in key.split("/")]

        ((attributes.setdefault(endpoint_id, {})).setdefault(cluster_id, {})).update(
            {attribute_id: value}
        )

    for endpoint_id, clusters in attributes.items():

        def add_command(cluster, command, payload={}):
            commands.append(
                {
                    "endpoint_id": endpoint_id,
                    "node_id": node_id,
                    "cluster_id": _get_cluster_id(cluster),
                    "command_name": command.__name__,
                    "payload": payload,
                }
            )

        on_off_cluster = clusters.get(_get_cluster_id(clusters_objects.OnOff), None)

        if on_off_cluster is not None:
            on_off_attribute = on_off_cluster.get(
                _get_attribute_id(clusters_objects.OnOff.Attributes.OnOff), None
            )

            if on_off_attribute is not None:
                add_command(
                    clusters_objects.OnOff,
                    clusters_objects.OnOff.Commands.On
                    if on_off_attribute
                    else clusters_objects.OnOff.Commands.Off,
                )

        level_control_cluster = clusters.get(
            _get_cluster_id(clusters_objects.LevelControl), None
        )

        if level_control_cluster is not None:
            current_level_attribute = level_control_cluster.get(
                _get_attribute_id(
                    clusters_objects.LevelControl.Attributes.CurrentLevel
                ),
                None,
            )

            if current_level_attribute is not None:
                add_command(
                    clusters_objects.LevelControl,
                    clusters_objects.LevelControl.Commands.MoveToLevelWithOnOff,
                    {"level": current_level_attribute},
                )

        color_control_cluster = clusters.get(
            _get_cluster_id(clusters_objects.ColorControl), None
        )

        if color_control_cluster is not None:
            current_hue_attribute = color_control_cluster.get(
                _get_attribute_id(clusters_objects.ColorControl.Attributes.CurrentHue),
                None,
            )

            current_saturation_attribute = color_control_cluster.get(
                _get_attribute_id(
                    clusters_objects.ColorControl.Attributes.CurrentSaturation
                ),
                None,
            )

            if (
                current_hue_attribute is not None
                and current_saturation_attribute is not None
            ):
                add_command(
                    clusters_objects.ColorControl,
                    clusters_objects.ColorControl.Commands.MoveToHueAndSaturation,
                    {
                        "hue": current_hue_attribute,
                        "saturation": current_saturation_attribute,
                    },
                )
            elif current_hue_attribute is not None:
                add_command(
                    clusters_objects.ColorControl,
                    clusters_objects.ColorControl.Commands.MoveToHue,
                    {"hue": current_hue_attribute},
                )
            elif current_saturation_attribute is not None:
                add_command(
                    clusters_objects.ColorControl,
                    clusters_objects.ColorControl.Commands.MoveToSaturation,
                    {"saturation": current_saturation_attribute},
                )
            else:
                color_temperature_mireds_attribute = color_control_cluster.get(
                    _get_attribute_id(
                        clusters_objects.ColorControl.Attributes.ColorTemperatureMireds
                    ),
                    None,
                )

                if color_temperature_mireds_attribute is not None:
                    add_command(
                        clusters_objects.ColorControl,
                        clusters_objects.ColorControl.Commands.MoveToColorTemperature,
                        {"colorTemperatureMireds": color_temperature_mireds_attribute},
                    )

    return commands

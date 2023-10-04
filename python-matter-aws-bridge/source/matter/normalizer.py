import hashlib
from chip.clusters import Objects as clusters_objects

_allowed_clusters = [
    ("0", "40", "1"),
    ("0", "40", "3"),
    ("0", "40", "8"),
    ("0", "40", "10"),
    ("0", "40", "11"),
    ("0", "40", "15"),
    ("0", "40", "18"),
    ("*", "6", "0"),
    ("*", "8", "0"),
    ("*", "768", "0"),
    ("*", "768", "1"),
]


def _cluster_from_id(cluster_id):
    return next(
        iter(
            [
                cluster
                for cluster in clusters_objects.__dict__.values()
                if getattr(cluster, "id", None) == cluster_id
            ]
        ),
        None,
    )


def _cluster_command_from_id(cluster, command_id):
    return (
        None
        if cluster is None
        else next(
            iter(
                [
                    command
                    for command in cluster.Commands.__dict__.values()
                    if getattr(command, "command_id", None) == command_id
                ]
            ),
            None,
        )
    )


def allowed_attribute(attribute):
    if not isinstance(attribute, tuple):
        return False

    key, _ = attribute

    endpoint_id, cluster_id, command_id = key.split("/")

    return (
        (endpoint_id, cluster_id, command_id) in _allowed_clusters
        or ("*", cluster_id, command_id) in _allowed_clusters
        or (endpoint_id, cluster_id, "*") in _allowed_clusters
        or ("*", cluster_id, "*") in _allowed_clusters
    )


def node_normalize(node):
    node_id = node.get("node_id", None)
    attributes = node.get("attributes", {})

    if not (node_id and isinstance(attributes, dict)):
        return None

    vendor_id = attributes.get("0/40/2", None)
    product_id = attributes.get("0/40/4", None)
    serial_number = attributes.get("0/40/18", None)

    if vendor_id is None or product_id is None or serial_number is None:
        return None

    allowed_attributes = dict(
        [attribute for attribute in attributes.items() if allowed_attribute(attribute)]
    )

    return (
        hashlib.sha256(
            "{}{}{}".format(vendor_id, product_id, serial_number).encode()
        ).hexdigest(),
        node_id,
        allowed_attributes,
    )


def command_args_normalize(node_id, attribute):
    data, value = attribute

    endpoint_id, cluster_id, command_id = data.split("/")

    cluster_id = int(cluster_id)

    cluster = _cluster_from_id(cluster_id)

    args = {
        "endpoint_id": int(endpoint_id),
        "node_id": node_id,
        "cluster_id": cluster_id,
    }

    def args_command(command, payload={}):
        return {"payload": payload, "command_name": command.__name__}

    if cluster == clusters_objects.OnOff:
        args.update(
            args_command(
                clusters_objects.OnOff.Commands.On
                if value
                else clusters_objects.OnOff.Commands.Off
            )
        )
    elif cluster == clusters_objects.LevelControl:
        args.update(
            args_command(
                clusters_objects.LevelControl.Commands.MoveToLevelWithOnOff,
                {"level": value, "transitionTime": 0},
            )
        )

    print(args)

    return args

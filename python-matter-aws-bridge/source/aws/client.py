from urllib import request
from awscrt import mqtt, http
from awsiot import iotshadow, mqtt_connection_builder, ModeledClass
from os import path, getcwd


class Client:
    def __init__(self, endpoint, client_id, certificate_id):
        self._client_id = client_id
        self._nodes = dict()

        certificate_path = path.join(getcwd(), "certificate")

        def certificate_filename(sufix):
            return path.join(certificate_path, "{}-{}".format(certificate_id, sufix))

        self._mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            cert_filepath=certificate_filename("certificate.pem.crt"),
            pri_key_filepath=certificate_filename("private.pem.key"),
            ca_filepath=path.join(certificate_path, "AmazonRootCA1.pem"),
            client_id="fiber_gateway_{}".format(client_id),
            clean_session=False,
            keep_alive_secs=30,
        )

    def connect(self, connected):
        self.connected_future = self._mqtt_connection.connect()

        self.connected_future.result()

        self._shadow = _Shadow(self)

        connected()

    def add_node(self, node_id, values):
        self._nodes[node_id] = _Shadow(self, node_id)

        self.update_values(values)

    def update_values(self, values):
        pass    


class _Shadow:
    def __init__(self, client, name=None):
        shadow_client = iotshadow.IotShadowClient(client._mqtt_connection)

        def subscribe(operation, accepted_callback, rejected_callback):
            def subscribe_future(operation, action, callback):
                shadow_client_subscribe_to = getattr(
                    shadow_client,
                    "subscribe_to_{}{}_shadow_{}".format(
                        operation, "" if name is None else "_named", action
                    ),
                )

                iotshadow_subscription_request = getattr(
                    iotshadow,
                    "{}{}ShadowSubscriptionRequest".format(
                        operation.capitalize(), "" if name is None else "Named"
                    ),
                )

                future, _ = shadow_client_subscribe_to(
                    request=iotshadow_subscription_request(
                        thing_name=client._client_id, shadow_name=name
                    ),
                    qos=mqtt.QoS.AT_LEAST_ONCE,
                    callback=callback,
                )

                return future

            subscribe_future(operation, "accepted", accepted_callback).result()
            subscribe_future(operation, "rejected", rejected_callback).result()

        subscribe("update", self._update_accepted, self._update_rejected)
        subscribe("get", self._get_accepted, self._get_rejected)
        subscribe("delete", self._delete_accepted, self._delete_rejected)

    def _update_accepted(self):
        pass

    def _update_rejected(self):
        pass

    def _get_accepted(self):
        pass

    def _get_rejected(self):
        pass

    def _delete_accepted(self):
        pass

    def _delete_rejected(self):
        pass

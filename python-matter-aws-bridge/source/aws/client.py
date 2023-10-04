from uuid import uuid4
from awscrt import mqtt
from awsiot import iotshadow, mqtt_connection_builder
from os import path, getcwd


class Client:
    def __init__(
        self,
        endpoint,
        client_id,
        certificate_id,
        on_updated,
        on_getted,
        on_deleted,
        on_delta_updated,
    ):
        self.client_id = client_id
        self._nodes = dict()
        self._on_updated = on_updated
        self._on_getted = on_getted
        self._on_deleted = on_deleted
        self._on_delta_updated = on_delta_updated

        certificate_path = path.join(getcwd(), "certificate")

        def certificate_filename(sufix):
            return path.join(certificate_path, "{}-{}".format(certificate_id, sufix))

        self._mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            cert_filepath=certificate_filename("certificate.pem.crt"),
            pri_key_filepath=certificate_filename("private.pem.key"),
            ca_filepath=path.join(certificate_path, "AmazonRootCA1.pem"),
            client_id=client_id,
            clean_session=False,
            keep_alive_secs=30,
        )

    def connect(self, connected):
        self.connected_future = self._mqtt_connection.connect()

        self.connected_future.result()

        self._shadow = _Shadow(self)

        connected()

    def update_values(self, values, name=None):
        shadow = (
            self._shadow
            if name is None
            else self._nodes.setdefault(name, _Shadow(self, name))
        )

        shadow.update_values(values)


class _Shadow:
    def __init__(self, client, name=None):
        self._name = name
        self._is_named = name is not None
        self._client = client
        self._shadow_client = iotshadow.IotShadowClient(client._mqtt_connection)

        def subscribe(operation, accepted_callback, rejected_callback):
            def subscribe_future(operation, action, callback):
                shadow_client_subscribe_to = getattr(
                    self._shadow_client,
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
                        thing_name=client.client_id, shadow_name=name
                    ),
                    qos=mqtt.QoS.AT_LEAST_ONCE,
                    callback=callback,
                )

                future.result()

            subscribe_future(operation, "accepted", accepted_callback)
            subscribe_future(operation, "rejected", rejected_callback)

        subscribe("update", self._on_update_accepted, self._on_update_rejected)
        subscribe("get", self._on_get_accepted, self._on_get_rejected)
        subscribe("delete", self._on_delete_accepted, self._on_delete_rejected)

        shadow_client_subscribe_to = getattr(
            self._shadow_client,
            "subscribe_to{}_shadow_delta_updated_events".format(
                "" if name is None else "_named"
            ),
        )

        iotshadow_subscription_request = getattr(
            iotshadow,
            "{}ShadowDeltaUpdatedSubscriptionRequest".format(
                "" if name is None else "Named"
            ),
        )

        future, _ = shadow_client_subscribe_to(
            request=iotshadow_subscription_request(
                thing_name=client.client_id, shadow_name=name
            ),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_delta_updated,
        )

        future.result()

    def _on_update_accepted(self, response):
        self._client._on_updated(self._name, response)

    def _on_update_rejected(self, error):
        print(error)

    def _on_get_accepted(self, response):
        self._client._on_getted(self._name, response)

    def _on_get_rejected(self, error):
        print(error)

    def _on_delete_accepted(self, response):
        self._client._on_deleted(self._name, response)

    def _on_delete_rejected(self, error):
        print(error)

    def _on_delta_updated(self, delta):
        self._client._on_delta_updated(self._name, delta)

    def update_values(self, values):
        token = str(uuid4())

        iotshadow_update_shadow_request = getattr(
            iotshadow, "Update{}ShadowRequest".format("Named" if self._is_named else "")
        )

        request = iotshadow_update_shadow_request(
            thing_name=self._client.client_id,
            shadow_name=self._name,
            state=iotshadow.ShadowState(desired=values, reported=values),
            client_token=token,
        )

        publish_update_shadow = getattr(
            self._shadow_client,
            "publish_update{}_shadow".format("_named" if self._is_named else ""),
        )

        future = publish_update_shadow(request, mqtt.QoS.AT_LEAST_ONCE)

        future.result()

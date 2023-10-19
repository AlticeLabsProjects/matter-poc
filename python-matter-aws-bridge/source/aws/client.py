import json
from uuid import uuid4

from awscrt import mqtt
from awsiot import iotshadow

from source.aws.connection import Connection


class Client(Connection):
    def __init__(
        self,
        thing_name,
        on_updated,
        on_getted,
        on_deleted,
        on_delta_updated,
    ):
        super().__init__(thing_name)

        self._nodes = dict()
        self._on_updated = on_updated
        self._on_getted = on_getted
        self._on_deleted = on_deleted
        self._on_delta_updated = on_delta_updated

    def connect(self, on_connected, on_command):
        try:
            self._mqtt_connection = super().connect()

            self._command_topic = "matter/things/{}/command".format(self.thing_name)

            def on_message_received(topic, payload, **kwargs):
                on_command(json.loads(payload))

            future, _ = self._mqtt_connection.subscribe(
                topic=self._command_topic,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=on_message_received,
            )

            future.result()

            self._shadow = _Shadow(self)

            on_connected()
        except Exception as error:
            print(error)

    def publish_command(self, payload):
        self._mqtt_connection.publish(
            topic=self._command_topic,
            payload=json.dumps(payload),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

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
                        thing_name=client.thing_name, shadow_name=name
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
                thing_name=client.thing_name, shadow_name=name
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

    def _on_create_certificate_from_csr_accepted(self, response):
        print(response)

    def _on_create_certificate_from_csr_rejected(self, error):
        print(error)

    def _on_delta_updated(self, delta):
        self._client._on_delta_updated(self._name, delta)

    def update_values(self, values):
        token = str(uuid4())

        iotshadow_update_shadow_request = getattr(
            iotshadow, "Update{}ShadowRequest".format("Named" if self._is_named else "")
        )

        request = iotshadow_update_shadow_request(
            thing_name=self._client.thing_name,
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

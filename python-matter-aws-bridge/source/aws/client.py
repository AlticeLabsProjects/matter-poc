import json
from uuid import uuid4

from awscrt import mqtt
from awsiot import iotshadow

from source.aws.connection import Connection


class Client(Connection):
    def __init__(
        self,
        on_connected,
        on_command,
        on_updated,
        on_deleted,
    ):
        super().__init__()

        self._nodes = dict()
        self._on_connected = on_connected
        self._on_command = on_command
        self._on_updated = on_updated
        self._on_deleted = on_deleted

    def __publish_command(self, action, uuid, payload={}):
        self._mqtt_connection.publish(
            topic="{}/{}".format(
                self._command_topic,
                action,
            ),
            payload=json.dumps({"uuid": uuid, "payload": payload}),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def connect(self, thing_name):
        try:
            self._mqtt_connection = super().connect(thing_name)

            self._command_topic = "matter/things/{}/command".format(self.thing_name)

            def on_message_received(topic, payload, **kwargs):
                self._on_command(json.loads(payload))

            future, _ = self._mqtt_connection.subscribe(
                topic=self._command_topic,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=on_message_received,
            )

            future.result()

            self._shadow = _Shadow(self)

            self._on_connected()
        except Exception as error:
            print(error)

    def publish_command_accepted(self, uuid, payload={}):
        self.__publish_command("accepted", uuid, payload)

    def publish_command_rejected(self, uuid, payload={}):
        self.__publish_command("rejected", uuid, payload)

    def update_values(self, values, shadow_name=None):
        shadow = (
            self._shadow
            if shadow_name is None
            else self._nodes.get(shadow_name, None)
            or self._nodes.setdefault(shadow_name, _Shadow(self, shadow_name))
        )

        shadow.update_values(values)


class _Shadow:
    def __init__(self, client, shadow_name=None):
        self._shadow_name = shadow_name
        self._is_named = shadow_name is not None
        self._client = client
        self._shadow_client = iotshadow.IotShadowClient(client._mqtt_connection)

        def subscribe(operation, accepted_callback, rejected_callback):
            def subscribe_future(operation, action, callback):
                shadow_client_subscribe_to = getattr(
                    self._shadow_client,
                    "subscribe_to_{}{}_shadow_{}".format(
                        operation, "" if shadow_name is None else "_named", action
                    ),
                )

                iotshadow_subscription_request = getattr(
                    iotshadow,
                    "{}{}ShadowSubscriptionRequest".format(
                        operation.capitalize(), "" if shadow_name is None else "Named"
                    ),
                )

                future, _ = shadow_client_subscribe_to(
                    request=iotshadow_subscription_request(
                        thing_name=client.thing_name, shadow_name=shadow_name
                    ),
                    qos=mqtt.QoS.AT_LEAST_ONCE,
                    callback=callback,
                )

                future.result()

            subscribe_future(operation, "accepted", accepted_callback)
            subscribe_future(operation, "rejected", rejected_callback)

        subscribe("update", self._on_update_accepted, self._on_update_rejected)
        subscribe("delete", self._on_delete_accepted, self._on_delete_rejected)

    def _on_update_accepted(self, response):
        self._client._on_updated(self._shadow_name, response)

    def _on_update_rejected(self, error):
        print(error)

    def _on_delete_accepted(self, response):
        self._client._on_deleted(self._shadow_name, response)

    def _on_delete_rejected(self, error):
        print(error)

    def _on_create_certificate_from_csr_accepted(self, response):
        print(response)

    def _on_create_certificate_from_csr_rejected(self, error):
        print(error)

    def update_values(self, values):
        token = str(uuid4())

        iotshadow_update_shadow_request = getattr(
            iotshadow, "Update{}ShadowRequest".format("Named" if self._is_named else "")
        )

        request = iotshadow_update_shadow_request(
            thing_name=self._client.thing_name,
            shadow_name=self._shadow_name,
            state=iotshadow.ShadowState(reported=values),
            client_token=token,
        )

        publish_update_shadow = getattr(
            self._shadow_client,
            "publish_update{}_shadow".format("_named" if self._is_named else ""),
        )

        future = publish_update_shadow(request, mqtt.QoS.AT_LEAST_ONCE)

        future.result()

import json
from concurrent.futures import Future
from os import getenv
from uuid import uuid4

import requests
from awscrt import mqtt
from awsiot import iotidentity, mqtt_connection_builder

from .certificate import (
    export_certificate_signing_request_to_pem,
    export_private_key_to_pem,
    generate_certificate_signing_request,
    generate_private_key,
    load_certificate,
    save_certificate,
)


class Connection:
    def __init__(self):
        self._iot_endpoint = getenv("AWS_IOT_ENDPOINT")
        self._api_url = getenv("AWS_API_URL")
        self._template_name = getenv("AWS_TEMPLATE_NAME")
        self._mqtt_connection = None

    def __downloadClaim(self):
        print("AWS API CONNECTING TO {}".format(self._api_url))

        response = requests.get(self._api_url)

        if response.ok and "application/json" in response.headers.get(
            "content-type", None
        ):
            json_response = json.loads(response.text)

            return (
                json_response.get("certificate", None),
                json_response.get("private_key", None),
            )

        raise Exception("Cannot get claim certificate")

    def __connect(self, client_id, certificate_pem, private_key_pem):
        print("AWS CONNECTING TO {}".format(self._iot_endpoint))

        def on_connection_interrupted(connection, error, **kwargs):
            print("AWS CONNECTION INTERRUPTED:", error, kwargs)

        def on_connection_resumed(connection, return_code, session_present, **kwargs):
            print("AWS CONNECTION RESUMED:", return_code, session_present, kwargs)

        def on_connection_success(connection, callback_data):
            print("AWS CONNECTION SUCCESS:", callback_data)

        def on_connection_failure(connection, callback_data):
            print("AWS CONNECTION FAILURE:", callback_data)

        def on_connection_closed(connection, callback_data):
            print("AWS CONNECTION CLOSED:", callback_data)

            self._mqtt_connection = None

        mqtt_connection = mqtt_connection_builder.mtls_from_bytes(
            endpoint=self._iot_endpoint,
            cert_bytes=bytes(certificate_pem, "utf-8"),
            pri_key_bytes=bytes(private_key_pem, "utf-8"),
            client_id=client_id,
            clean_session=True,
            keep_alive_secs=30,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            on_connection_success=on_connection_success,
            on_connection_failure=on_connection_failure,
            on_connection_closed=on_connection_closed,
        )

        mqtt_connection.connect().result()

        return mqtt_connection

    def __create_certificate_from_csr(self, identity):
        accepted_future = Future()

        private_key = generate_private_key()

        def accepted(response):
            accepted_future.set_result(
                (
                    response.certificate_ownership_token,
                    response.certificate_pem,
                    export_private_key_to_pem(private_key),
                )
            )

        def rejected(response):
            raise Exception(response)

        certificate_signing_request_pem = export_certificate_signing_request_to_pem(
            generate_certificate_signing_request(private_key, self.thing_name)
        )

        request = iotidentity.CreateCertificateFromCsrRequest(
            certificate_signing_request=certificate_signing_request_pem
        )

        identity.subscribe_to_create_certificate_from_csr_accepted(
            request=request, qos=mqtt.QoS.AT_LEAST_ONCE, callback=accepted
        )

        identity.subscribe_to_create_certificate_from_csr_rejected(
            request=request, qos=mqtt.QoS.AT_LEAST_ONCE, callback=rejected
        )

        future = identity.publish_create_certificate_from_csr(
            request=request, qos=mqtt.QoS.AT_LEAST_ONCE
        )

        future.result()

        return accepted_future

    def __register_thing(self, identity, certificate_ownership_token):
        accepted_future = Future()

        def accepted(response):
            accepted_future.set_result(response)

        def rejected(response):
            raise Exception(response)

        request = iotidentity.RegisterThingRequest(
            certificate_ownership_token=certificate_ownership_token,
            template_name=self._template_name,
        )

        identity.subscribe_to_register_thing_accepted(
            request=request, qos=mqtt.QoS.AT_LEAST_ONCE, callback=accepted
        )

        identity.subscribe_to_register_thing_rejected(
            request=request, qos=mqtt.QoS.AT_LEAST_ONCE, callback=rejected
        )

        future = identity.publish_register_thing(
            request=request, qos=mqtt.QoS.AT_LEAST_ONCE
        )

        future.result()

        return accepted_future

    def __connectWithClaim(self):
        claim_certificate_pem, claim_private_key_pem = self.__downloadClaim()

        mqtt_connection = self.__connect(
            str(uuid4()), claim_certificate_pem, claim_private_key_pem
        )

        identity = iotidentity.IotIdentityClient(mqtt_connection)

        (
            certificate_ownership_token,
            certificate_pem,
            private_key_pem,
        ) = self.__create_certificate_from_csr(identity).result()

        self.__register_thing(identity, certificate_ownership_token).result()

        save_certificate(self.thing_name, certificate_pem, private_key_pem)

        return self.__connect(self.thing_name, certificate_pem, private_key_pem)

    def connect(self, thing_name):
        if self._mqtt_connection is not None:
            return self._mqtt_connection

        self.thing_name = thing_name

        try:
            certificate_pem, private_key_pem = load_certificate(self.thing_name)

            if certificate_pem is None or private_key_pem is None:
                return self.__connectWithClaim()

            try:
                self._mqtt_connection = self.__connect(
                    self.thing_name, certificate_pem, private_key_pem
                )

                return self._mqtt_connection
            except Exception as error:
                print(error)

                return self.__connectWithClaim()
        except Exception as error:
            print(error)

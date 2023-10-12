from os import path, getcwd, getenv
from awsiot import iotidentity, iotshadow, mqtt_connection_builder


certificate_path = path.join(getcwd(), "certificate")
certificate, private_key = None

endpoint = getenv("AWS_ENDPOINT")


def downloadCertificate(certificate, private_key):
    pass


def loadCertificate(certificate, private_key):
    certificate_filename, private_key_filename = [
        path.join(certificate_path, "onboard-{}".format(sufix))
        for sufix in ["certificate.pem.crt", "private.pem.key"]
    ]

    certificate, private_key = [
        open(filename, "r").read()
        for filename in [certificate_filename, private_key_filename]
        if path.isfile(filename)
    ]

    return certificate is not None and private_key is not None


def connect(client_id, certificate, private_key):
    mqtt_connection = mqtt_connection_builder.mtls_from_bytes(
        endpoint=endpoint,
        cert_bytes=bytes(certificate, "utf-8"),
        pri_key_bytes=bytes(private_key, "utf-8"),
        ca_filepath=path.join(certificate_path, "AmazonRootCA1.pem"),
        client_id=client_id,
        clean_session=False,
        keep_alive_secs=30,
    )


if not (
    loadCertificate(certificate, private_key)
    or downloadCertificate(certificate, private_key)
):
    raise Exception()


def certificate_filename(sufix):
    return path.join(certificate_path, "onboard-{}".format(sufix))


itentity = iotidentity.IotIdentityClient(self._mqtt_connection)

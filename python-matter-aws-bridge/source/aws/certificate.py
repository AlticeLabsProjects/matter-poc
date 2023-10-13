import json
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from os import path, getcwd

certificate_pem_store_key = "certificatePem"
private_key_pem_store_key = "privateKeyPem"

certificate_path = path.join(getcwd(), "certificate")


def generate_certificate_signing_request(key, thing_name):
    return (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "PT"),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Lisbon"),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, "Lisbon"),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Altice"),
                    x509.NameAttribute(NameOID.COMMON_NAME, thing_name),
                ]
            )
        )
        .sign(key, hashes.SHA256())
    )


def export_certificate_signing_request_to_pem(csr):
    return csr.public_bytes(serialization.Encoding.PEM).decode("utf-8")


def generate_private_key():
    return ec.generate_private_key(ec.SECP384R1(), default_backend())


def export_private_key_to_pem(key):
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


def _certificate_store_filename(thing_name):
    return path.join(certificate_path, thing_name) + ".json"


def load_certificate(thing_name):
    filename = _certificate_store_filename(thing_name)

    if path.isfile(filename):
        file_store = None

        try:
            file_store = open(filename, "r")

            json_store = json.load(file_store)

            return (
                json_store[certificate_pem_store_key],
                json_store[private_key_pem_store_key],
            )
        except Exception as e:
            print(e)
        finally:
            if file_store is not None:
                file_store.close()

    return (None, None)


def save_certificate(thing_name, certificate_pem, private_key_pem):
    filename = _certificate_store_filename(thing_name)

    file_store = None

    try:
        file_store = open(filename, "w")

        json.dump(
            {
                certificate_pem_store_key: certificate_pem,
                private_key_pem_store_key: private_key_pem,
            },
            file_store,
        )
    except Exception as e:
        print(e)
    finally:
        if file_store is not None:
            file_store.close()

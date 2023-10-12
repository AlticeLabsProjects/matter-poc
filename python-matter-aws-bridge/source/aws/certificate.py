from cryptography.hazmat.primitives.asymmetric import ec
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def generateCertificateSigningRequest(key, client_id):
    return (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "PT"),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Lisbon"),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, "Lisbon"),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Altice"),
                    x509.NameAttribute(NameOID.COMMON_NAME, client_id),
                ]
            )
        )
        .sign(key, hashes.SHA256())
    )


def exportCertificateSigningRequesttoPEM(csr):
    return csr.public_bytes(serialization.Encoding.PEM)


def generatePrivateKey():
    return ec.generate_private_key(ec.SECP384R1(), default_backend())


def exportPrivateKeytoPEM(key):
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

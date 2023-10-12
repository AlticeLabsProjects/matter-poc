from source.aws.certificate import (
    exportCertificateSigningRequesttoPEM,
    exportPrivateKeytoPEM,
    generateCertificateSigningRequest,
    generatePrivateKey,
)

try:
    key = generatePrivateKey()

    print(exportPrivateKeytoPEM(key))

    csr = generateCertificateSigningRequest(key, "test")

    print(exportCertificateSigningRequesttoPEM(csr))
except Exception as err:
    print(err)

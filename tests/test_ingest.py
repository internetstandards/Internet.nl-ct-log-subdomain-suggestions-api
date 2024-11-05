from ctlssa.suggestions.logic.ingest import add_domains, certstream_callback
from ctlssa.suggestions.models import Domain


def test_certstream_callback(db):
    """
    This is what this message looks like. The 'context' parameter is empty afaik.
    {
      "data": {
        "cert_index": 371670721,
        "cert_link": "https://ct.googleapis.com/logs/eu1/xenon2025h1/ct/v1/get-entries?start=371670721&end=371670721",
        "leaf_cert": {
          "all_domains": [
            "git.boatcontroller.nl"
          ],
          "extensions": {
            "authorityInfoAccess": "CA Issuers - URI:http://r10.i.lencr.org/\nOCSP - URI:http://r10.o.lencr.org\n",
            "authorityKeyIdentifier": "keyid:BB:BC:C3:47:A5:E4:BC:A9:C6:C3:A4:72:0C:10:8D:A2:35:E1:C8:E8\n",
            "basicConstraints": "CA:FALSE",
            "certificatePolicies": "Policy: 2.23.140.1.2.1",
            "ctlPoisonByte": true,
            "extendedKeyUsage": "TLS Web server authentication, TLS Web client authentication",
            "keyUsage": "Digital Signature, Key Encipherment",
            "subjectAltName": "DNS:git.boatcontroller.nl",
            "subjectKeyIdentifier": "3E:04:80:C0:66:F1:4F:25:73:EC:19:C2:D8:80:95:5C:62:49:E7:76"
          },
          "fingerprint": "2F:FC:20:BB:3C:D9:F1:01:9A:74:B6:B5:C3:56:03:33:94:DB:25:B0",
          "issuer": {
            "C": "US",
            "CN": "R10",
            "L": null,
            "O": "Let's Encrypt",
            "OU": null,
            "ST": null,
            "aggregated": "/C=US/CN=R10/O=Let's Encrypt",
            "emailAddress": null
          },
          "not_after": 1737978120,
          "not_before": 1730202121,
          "serial_number": "358AABBFD6E827CB38D239A526E8A2CE805",
          "signature_algorithm": "sha256, rsa",
          "subject": {
            "C": null,
            "CN": "git.boatcontroller.nl",
            "L": null,
            "O": null,
            "OU": null,
            "ST": null,
            "aggregated": "/CN=git.boatcontroller.nl",
            "emailAddress": null
          }
        },
        "seen": 1730205715.758093,
        "source": {
          "name": "Google 'Xenon2025h1' log",
          "url": "https://ct.googleapis.com/logs/eu1/xenon2025h1/"
        },
        "update_type": "PrecertLogEntry"
      },
      "message_type": "certificate_update"
    }

    There is also a 'heartbeat' message_type which we flagrantly ignore. Some stuff in the data below was truncated.
    :return:
    """
    data = {
        "data": {
            "cert_index": 228890197,
            "cert_link": "https://ct.googleapis.com/logs/us1/argon2025h1/ct/v1/get-entries?start=228890197&end=2288901",
            "leaf_cert": {
                "all_domains": ["webadminvps8.goodadvice-it.nl"],
                "extensions": {
                    "authorityInfoAccess": "CA Issuers - URI:http://r10.i.lencr.org/\nOCSP - URI:http://r10.o.lencr.o",
                    "authorityKeyIdentifier": "keyid:BB:BC:C3:47:A5:E4:BC:A9:C6:C3:A4:72:0C:10:8D:A2:35:E1:C8:E8\n",
                    "basicConstraints": "CA:FALSE",
                    "certificatePolicies": "Policy: 2.23.140.1.2.1",
                    "ctlSignedCertificateTimestamp": "...",
                    "extendedKeyUsage": "TLS Web server authentication, TLS Web client authentication",
                    "keyUsage": "Digital Signature, Key Encipherment",
                    "subjectAltName": "DNS:webadminvps8.goodadvice-it.nl",
                    "subjectKeyIdentifier": "9B:A8:88:4A:18:8F:F9:08:68:51:9E:08:9B:35:16:38:84:17:24:F2",
                },
                "fingerprint": "9F:5B:B2:6B:01:D1:CD:DA:64:3D:9B:B4:DD:39:C9:32:A1:E1:C7:CF",
                "issuer": {
                    "C": "US",
                    "CN": "R10",
                    "L": None,
                    "O": "Let's Encrypt",
                    "OU": None,
                    "ST": None,
                    "aggregated": "/C=US/CN=R10/O=Let's Encrypt",
                    "emailAddress": None,
                },
                "not_after": 1737978056,
                "not_before": 1730202057,
                "serial_number": "33CA8E8B209F4B5BB643EC8B7CD073BAFD4",
                "signature_algorithm": "sha256, rsa",
                "subject": {
                    "C": None,
                    "CN": "webadminvps8.goodadvice-it.nl",
                    "L": None,
                    "O": None,
                    "OU": None,
                    "ST": None,
                    "aggregated": "/CN=webadminvps8.goodadvice-it.nl",
                    "emailAddress": None,
                },
            },
            "seen": 1730205715.766654,
            "source": {
                "name": "Google 'Argon2025h1' log",
                "url": "https://ct.googleapis.com/logs/us1/argon2025h1/",
            },
            "update_type": "X509LogEntry",
        },
        "message_type": "certificate_update",
    }
    certstream_callback(data, None)
    assert Domain.objects.count() == 1

    # does nothing, but most importantly does not crash
    data = {"data": {}, "message_type": "heartbeat"}
    certstream_callback(data, None)


def test_add_domains(db, caplog):  # sourcery skip: extract-duplicate-method
    # start with an empty slate, skipping sourcery suggestions to deal with every skip-case one by one...
    assert Domain.objects.count() == 0

    # first some cases that will not be added:
    # top level domain, no domain is added as it is not valuable
    add_domains(["nu.nl"])

    # wildcard domain is not added as it is not valuable
    add_domains(["*.nu.nl"])

    # wildcard of subdomains are not added
    add_domains(["*.subdomain.nu.nl"])

    # domain is outside of the accepted (default) zone
    add_domains(["*.subdomain.nu.com"])
    assert Domain.objects.count() == 0

    # the deque prevents insertion of the same domain twice in an N-number of domains added period.
    add_domains(["test.nu.nl"])
    add_domains(["test.nu.nl"])
    add_domains(["test.nu.nl"])
    assert Domain.objects.count() == 1

    # multiple domains can be added in one setting, this will add only one.
    added = add_domains(["test.nu.nl", "test2.nu.nl", "nu.nl"])
    assert Domain.objects.count() == 2
    assert added == 1

    # test if logging works correctly, disabled due to flooding
    # assert "ingesting" in caplog.text

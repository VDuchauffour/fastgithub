from fastgithub.webhook.signature import SignatureVerificationSHA1, SignatureVerificationSHA256


def test_sha256_verification(
    signature_payload: bytes, signature_sha256: str, signature_secret: str
):
    signature_checker = SignatureVerificationSHA256(signature_secret)
    status = signature_checker._verify_signature(signature_payload, signature_sha256)
    assert status is True


def test_sha1_verification(signature_payload: bytes, signature_sha1: str, signature_secret: str):
    signature_checker = SignatureVerificationSHA1(signature_secret)
    status = signature_checker._verify_signature(signature_payload, signature_sha1)
    assert status is True

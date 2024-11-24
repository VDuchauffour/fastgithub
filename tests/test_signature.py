from fastgithub.webhook.signature import SignatureVerificationSHA1, SignatureVerificationSHA256


def test_sha256_verification(payload: bytes, signature_sha256: str, secret: str):
    signature_checker = SignatureVerificationSHA256(secret)
    status = signature_checker._verify_signature(payload, signature_sha256)
    assert status is True


def test_sha1_verification(payload: bytes, signature_sha1: str, secret: str):
    signature_checker = SignatureVerificationSHA1(secret)
    status = signature_checker._verify_signature(payload, signature_sha1)
    assert status is True

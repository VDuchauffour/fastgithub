import hashlib
import hmac
from abc import ABC

from fastapi import HTTPException, Request


class SignatureVerification(ABC):
    signature_header: str

    def __init__(self, secret: str) -> None:
        self._secret = secret

    @property
    def secret(self) -> str:
        return self._secret

    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify the GitHub webhook signature.

        Args:
            payload (bytes): The raw request payload.
            signature (str): The signature provided by GitHub in the header.

        Returns:
            bool: True if the signature is valid, otherwise False.
        """
        hash_alg, provided_signature = signature.split("=")
        computed_signature = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.new(hash_alg).name,
        ).hexdigest()

        return hmac.compare_digest(provided_signature, computed_signature)

    async def verify(self, request: Request):
        signature = request.headers.get(SignatureVerification.signature_header)
        if not signature:
            raise HTTPException(status_code=400, detail="Signature is missing")

        payload = await request.body()

        if not self._verify_signature(payload, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")


class SignatureVerificationSHA256(SignatureVerification):
    signature_header = "X-Hub-Signature-256"


class SignatureVerificationSHA1(SignatureVerification):
    signature_header = "X-Hub-Signature"

from typing import Any

import uvicorn
from fastapi import FastAPI

from fastgithub import GithubWebhookHandler, SignatureVerificationSHA256, webhook_router

signature_verification = SignatureVerificationSHA256(secret="mysecret")  # noqa: S106
webhook_handler = GithubWebhookHandler(signature_verification)


def hello(data: dict[str, Any]):
    print(f"Hello from: {data['repository']}")


def bye(data: dict[str, Any]):
    print(f"Goodbye from: {data['repository']}")


webhook_handler.listen("push", [hello, bye])

app = FastAPI()
router = webhook_router(handler=webhook_handler, path="/postreceive")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app)

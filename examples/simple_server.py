from typing import Any
from fastapi import FastAPI
import uvicorn
from fastgithub.endpoint.webhook_router import webhook_router
from fastgithub.handler import GithubWebhookHandler
from fastgithub.signature import SignatureVerificationSHA256

signature_verification = SignatureVerificationSHA256(secret="mysecret")
webhook_handler = GithubWebhookHandler(signature_verification)

def hello(data: dict[str, Any]):
    print(f"Hello from: {data["repository"]}")

def bye(data: dict[str, Any]):
    print(f"Goodbye from: {data["repository"]}")

webhook_handler.listen("push", [hello, bye])

app = FastAPI()
router = webhook_router(handler=webhook_handler, path="/postreceive")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app)

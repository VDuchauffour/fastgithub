import uvicorn
from fastapi import FastAPI

from fastgithub import GithubWebhookHandler, Recipe, SignatureVerificationSHA256, webhook_router
from fastgithub.types import Payload

signature_verification = SignatureVerificationSHA256(secret="mysecret")  # noqa: S106
webhook_handler = GithubWebhookHandler(signature_verification)


class Hello(Recipe):
    def execute(self, payload: Payload):
        print(f"Hello from: {payload['repository']}")


class Bye(Recipe):
    def execute(self, payload: Payload):
        print(f"Bye from: {payload['repository']}")


recipes = [Hello(), Bye()]
webhook_handler.listen("push", recipes)

app = FastAPI()
router = webhook_router(handler=webhook_handler, path="/postreceive")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app)

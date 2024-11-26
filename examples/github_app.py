import os

import uvicorn
from fastapi import FastAPI
from github import Auth, Github

from fastgithub import GithubWebhookHandler, SignatureVerificationSHA256, webhook_router
from fastgithub.recipes.github import AutoCreatePullRequest, LabelsFromCommits

signature_verification = SignatureVerificationSHA256(secret="mysecret")  # noqa: S106
webhook_handler = GithubWebhookHandler(signature_verification)

github = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))

webhook_handler.plan([AutoCreatePullRequest(github), LabelsFromCommits(github)])


app = FastAPI()
router = webhook_router(handler=webhook_handler, path="/postreceive")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app)

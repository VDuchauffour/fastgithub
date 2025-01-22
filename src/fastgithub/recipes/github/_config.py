from fastgithub.helpers.github import Label

BUG = Label(
    name="bug",
    description="Something isn't working",
    color="d73a4a",
)
CHORE = Label(
    name="chore",
    description="Regular maintenance",
    color="cccccc",
)
ENHANCEMENT = Label(
    name="enhancement",
    description="New feature or request",
    color="a2eeef",
)
DEPENDENCIES = Label(
    name="dependencies",
    description="Pull requests that update a dependency file",
    color="0366d6",
)
DOCUMENTATION = Label(
    name="documentation",
    description="Improvements or additions to documentation",
    color="0075ca",
)
NODRAFT = Label(
    name="nodraft",
    description="This PR is not a draft:",
    color="cccccc",
)
AUTO_MERGE = Label(
    name="automerge",
    description="Automatically merge this PR (and update it)",
    color="e5ee15",
)
AUTO_APPROVE = Label(
    name="autoapprove",
    description="Automatically approve this PR (to bypass branch protection rules)",
    color="e5ee15",
)
AUTO_RELEASE = Label(
    name="autorelease",
    description="Automatically create a release after all PRs with this label have been merged",
    color="ff66cc",
)

LABEL_CONFIG: dict[str, list[Label]] = {
    "#nodraft": [NODRAFT],
    "#fast": [NODRAFT, AUTO_MERGE, AUTO_APPROVE],
    "#release": [NODRAFT, AUTO_MERGE, AUTO_RELEASE],
    "#furious": [NODRAFT, AUTO_MERGE, AUTO_APPROVE, AUTO_RELEASE],
}

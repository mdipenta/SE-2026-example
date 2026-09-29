import os
from typing import Optional

import requests

# comment
def get_github_history(
    owner: str,
    repo: str,
    branch: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    token: Optional[str] = None,
    max_commits: Optional[int] = None,
) -> list[dict]:
    """
    Retrieve the commit history of a GitHub repository.

    Args:
        owner: Repository owner or organization.
        repo: Repository name.
        branch: Branch name, tag, or commit SHA. Uses the default branch if omitted.
        since: Include commits after this ISO 8601 timestamp.
               Example: "2026-01-01T00:00:00Z".
        until: Include commits before this ISO 8601 timestamp.
        token: GitHub personal access token. If omitted, reads GITHUB_TOKEN.
        max_commits: Maximum number of commits to return. None retrieves all.

    Returns:
        A list of dictionaries describing the commits.

    Raises:
        requests.HTTPError: If GitHub returns an error response.
    """
    token = token or os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    params = {"per_page": 100}

    if branch:
        params["sha"] = branch
    if since:
        params["since"] = since
    if until:
        params["until"] = until

    history = []

    while url:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        for item in response.json():
            commit = item["commit"]

            history.append({
                "sha": item["sha"],
                "author_name": commit["author"]["name"],
                "author_email": commit["author"]["email"],
                "author_login": (
                    item["author"]["login"]
                    if item.get("author")
                    else None
                ),
                "date": commit["author"]["date"],
                "message": commit["message"],
                "url": item["html_url"],
                "parents": [
                    parent["sha"] for parent in item["parents"]
                ],
            })

            if max_commits and len(history) >= max_commits:
                return history

        # GitHub provides the next page through the Link header.
        url = response.links.get("next", {}).get("url")
        params = None  # Parameters are already included in the next-page URL.

    return history

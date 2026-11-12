"""
Renews the Instagram access token (valid 60 days) and saves the new one
back into the IG_TOKEN secret. Runs twice a month on GitHub Actions.
"""

import os
import subprocess
import sys

import requests

token = os.environ.get("IG_TOKEN", "")
if not token:
    print("::error::The IG_TOKEN secret is missing.")
    sys.exit(1)

resp = requests.get(
    "https://graph.instagram.com/refresh_access_token",
    params={"grant_type": "ig_refresh_token", "access_token": token},
    timeout=60,
)
data = resp.json()
if resp.status_code != 200 or "access_token" not in data:
    print(f"::error::Token refresh failed: {data}")
    sys.exit(1)

new_token = data["access_token"]
print(f"::add-mask::{new_token}")
subprocess.run(
    ["gh", "secret", "set", "IG_TOKEN", "--repo", os.environ["GITHUB_REPOSITORY"]],
    input=new_token, text=True, check=True,
)
days = int(data.get("expires_in", 0)) // 86400
print(f"Token renewed. Valid for about {days} days.")

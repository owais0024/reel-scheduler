"""
Posts the next due reel from posts.csv to Instagram.

Runs on GitHub Actions once a day. For the earliest row whose date has
arrived (US Eastern time) and whose status is empty, it:
  1. downloads the video from the "queue" release,
  2. converts it to Instagram's reel format,
  3. puts it on a temporary public branch so Instagram can fetch it,
  4. creates and publishes the reel,
  5. marks the row as posted and cleans up.
"""

import csv
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

API = "https://graph.instagram.com/v27.0"
SCHEDULE = "posts.csv"
RELEASE_TAG = "queue"
MEDIA_BRANCH = "media"
TIMEZONE = "America/New_York"
WORK = "work"

TOKEN = os.environ.get("IG_TOKEN", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
GH_TOKEN = os.environ.get("GH_TOKEN", "")
DRY_RUN = os.environ.get("DRY_RUN", "").lower() == "true"


def fail(message):
    print(f"::error::{message}")
    sys.exit(1)


def run(cmd, cwd=None):
    shown = [c.replace(GH_TOKEN, "***") if GH_TOKEN else c for c in cmd]
    print("+", " ".join(shown))
    subprocess.run(cmd, check=True, cwd=cwd)


def api(method, path, **params):
    params["access_token"] = TOKEN
    resp = requests.request(method, f"{API}/{path}", params=params, timeout=120)
    try:
        data = resp.json()
    except ValueError:
        fail(f"Instagram returned a non-JSON reply on {path}: {resp.text[:300]}")
    if resp.status_code != 200 or "error" in data:
        fail(f"Instagram API error on {path}: {json.dumps(data)}")
    return data


def load_rows():
    with open(SCHEDULE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames
    for needed in ("date", "video", "caption", "status"):
        if needed not in (fields or []):
            fail(f"posts.csv is missing the '{needed}' column")
    return rows, fields


def save_rows(rows, fields):
    with open(SCHEDULE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def pick_due(rows):
    today = datetime.now(ZoneInfo(TIMEZONE)).date().isoformat()
    due = [
        r for r in rows
        if not (r.get("status") or "").strip() and (r.get("date") or "").strip()
        and r["date"].strip() <= today
    ]
    due.sort(key=lambda r: r["date"].strip())
    return (due[0] if due else None), today


def download_video(name):
    os.makedirs(WORK, exist_ok=True)
    run(["gh", "release", "download", RELEASE_TAG, "--repo", REPO,
         "--pattern", name, "--dir", WORK, "--clobber"])
    path = os.path.join(WORK, name)
    if not os.path.exists(path):
        fail(f"Video '{name}' was not found in the '{RELEASE_TAG}' release")
    return path


def convert(src, out_name):
    """Re-encode to 1080x1920, H.264/AAC, so Instagram accepts it and it stays under 100 MB."""
    out = os.path.join(WORK, out_name)
    run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", src,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
        "-c:v", "libx264", "-preset", "veryfast", "-profile:v", "high",
        "-b:v", "6M", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", out,
    ])
    size_mb = os.path.getsize(out) / 1_000_000
    print(f"Converted video: {size_mb:.1f} MB")
    if size_mb > 95:
        fail("Converted video is over 95 MB. Keep reels under about 2 minutes.")
    return out


def publish_to_media_branch(path):
    """Push only this file to a throwaway branch so Instagram can fetch it from a public URL."""
    tmp = os.path.join(WORK, "media-branch")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    shutil.copy(path, tmp)
    remote = f"https://x-access-token:{GH_TOKEN}@github.com/{REPO}.git"
    run(["git", "init", "-q", "-b", MEDIA_BRANCH], cwd=tmp)
    run(["git", "-c", "user.name=reel-bot", "-c", "user.email=reel-bot@users.noreply.github.com",
         "add", "."], cwd=tmp)
    run(["git", "-c", "user.name=reel-bot", "-c", "user.email=reel-bot@users.noreply.github.com",
         "commit", "-q", "-m", "Temporary media for posting"], cwd=tmp)
    run(["git", "push", "-q", "--force", remote, MEDIA_BRANCH], cwd=tmp)
    url = f"https://raw.githubusercontent.com/{REPO}/{MEDIA_BRANCH}/{os.path.basename(path)}"
    for _ in range(20):
        if requests.head(url, timeout=30).status_code == 200:
            print(f"Video is public at {url}")
            return url
        time.sleep(6)
    fail("The temporary video link never became reachable. Is the repository public?")


def delete_media_branch():
    remote = f"https://x-access-token:{GH_TOKEN}@github.com/{REPO}.git"
    try:
        run(["git", "push", "-q", remote, "--delete", MEDIA_BRANCH])
    except subprocess.CalledProcessError:
        print("Media branch was already gone.")


def wait_until_ready(container_id):
    for _ in range(40):  # about 13 minutes
        status = api("GET", container_id, fields="status_code,status").get("status_code")
        print(f"Container status: {status}")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            detail = api("GET", container_id, fields="status")
            fail(f"Instagram could not process the video: {json.dumps(detail)}")
        time.sleep(20)
    fail("Instagram took too long to process the video.")


def commit_schedule(message):
    run(["git", "config", "user.name", "reel-bot"])
    run(["git", "config", "user.email", "reel-bot@users.noreply.github.com"])
    run(["git", "add", SCHEDULE])
    run(["git", "commit", "-q", "-m", message])
    run(["git", "push", "-q"])


def main():
    if not TOKEN:
        fail("The IG_TOKEN secret is missing.")

    me = api("GET", "me", fields="user_id,username")
    ig_id = me.get("user_id") or me.get("id")
    print(f"Signed in as @{me.get('username')}")

    rows, fields = load_rows()
    row, today = pick_due(rows)
    if not row:
        print(f"Nothing due on {today} (US Eastern). Done.")
        return

    caption = row["caption"].strip()
    if len(caption) > 2200:
        fail(f"Caption for {row['video']} is {len(caption)} characters; the limit is 2200.")
    print(f"Due: {row['date']} -> {row['video']}")

    if DRY_RUN:
        out = subprocess.run(["gh", "release", "view", RELEASE_TAG, "--repo", REPO,
                              "--json", "assets", "-q", ".assets[].name"],
                             capture_output=True, text=True)
        names = out.stdout.split()
        if row["video"].strip() in names:
            print("Dry run OK: token works, the video is in the queue, and nothing was posted.")
        else:
            fail(f"Dry run: '{row['video']}' is not in the '{RELEASE_TAG}' release yet.")
        return

    src = download_video(row["video"].strip())
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    video = convert(src, f"reel-{stamp}.mp4")
    url = publish_to_media_branch(video)

    try:
        container = api("POST", f"{ig_id}/media", media_type="REELS",
                        video_url=url, caption=caption, share_to_feed="true")
        wait_until_ready(container["id"])
        published = api("POST", f"{ig_id}/media_publish", creation_id=container["id"])
    finally:
        delete_media_branch()

    media_id = published.get("id", "")
    posted_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"Published reel {media_id} at {posted_at}")

    row["status"] = f"posted {posted_at} id {media_id}"
    save_rows(rows, fields)
    commit_schedule(f"Posted {row['video']}")

    try:
        run(["gh", "release", "delete-asset", RELEASE_TAG, row["video"].strip(),
             "--repo", REPO, "--yes"])
    except subprocess.CalledProcessError:
        print("Could not remove the video from the queue; remove it by hand.")


if __name__ == "__main__":
    main()

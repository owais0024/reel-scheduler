"""
Posts the next due reel to Instagram.

The schedule lives in the Google Sheet "Reel Control Panel" (read through its
Apps Script web app, secret SHEET_URL). Without SHEET_URL it falls back to
posts.csv. Runs on GitHub Actions; posts at most one reel per day. For the
earliest due row that is not Posted or on Hold, it:
  1. downloads the video from the Drive folder or the "queue" release,
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

API = "https://graph.facebook.com/v25.0"
IG_USER_ID = os.environ.get("IG_USER_ID", "17841429764855705")
SCHEDULE = "posts.csv"
RELEASE_TAG = "queue"
MEDIA_BRANCH = "media"
TIMEZONE = "Asia/Karachi"
WORK = "work"

TOKEN = os.environ.get("IG_TOKEN", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
GH_TOKEN = os.environ.get("GH_TOKEN", "")
DRY_RUN = os.environ.get("DRY_RUN", "").lower() == "true"
SHEET_URL = os.environ.get("SHEET_URL", "").strip()


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


def load_sheet():
    resp = requests.get(SHEET_URL, timeout=120)
    try:
        data = resp.json()
    except ValueError:
        fail(f"The Google Sheet link did not return data: {resp.text[:300]}")
    if not data.get("ok", True) or "rows" not in data:
        fail(f"The Google Sheet refused the request ({data.get('error')}). Check the PIN in SHEET_URL.")
    return data["rows"], data.get("files", {})


def update_sheet(row, **fields):
    try:
        requests.post(SHEET_URL, data=json.dumps({"row": row["row"], **fields}),
                      headers={"Content-Type": "text/plain"}, timeout=120)
    except requests.RequestException as e:
        print(f"::warning::Could not update the sheet: {e}")


def today_str():
    return datetime.now(ZoneInfo(TIMEZONE)).date().isoformat()


def pick_due(rows):
    today = today_str()
    done = lambda r: (r.get("status") or "").strip().lower().startswith(("posted", "hold"))
    due = [
        r for r in rows
        if not done(r) and (r.get("date") or "").strip() and (r.get("video") or "").strip()
        and r["date"].strip() <= today
    ]
    due.sort(key=lambda r: r["date"].strip())
    return (due[0] if due else None), today


def posted_today(rows):
    today = today_str()
    for r in rows:
        if (r.get("status") or "").lower().startswith("posted") and \
                str(r.get("posted_at") or "").startswith(today):
            return True
    return False


def download_from_drive(name, file_id):
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    if os.path.getsize(path) < 10_000:
        fail(f"Could not download '{name}' from Google Drive.")
    return path


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

    ig_id = IG_USER_ID
    me = api("GET", ig_id, fields="username")
    print(f"Signed in as @{me.get('username')}")

    files = {}
    if SHEET_URL:
        rows, files = load_sheet()
        print(f"Read {len(rows)} rows from the Google Sheet.")
    else:
        rows, fields = load_rows()
        for r in rows:
            st = (r.get("status") or "").strip()
            r["posted_at"] = st[7:17] if st.lower().startswith("posted") else ""
    if posted_today(rows):
        print("A reel was already posted today. Done.")
        return
    row, today = pick_due(rows)
    if not row:
        print(f"Nothing due on {today} (Pakistan time). Done.")
        return

    name = row["video"].strip()
    caption = row["caption"].strip()
    if len(caption) > 2200:
        fail(f"Caption for {name} is {len(caption)} characters; the limit is 2200.")
    print(f"Due: {row['date']} -> {name}")

    queue = subprocess.run(["gh", "release", "view", RELEASE_TAG, "--repo", REPO,
                            "--json", "assets", "-q", ".assets[].name"],
                           capture_output=True, text=True).stdout.split()
    if name not in files and name not in queue:
        if SHEET_URL and not DRY_RUN:
            update_sheet(row, status="Video missing")
        fail(f"'{name}' is not in the Drive folder or the GitHub queue.")

    if DRY_RUN:
        print("Dry run OK: token works, the video was found, and nothing was posted.")
        return

    try:
        src = download_from_drive(name, files[name]) if name in files else download_video(name)
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
    except SystemExit:
        if SHEET_URL:
            update_sheet(row, status="Error: see GitHub Actions log")
        raise

    media_id = published.get("id", "")
    link = ""
    try:
        link = api("GET", media_id, fields="permalink").get("permalink", "")
    except SystemExit:
        pass
    posted_at = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d %H:%M")
    print(f"Published reel {media_id} at {posted_at} ({link})")

    if SHEET_URL:
        update_sheet(row, status="Posted", posted_at=posted_at, link=link)
    else:
        row["status"] = f"posted {posted_at} PKT id {media_id}"
        for r in rows:
            r.pop("posted_at", None)
        save_rows(rows, fields)
        commit_schedule(f"Posted {name}")

    if name in queue:
        try:
            run(["gh", "release", "delete-asset", RELEASE_TAG, name, "--repo", REPO, "--yes"])
        except subprocess.CalledProcessError:
            print("Could not remove the video from the queue; remove it by hand.")


if __name__ == "__main__":
    main()

# Reel Scheduler

Posts one reel a day to Instagram at about 7:23 pm US Eastern, using GitHub Actions and Instagram's official API.

- `post.py` posts the next due reel from `posts.csv`, using videos uploaded to the `queue` release.
- `refresh_token.py` renews the Instagram token twice a month.
- Secrets needed: `IG_TOKEN` (Instagram access token) and `GH_PAT` (fine-grained token with Secrets read/write on this repo).

Weekly: upload videos to the `queue` release and add rows to `posts.csv` (date in US Eastern, video file name, caption, empty status).

import json, subprocess, sys
from playwright.sync_api import sync_playwright
tim=json.load(open("timing.json")); fps=30
times=[float(x) for x in sys.argv[1].split(",")] if len(sys.argv)>1 else None
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("file://"+__import__("os").path.abspath("anim.html"))
    pg.evaluate("t=>init(t)",tim)
    if times:
        for t in times:
            pg.evaluate(f"render({t})"); pg.locator("#c").screenshot(path=f"test_{t}.jpg",type="jpeg",quality=80)
    else:
        n=int(tim["total"]*fps)
        ff=subprocess.Popen(["ffmpeg","-loglevel","error","-y","-f","image2pipe","-framerate",str(fps),"-c:v","mjpeg","-i","-","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p","frames.mp4"],stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"render({i/fps})")
            ff.stdin.write(pg.locator("#c").screenshot(type="jpeg",quality=92))
        ff.stdin.close(); ff.wait()
    b.close()

#!/usr/bin/env python3
"""Jaopao Music API — เฉพาะ API calls (Suno, SeedDream, FFmpeg, Upload, YouTube)
Agent สั่ง exec script นี้ด้วย JSON params"""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime

KIE_KEY = "26ecfa9d4abd06869689ca28062eb7a9"
ZERNIO_KEY = "sk_4224145db4a318d50ad22f087f57dcdf64890f11e08944e57aa2acb4119c85af"
YOUTUBE_ACCOUNT = "69b012a6dc8cab9432c8d81d"
BOT_TOKEN = "8376969560:AAH2rJtldj8fpLaByB20znOghQAPLgiHUPw"
OWNER_CHAT_ID = 5611560704
MUSIC_PROMPT = "Retro Thai Soul Pop, Lofi Funk, 80 BPM, F#m, Electric Piano Chorus FX, Soft Jazz Drums, Warm Bass, Clean Guitar, Saxophone, Vintage Synth Pad, Smooth Male Thai Vocal, Slow Rap"

YOUTUBE_FOOTER = """
━━━━━━━━━━━━━━━━━━━
Spotify ค้นได้เลยพิมว่า : เจ้าเปา ได้เลยนะจั๊บ

ฝากคุณพี่ทุกท่านติดตาม เจ้าเปา (JaoPao) ได้ที่ Tiktok

จิ้มเบาๆที่นี้นะคร้าฟ : https://www.tiktok.com/@jaopaodogsong
━━━━━━━━━━━━━━━━━━━"""


def log(msg):
    print(f"[API] {msg}", flush=True)


def send_telegram(text):
    try:
        payload = json.dumps({"chat_id": OWNER_CHAT_ID, "text": text}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
    except:
        pass


def kie_api(endpoint, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"https://api.kie.ai{endpoint}", data=data,
        headers={"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:
        errors = {402: "Credits หมด!", 429: "Rate limit!", 455: "Maintenance!", 501: "Generation failed!"}
        msg = errors.get(e.code, f"API error {e.code}")
        log(f"ERROR: {msg}")
        send_telegram(f"❌ Music API: {msg}")
        return {"error": msg}


def poll_suno(task_id):
    import time
    for i in range(40):
        time.sleep(15)
        req = urllib.request.Request(
            f"https://api.kie.ai/api/v1/generate/record-info?taskId={task_id}",
            headers={"Authorization": f"Bearer {KIE_KEY}"})
        data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        status = data.get("data", {}).get("status", "PENDING")
        log(f"Suno poll {i+1}: {status}")
        if status == "SUCCESS":
            songs = data.get("data", {}).get("response", {}).get("sunoData", [])
            best = min(songs, key=lambda s: abs(s.get("duration", 0) - 180)) if songs else {}
            log(f"Selected: {best.get('duration',0):.0f}s from {len(songs)} versions")
            return best.get("audioUrl", "")
        if status == "SENSITIVE_WORD_ERROR":
            send_telegram("⚠️ เนื้อเพลงโดนกรอง!")
            return ""
        if "FAILED" in status or "ERROR" in status:
            send_telegram(f"❌ Suno failed: {status}")
            return ""
    send_telegram("❌ Suno timeout!")
    return ""


def poll_image(task_id):
    import time
    for i in range(15):
        time.sleep(15)
        try:
            req = urllib.request.Request(
                f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                headers={"Authorization": f"Bearer {KIE_KEY}"})
            data = json.loads(urllib.request.urlopen(req, timeout=30).read())
        except:
            continue
        state = data.get("data", {}).get("state", "waiting")
        log(f"Image poll {i+1}: {state}")
        if state == "success":
            result = data.get("data", {}).get("resultJson", "")
            if result:
                r = json.loads(result) if isinstance(result, str) else result
                return r.get("resultUrls", [""])[0]
        if state == "failed":
            send_telegram("❌ Image failed!")
            return ""
    send_telegram("❌ Image timeout!")
    return ""


def main():
    # Read JSON params from stdin
    params = json.loads(sys.stdin.read())
    title = params["title"]
    title_en = params.get("title_en", "song").replace(" ", "-")
    lyrics = params["lyrics"]
    suno_style = params.get("suno_style", MUSIC_PROMPT)
    image_prompt = params["image_prompt"]
    seo_title = params.get("seo_title", f"{title} ({title_en}) JaoPao | Official Music Audio")
    seo_desc = params.get("seo_description", lyrics[:500])
    publish = params.get("publish", False)

    log(f"Starting API pipeline: {title}")

    # Check credits
    try:
        resp = urllib.request.urlopen(urllib.request.Request(
            "https://api.kie.ai/api/v1/chat/credit",
            headers={"Authorization": f"Bearer {KIE_KEY}"}), timeout=15)
        credits = json.loads(resp.read()).get("data", 0)
        log(f"Credits: {credits}")
        if credits < 100:
            print(json.dumps({"error": "Credits < 100", "credits": credits}))
            return
    except:
        pass

    # Parallel: Suno + SeedDream
    from concurrent.futures import ThreadPoolExecutor

    log("Launching Suno V5 + SeedDream parallel...")
    suno_resp = kie_api("/api/v1/generate", {
        "prompt": lyrics[:5000], "customMode": True, "instrumental": False,
        "model": "V5", "style": suno_style, "title": title[:80],
        "callBackUrl": "https://httpbin.org/post"})
    suno_task = suno_resp.get("data", {}).get("taskId", "")

    img_resp = kie_api("/api/v1/jobs/createTask", {
        "model": "seedream/5-lite-text-to-image", "task_type": "text-to-image",
        "input": {"prompt": image_prompt, "aspect_ratio": "16:9", "quality": "basic"}})
    img_task = img_resp.get("data", {}).get("taskId", "")

    with ThreadPoolExecutor(max_workers=2) as ex:
        f_music = ex.submit(poll_suno, suno_task) if suno_task else None
        f_image = ex.submit(poll_image, img_task) if img_task else None
        image_url = f_image.result() if f_image else ""
        music_url = f_music.result() if f_music else ""

    if not music_url or not image_url:
        print(json.dumps({"error": "Suno or Image failed", "music": bool(music_url), "image": bool(image_url)}))
        return

    # FFmpeg
    log("FFmpeg...")
    import tempfile, shutil
    work_dir = tempfile.mkdtemp(prefix="jaopao_")
    subprocess.run(["curl", "-sL", "--max-time", "180", "-o", f"{work_dir}/music.mp3", music_url], timeout=200)
    subprocess.run(["curl", "-sL", "--max-time", "180", "-o", f"{work_dir}/cover.jpg", image_url], timeout=200)
    subprocess.run(["ffmpeg", "-loop", "1", "-i", f"{work_dir}/cover.jpg", "-i", f"{work_dir}/music.mp3",
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-shortest", "-y", f"{work_dir}/output.mp4"], capture_output=True, timeout=300)

    if not os.path.exists(f"{work_dir}/output.mp4"):
        print(json.dumps({"error": "FFmpeg failed"}))
        shutil.rmtree(work_dir, ignore_errors=True)
        return

    size_mb = os.path.getsize(f"{work_dir}/output.mp4") / 1024 / 1024
    log(f"MP4: {size_mb:.1f} MB")

    # Upload
    log("Uploading...")
    upload = subprocess.run(["curl", "-s", "-X", "POST", "https://kieai.redpandaai.co/api/file-stream-upload",
        "-H", f"Authorization: Bearer {KIE_KEY}", "-F", f"file=@{work_dir}/output.mp4",
        "-F", "uploadPath=jaopao", "-F", f"fileName={title_en}-{datetime.now().strftime('%Y%m%d')}.mp4"],
        capture_output=True, timeout=300)
    try:
        video_url = json.loads(upload.stdout).get("data", {}).get("downloadUrl", "")
    except:
        video_url = ""

    shutil.rmtree(work_dir, ignore_errors=True)

    if not video_url:
        print(json.dumps({"error": "Upload failed"}))
        return

    # YouTube
    yt_url = ""
    if publish:
        log("Publishing YouTube...")
        yt_json = json.dumps({"content": (seo_desc + YOUTUBE_FOOTER)[:2000], "title": seo_title,
            "mediaUrls": [video_url], "platforms": [{"platform": "youtube", "accountId": YOUTUBE_ACCOUNT}]})
        try:
            yt_resp = json.loads(urllib.request.urlopen(urllib.request.Request(
                "https://zernio.com/api/v1/posts", data=yt_json.encode(),
                headers={"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}),
                timeout=60).read())
            yt_url = yt_resp.get("post", {}).get("_id", "")
            log(f"YouTube: {yt_resp.get('post',{}).get('status','?')}")
        except Exception as e:
            log(f"YouTube error: {e}")

    # Output result as JSON
    result = {
        "success": True,
        "title": title,
        "music_url": music_url,
        "image_url": image_url,
        "video_url": video_url,
        "youtube_id": yt_url,
        "size_mb": round(size_mb, 1)
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()

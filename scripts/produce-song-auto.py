#!/usr/bin/env python3
"""Jaopao Music Factory — Script ควบคุม flow + Spark ทำ creative"""

import json
import os
import subprocess
import urllib.request
from datetime import datetime

OLLAMA_URL = "http://192.168.1.199:11434"
MODEL = "qwen3.5:27b"
KIE_KEY = "26ecfa9d4abd06869689ca28062eb7a9"
ZERNIO_KEY = "sk_4224145db4a318d50ad22f087f57dcdf64890f11e08944e57aa2acb4119c85af"
YOUTUBE_ACCOUNT = "69b012a6dc8cab9432c8d81d"
BOT_TOKEN = "8376969560:AAH2rJtldj8fpLaByB20znOghQAPLgiHUPw"
OWNER_CHAT_ID = 5611560704
LOG_FILE = "/tmp/jaopao-music.log"

# Channel config
GENRE = "Retro Thai Soul Pop + Lofi Funk"
MUSIC_PROMPT = "Retro Thai Soul Pop, Lofi Funk, 80 BPM, F#m, Electric Piano Chorus FX, Soft Jazz Drums, Warm Bass, Clean Guitar, Saxophone, Vintage Synth Pad, Smooth Male Thai Vocal, Slow Rap"
STYLE_PROMPT = "A cinematic retro-inspired scene of a young man sitting quietly at an old wooden table, a single vase of flowers placed beside him. Warm golden-hour sunlight streams through a window, casting soft shadows across the room. He gazes thoughtfully with a nostalgic and melancholic expression, as if reflecting on love and the passage of time. Vintage retro outfit light shirt rolled sleeves dark trousers evoking 70s-80s pop aesthetics. Background softly blurred with hints of old Thai wooden architecture, adding a sense of timelessness. Dreamy intimate romantic, shallow depth of field, cinematic lens flare, subtle film grain, warm pastel amber tones"
LANGUAGE = "th:80,en:20"

# Song structure template
SONG_STRUCTURE = """[Intro] [Lofi Crackle]

[Verse 1] [Soft | Intimate]
{verse1}

[Pre-Chorus] [Build | Pads + Guitar]
{prechorus1}

[Chorus] [Smooth | Soulful Hook]
{chorus}

[Verse 2] [Medium | Add Drums & Groove]
{verse2}

[Rap] [Slow Cadence | Emotional]
{rap}

[Pre-Chorus] [Strings Swell]
{prechorus2}

[Chorus] [Full | Warm & Emotional]
{chorus}

[Bridge] [Saxophone Solo | Soulful | Dreamy]

[Final Chorus] [Epic Soul Release]
{chorus_final}

[Outro] [Fade | Vinyl Crackle]
{outro}
[End]"""

MOODS = ["Warm, Regretful, Intimate, Romantic, Emotional"]  # ผสม 5 mood ทุกเพลง

YOUTUBE_FOOTER = """
━━━━━━━━━━━━━━━━━━━
Spotify ค้นได้เลยพิมว่า : เจ้าเปา ได้เลยนะจั๊บ

ฝากคุณพี่ทุกท่านติดตาม เจ้าเปา (JaoPao) ได้ที่ Tiktok

จิ้มเบาๆที่นี้นะคร้าฟ : https://www.tiktok.com/@jaopaodogsong
━━━━━━━━━━━━━━━━━━━"""

LESSONS_FILE = "/Users/jaochai/.openclaw/workspace-music/memory/lessons.md"
EVOLUTION_LOG = "/Users/jaochai/.openclaw/workspace-music/memory/evolution_log.md"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)


def ask_spark(prompt, system=""):
    """Ask Spark via Ollama chat API with think:false."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": MODEL,
        "stream": False,
        "think": False,
        "options": {"num_ctx": 8192, "num_predict": 1000},
        "messages": messages,
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=180)
    data = json.loads(resp.read())
    return data.get("message", {}).get("content", "")


def check_credits():
    """Check KIE credits before starting."""
    req = urllib.request.Request(
        "https://api.kie.ai/api/v1/chat/credit",
        headers={"Authorization": f"Bearer {KIE_KEY}"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        credits = data.get("data", 0)
        log(f"  KIE Credits: {credits}")
        if credits < 100:
            send_telegram(f"⚠️ Music Factory: KIE credits เหลือน้อย! ({credits} credits)")
            return False
        return True
    except:
        return True  # ถ้าเช็คไม่ได้ ให้ทำต่อ


def kie_api(endpoint, payload):
    """Call KIE API with error handling."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"https://api.kie.ai{endpoint}",
        data=data,
        headers={"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_map = {
            402: "❌ Credits หมด! เติม credits ที่ kie.ai",
            429: "⚠️ Rate limit! รอสักครู่แล้วลองใหม่",
            455: "⚠️ KIE ปิดปรับปรุง (maintenance)",
            501: "❌ Generation failed!",
        }
        msg = error_map.get(e.code, f"❌ KIE API error {e.code}")
        log(f"  KIE Error: {msg}")
        send_telegram(f"Music Factory: {msg}")
        return {"code": e.code, "error": msg}


def poll_suno(task_id):
    """Poll Suno task until done. 15s interval, max 40 polls = 10 min."""
    import time
    for i in range(40):
        time.sleep(15)
        req = urllib.request.Request(
            f"https://api.kie.ai/api/v1/generate/record-info?taskId={task_id}",
            headers={"Authorization": f"Bearer {KIE_KEY}"},
        )
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        status = data.get("data", {}).get("status", "PENDING")
        log(f"  Suno poll {i+1}: {status}")
        if status == "SUCCESS":
            songs = data.get("data", {}).get("response", {}).get("sunoData", [])
            # เลือกเวอร์ชันที่ duration ใกล้ 180 วินาที (3 นาที) ที่สุด
            best = min(songs, key=lambda s: abs(s.get("duration", 0) - 180)) if songs else {}
            log(f"  Selected: {best.get('duration',0):.0f}s (from {len(songs)} versions)")
            return best.get("audioUrl", "")
        if status == "SENSITIVE_WORD_ERROR":
            log("  ⚠️ เนื้อเพลงโดนกรอง (sensitive word)")
            send_telegram("⚠️ Music Factory: เนื้อเพลงโดนกรอง! ต้องแก้เนื้อเพลง")
            return ""
        if "FAILED" in status or "ERROR" in status:
            error_msg = data.get("data", {}).get("errorMessage", status)
            log(f"  ❌ Suno failed: {error_msg}")
            send_telegram(f"❌ Music Factory: Suno failed — {error_msg}")
            return ""
    log("  ❌ Suno timeout (10 min)")
    send_telegram("❌ Music Factory: Suno timeout 10 นาที!")
    return ""


def quality_gate(lyrics, concept):
    """Quality Gate — ตรวจเนื้อเพลงก่อน publish."""
    required_sections = ["[Verse 1]", "[Chorus]", "[Rap]", "[Bridge]", "[Outro]"]
    missing = [s for s in required_sections if s not in lyrics]

    if missing:
        log(f"  Quality Gate: missing sections {missing}")
        return False, f"missing {missing}"

    if len(lyrics) < 500:
        log(f"  Quality Gate: lyrics too short ({len(lyrics)} chars)")
        return False, "lyrics too short"

    title = concept.get("title", "")
    if not title:
        return False, "no title"

    return True, "passed"


def load_lessons():
    """Learning Inject — โหลดบทเรียนจาก evolution_log."""
    lessons = []
    if os.path.exists(EVOLUTION_LOG):
        with open(EVOLUTION_LOG, "r") as f:
            content = f.read()
            if content.strip():
                # ดึง pattern ที่คนชอบ/ไม่ชอบ
                lessons.append(content[-500:])  # ใช้ล่าสุด 500 chars

    if os.path.exists(LESSONS_FILE):
        with open(LESSONS_FILE, "r") as f:
            content = f.read()
            if content.strip():
                lessons.append(content[-300:])

    return "\n".join(lessons) if lessons else ""


def save_lesson(lesson_text):
    """บันทึกบทเรียนจาก run นี้."""
    os.makedirs(os.path.dirname(LESSONS_FILE), exist_ok=True)
    with open(LESSONS_FILE, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"\n## {ts}\n{lesson_text}\n")


def poll_image(task_id):
    """Poll SeedDream 5 Lite task until done. 15s interval, max 15 polls = 3.75 min."""
    import time
    for i in range(15):
        time.sleep(15)
        req = urllib.request.Request(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {KIE_KEY}"},
        )
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
        except Exception as e:
            log(f"  Image poll error: {e}")
            continue
        state = data.get("data", {}).get("state", "waiting")
        fail_msg = data.get("data", {}).get("failMsg", "")
        log(f"  Image poll {i+1}: {state}")
        if state == "success":
            result = data.get("data", {}).get("resultJson", "")
            if result:
                r = json.loads(result) if isinstance(result, str) else result
                urls = r.get("resultUrls", [])
                return urls[0] if urls else ""
        if state == "failed":
            log(f"  ❌ Image failed: {fail_msg}")
            send_telegram(f"❌ Music Factory: Image failed — {fail_msg}")
            return ""
    log("  ❌ Image timeout (3.75 min)")
    send_telegram("❌ Music Factory: Image timeout!")
    return ""


def send_telegram(text):
    payload = json.dumps({"chat_id": OWNER_CHAT_ID, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except:
        pass


def main(publish_youtube=True):
    log("🎷 Starting Jaopao Music Factory...")

    # Step 0: Check credits
    log("Step 0: Credits check...")
    if not check_credits():
        log("❌ Not enough credits! Stopping.")
        return

    # Step 1: Spark คิด Concept + Theme (with Learning Inject)
    log("Step 1: Concept (with lessons)...")
    import random
    mood = random.choice(MOODS)

    # Learning Inject — ดึงบทเรียนจาก evolution_log
    lessons = load_lessons()
    lesson_prompt = f"\n\nบทเรียนจากเพลงก่อนหน้า:\n{lessons}" if lessons else ""

    concept = None
    for attempt in range(3):  # Self-Healing: retry 3 ครั้ง
        concept_raw = ask_spark(
            f"คิดเพลงใหม่ 1 เพลง แนว {GENRE} อารมณ์: {mood} ใช้ภาพเปรียบเทียบจากธรรมชาติ (ดอกไม้ ฤดูกาล แสงแดด ฝน ทะเล) เป็นแกนเรื่อง{lesson_prompt}\nตอบ JSON เท่านั้น: {{\"title\": \"ชื่อเพลงไทยที่สอดคล้องกับเนื้อหา\", \"title_en\": \"EnglishTitle\", \"concept\": \"เรื่องราวของเพลง 2-3 ประโยค ใช้ภาพเปรียบเทียบ\", \"mood\": \"{mood}\", \"scene\": \"ฉากสำหรับภาพปก 1 ประโยค\"}}",
            system=f"คุณเป็นโปรดิวเซอร์เพลง {GENRE} ใช้ภาพเปรียบเทียบ (metaphor) จากธรรมชาติเป็นแกนเรื่อง ชื่อเพลงต้องสอดคล้องกับ concept ตอบ JSON เท่านั้น"
        )
        try:
            if "```" in concept_raw:
                concept_raw = concept_raw.split("```")[1]
                if concept_raw.startswith("json"):
                    concept_raw = concept_raw[4:]
            concept = json.loads(concept_raw.strip())
            break
        except:
            log(f"  Concept parse retry {attempt+1}: {concept_raw[:100]}")
            if attempt == 2:
                log("Concept parse failed after 3 attempts")
                send_telegram("❌ Music Factory: Concept parse failed (3 attempts)")
                save_lesson("Concept parse failed — ปรับ prompt ให้ชัดขึ้น")
                return
    log(f"  Title: {concept.get('title')} ({concept.get('title_en')})")

    # Step 2: Spark เขียนเนื้อเพลงตามโครง
    log("Step 2: Lyrics...")
    lyrics = ask_spark(
        f"""เขียนเนื้อเพลง "{concept['title']}"
concept: {concept['concept']}
mood: {concept.get('mood', mood)}
ภาษาไทย 75% อังกฤษ 25%

หลักการเขียน:
- ใช้ภาพเปรียบเทียบ (metaphor) จากธรรมชาติเป็นแกนหลัก
- Verse เล่าเรื่องนุ่มนวลผ่านภาพ poetic
- Chorus ต้องมี hook ที่จำง่าย ซ้ำได้
- Hook อังกฤษ 1 บรรทัดใน Chorus
- Rap ต้อง poetic ไม่ aggressive ผสมไทย+อังกฤษ

ใช้โครงสร้างนี้เท่านั้น:

[Intro] [Lofi Crackle]

[Verse 1] [Soft | Intimate]
(4 บรรทัด — เล่าเรื่องผ่าน metaphor)

[Pre-Chorus] [Build | Pads + Guitar]
(4 บรรทัด — build อารมณ์)

[Chorus] [Smooth | Soulful Hook]
(4-6 บรรทัด — hook ชัด จำง่าย + 1 บรรทัดอังกฤษ)

[Verse 2] [Medium | Add Drums & Groove]
(4 บรรทัด — เล่าเรื่องต่อ เพิ่มความลึก)

[Rap] [Slow Cadence | Emotional]
(6 บรรทัด — poetic ผสมไทย+อังกฤษ ไม่ aggressive)

[Pre-Chorus] [Strings Swell]
(4 บรรทัด)

[Chorus] [Full | Warm & Emotional]
(เหมือน Chorus แรก)

[Bridge] [Saxophone Solo | Soulful | Dreamy]

[Final Chorus] [Epic Soul Release]
(4-6 บรรทัด — variation จาก Chorus หลัก)

[Outro] [Fade | Vinyl Crackle]
(1-2 บรรทัด — จบด้วย hook อังกฤษ)
[End]

เขียนเนื้อเพลงเลย ห้ามอธิบาย ห้ามพูดอะไรเพิ่ม""",
        system=f"นักแต่งเพลง {GENRE} ใช้ภาพเปรียบเทียบจากธรรมชาติ เขียนเนื้อเพลงเท่านั้น ห้ามอธิบาย"
    )
    log(f"  Lyrics: {len(lyrics)} chars")

    # Quality Gate — ตรวจเนื้อเพลงก่อนทำต่อ
    log("  Quality Gate...")
    passed, reason = quality_gate(lyrics, concept)
    if not passed:
        log(f"  Quality Gate FAILED: {reason} → rewriting...")
        # Self-Healing: ให้ Spark เขียนใหม่ 1 ครั้ง
        lyrics = ask_spark(
            f"เขียนเนื้อเพลงใหม่ \"{concept['title']}\" ให้ครบทุก section: [Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Rap] [Bridge] [Outro] concept: {concept['concept']} mood: {concept.get('mood', mood)} ภาษาไทย 80% อังกฤษ 20% เขียนเนื้อเพลงเลย ห้ามอธิบาย",
            system=f"นักแต่งเพลง {GENRE} เขียนเนื้อเพลงเท่านั้น ห้ามอธิบาย"
        )
        log(f"  Rewritten lyrics: {len(lyrics)} chars")
        passed2, reason2 = quality_gate(lyrics, concept)
        if not passed2:
            log(f"  Quality Gate FAILED again: {reason2}")
            save_lesson(f"Lyrics quality failed: {reason} → {reason2}")
            send_telegram(f"⚠️ Music Factory: Quality Gate failed — {reason2} (ทำต่อด้วย lyrics ที่มี)")
    else:
        log("  Quality Gate: PASSED ✅")

    # Step 3: Image Prompt ตาม theme + scene
    log("Step 3: Image prompt...")
    scene = concept.get("scene", "a young man sitting quietly with flowers")
    image_prompt = f"{STYLE_PROMPT}, {scene}, {concept['concept']}, album cover art style, 16:9 cinematic, no text, no words, no letters, no typography, no watermark"

    # Step 4-6: PARALLEL — Suno + SeedDream + SEO พร้อมกัน!
    log("Step 4-6: Parallel (Suno + Image + SEO)...")
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Launch Suno first (ช้าสุด)
    log("  → Launching Suno V5...")
    suno_resp = kie_api("/api/v1/generate", {
        "prompt": lyrics[:5000],
        "customMode": True,
        "instrumental": False,
        "model": "V5",
        "style": concept.get("suno_style", MUSIC_PROMPT),
        "title": concept["title"][:80],
        "callBackUrl": "https://httpbin.org/post",
    })
    suno_task = suno_resp.get("data", {}).get("taskId", "")
    if not suno_task:
        log(f"  Suno failed: {suno_resp}")
        send_telegram("❌ Music Factory: Suno failed")
        return

    # Launch Image
    log("  → Launching SeedDream 5 Lite...")
    img_resp = kie_api("/api/v1/jobs/createTask", {
        "model": "seedream/5-lite-text-to-image",
        "task_type": "text-to-image",
        "input": {"prompt": image_prompt, "aspect_ratio": "16:9", "quality": "basic"},
    })
    img_task = img_resp.get("data", {}).get("taskId", "")

    # Run Suno poll + Image poll + SEO in parallel
    music_url = ""
    image_url = ""
    seo = {}

    def do_suno():
        return poll_suno(suno_task)

    def do_image():
        return poll_image(img_task) if img_task else ""

    def do_seo():
        # YouTube title format: {ชื่อไทย} ({ชื่ออังกฤษ}) JaoPao | Official Music Audio
        yt_title = f"{concept['title']} ({concept.get('title_en', '')}) JaoPao | Official Music Audio"
        seo_raw = ask_spark(
            f"เขียน YouTube description สำหรับเพลง \"{concept['title']}\" แนว {GENRE} concept: {concept.get('concept','')} ตอบ JSON: {{\"seo_description\": \"description ที่มีเนื้อเพลง + hashtags + credit เจ้าเปา\"}}",
            system="เขียน YouTube SEO description ตอบ JSON เท่านั้น"
        )
        try:
            if "```" in seo_raw:
                seo_raw_clean = seo_raw.split("```")[1]
                if seo_raw_clean.startswith("json"):
                    seo_raw_clean = seo_raw_clean[4:]
                parsed = json.loads(seo_raw_clean.strip())
            else:
                parsed = json.loads(seo_raw.strip())
            return {"seo_title": yt_title, "seo_description": parsed.get("seo_description", lyrics[:500])}
        except:
            return {"seo_title": yt_title, "seo_description": lyrics[:500]}

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_suno = executor.submit(do_suno)
        future_image = executor.submit(do_image)
        future_seo = executor.submit(do_seo)

        seo = future_seo.result()
        log(f"  ✅ SEO done: {seo.get('seo_title','')[:50]}")

        image_url = future_image.result()
        if image_url:
            log(f"  ✅ Image done: {image_url[:60]}...")
        else:
            log("  ❌ Image failed")
            send_telegram("❌ Music Factory: Image failed")
            return

        music_url = future_suno.result()
        if music_url:
            log(f"  ✅ Music done: {music_url[:60]}...")
        else:
            log("  ❌ Suno timeout/failed")
            send_telegram("❌ Music Factory: Suno timeout")
            return

    # Step 7: FFmpeg
    log("Step 7: FFmpeg...")
    import tempfile
    work_dir = tempfile.mkdtemp(prefix="jaopao_")
    # Download with retry (KIE server can be slow)
    for attempt in range(3):
        try:
            log(f"  Downloading music (attempt {attempt+1})...")
            subprocess.run(["curl", "-sL", "--connect-timeout", "30", "--max-time", "180", "-o", f"{work_dir}/music.mp3", music_url], timeout=200)
            if os.path.getsize(f"{work_dir}/music.mp3") > 1000:
                break
        except:
            log(f"  Download music retry {attempt+1}")
    for attempt in range(3):
        try:
            log(f"  Downloading cover (attempt {attempt+1})...")
            subprocess.run(["curl", "-sL", "--connect-timeout", "30", "--max-time", "180", "-o", f"{work_dir}/cover.jpg", image_url], timeout=200)
            if os.path.getsize(f"{work_dir}/cover.jpg") > 1000:
                break
        except:
            log(f"  Download cover retry {attempt+1}")
    result = subprocess.run([
        "ffmpeg", "-loop", "1", "-i", f"{work_dir}/cover.jpg",
        "-i", f"{work_dir}/music.mp3",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-shortest", "-y",
        f"{work_dir}/output.mp4"
    ], capture_output=True, timeout=300)
    if not os.path.exists(f"{work_dir}/output.mp4"):
        log("  FFmpeg failed")
        send_telegram("❌ Music Factory: FFmpeg failed")
        return
    size_mb = os.path.getsize(f"{work_dir}/output.mp4") / 1024 / 1024
    log(f"  ✅ MP4: {size_mb:.1f} MB")

    # Step 8: KIE Upload
    log("Step 8: Upload...")
    title_en = concept.get("title_en", "song").replace(" ", "-")
    upload_cmd = subprocess.run([
        "curl", "-s", "-X", "POST", "https://kieai.redpandaai.co/api/file-stream-upload",
        "-H", f"Authorization: Bearer {KIE_KEY}",
        "-F", f"file=@{work_dir}/output.mp4",
        "-F", "uploadPath=jaopao",
        "-F", f"fileName={title_en}-{datetime.now().strftime('%Y%m%d')}.mp4"
    ], capture_output=True, timeout=300)
    try:
        upload_data = json.loads(upload_cmd.stdout)
        video_url = upload_data.get("data", {}).get("downloadUrl", "")
    except:
        video_url = ""
    if not video_url:
        log("  Upload failed")
        send_telegram("❌ Music Factory: Upload failed")
        return
    log(f"  ✅ URL: {video_url[:60]}...")

    # Step 9: YouTube (optional)
    if publish_youtube:
        log("Step 9: YouTube...")
        yt_json = json.dumps({
            "content": (seo.get("seo_description", "") + YOUTUBE_FOOTER)[:2000],
            "title": seo.get("seo_title", concept["title"]),
            "mediaUrls": [video_url],
            "platforms": [{"platform": "youtube", "accountId": YOUTUBE_ACCOUNT}],
        })
        yt_req = urllib.request.Request(
            "https://zernio.com/api/v1/posts",
            data=yt_json.encode(),
            headers={"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"},
        )
        try:
            yt_resp = json.loads(urllib.request.urlopen(yt_req, timeout=60).read())
            yt_status = yt_resp.get("post", {}).get("status", "unknown")
            log(f"  ✅ YouTube: {yt_status}")
        except Exception as e:
            log(f"  YouTube error: {e}")
    else:
        log("Step 9: YouTube SKIPPED (test mode)")

    # Step 10: Notify Telegram
    log("Step 10: Notify...")
    send_telegram(f"""🎷 เพลงใหม่วันนี้!

ชื่อ: {concept['title']} ({concept.get('title_en','')})
แนว: {concept.get('mood','')}
🎵 เพลง: {music_url}
🖼️ รูปปก: {image_url}
🎬 วิดีโอ: {video_url}
📺 YouTube: {'Published' if publish_youtube else 'SKIPPED (test)'}""")

    # Cleanup
    import shutil
    shutil.rmtree(work_dir, ignore_errors=True)

    # Save lesson from this run
    save_lesson(f"เพลง: {concept['title']} | mood: {concept.get('mood','')} | lyrics: {len(lyrics)} chars | duration: selected | สำเร็จ")

    log(f"🎷🎉 Done! Title: {concept['title']}")


if __name__ == "__main__":
    import sys
    publish = "--publish" in sys.argv
    main(publish_youtube=publish)

---
name: music-factory
description: ผลิตเพลง AI อัตโนมัติ — Script ควบคุม + Spark creative | Parallel pipeline | SeedDream 5 Lite | Suno V5 | Quality Gate + Self-Healing + Learning
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: [curl, ffmpeg, python3]
---

# Music Factory 🎷

ผลิตเพลงอัตโนมัติสำหรับช่อง YouTube
Script: produce-song-auto.py ควบคุม flow + Spark (27b think:false) ทำ creative

## วิธีทำงาน
Script ควบคุม (ไม่ใช่ agent ทำเอง):
- Spark ทำ: concept, เนื้อเพลง, SEO
- Script ทำ: API calls, format, upload, error handling

## Style ช่องเจ้าเปา
- Genre: Retro Thai Soul Pop + Lofi Funk
- Tempo: 80 BPM | Key: F#m
- Vocal: Smooth Male Thai + Slow Rap
- Instruments: Electric Piano, Jazz Drums, Warm Bass, Guitar, Saxophone, Synth Pad
- Mood: สุ่มจาก 10 อารมณ์ (Warm, Regretful, Intimate, Romantic, Emotional, Nostalgic, Melancholic, Hopeful, Bittersweet, Dreamy)
- ภาษา: ไทย 80% อังกฤษ 20%

## โครงเพลง (Template ตายตัว)
[Intro] Lofi Crackle → [Verse 1] Soft | Intimate → [Pre-Chorus] Build | Pads + Guitar → [Chorus] Smooth | Soulful Hook → [Verse 2] Medium | Drums & Groove → [Rap] Slow Cadence | Emotional → [Pre-Chorus] Strings Swell → [Chorus] Full | Warm → [Bridge] Saxophone Solo → [Final Chorus] Epic Soul Release → [Outro] Fade | Vinyl Crackle

## Pipeline (Parallel)

Step 0: Credits check (< 100 = หยุด)
Step 1: Concept + Learning Inject (lessons → prompt)
Step 2: Lyrics + Quality Gate (เช็ค sections + rewrite ถ้า fail)
Step 3: Image prompt (cinematic retro + scene + no text)
Step 4-6: PARALLEL ⚡ Suno V5 + SeedDream 5 Lite + SEO
Step 7: FFmpeg (รูป + เพลง → MP4)
Step 8: KIE Upload
Step 9: Zernio → YouTube
Step 10: Notify Telegram + Save Lesson

## YouTube Title Format
`{ชื่อไทย} ({ชื่ออังกฤษ}) JaoPao | Official Music Audio`
ตัวอย่าง: ทำไมแค่ฉันคนเดียวไม่พอ (Why Am I Never Enough) JaoPao | Official Music Audio

## APIs

### KIE Suno V5 (เพลง)
- POST https://api.kie.ai/api/v1/generate
- Params: prompt (5000 chars max), customMode: true, instrumental: false, model: "V5", style, title (80 chars max)
- Poll: GET /api/v1/generate/record-info?taskId= (15s interval, max 40 polls)
- เลือก: duration ใกล้ 180 วินาที

### KIE SeedDream 5 Lite (รูป)
- POST https://api.kie.ai/api/v1/jobs/createTask
- model: "seedream/5-lite-text-to-image"
- input: {prompt + "no text no words no letters", aspect_ratio: "16:9", quality: "basic"}
- Poll: GET /api/v1/jobs/recordInfo?taskId= (15s interval, max 15 polls)

### KIE Upload
- POST https://kieai.redpandaai.co/api/file-stream-upload
- Returns: downloadUrl (3 days)

### Zernio YouTube
- POST https://zernio.com/api/v1/posts
- accountId: 69b012a6dc8cab9432c8d81d

## AutoResearchClaw Patterns

### Quality Gate
- เช็ค: [Verse 1], [Chorus], [Rap], [Bridge], [Outro] ครบ
- ความยาว > 500 chars
- Fail → Spark rewrite 1 ครั้ง

### Self-Healing
- Concept parse: retry 3 ครั้ง
- Suno: SENSITIVE_WORD_ERROR → แจ้ง Telegram
- Download: retry 3 ครั้ง + 180s timeout
- Error → log + แจ้ง Telegram ทุก type (402/429/455/501)

### Learning Inject
- อ่าน lessons.md + evolution_log.md
- ใส่กลับเข้า concept prompt
- Save lesson หลังทุก run

### PIVOT/REFINE (style-evolver)
- PROCEED / REFINE / PIVOT
- Max 2 pivots

## Database (Neon: dawn-frost-22911856)
- channels: config ช่อง
- songs: เพลงที่สร้าง
- jobs: log แต่ละ step
- feedback: views/likes/comments
- evolution_log: การปรับ style

## Cron
- Daily Song: 13:00 (script trigger)
- Feedback: 20:00
- Style Evolve: จันทร์ 06:00

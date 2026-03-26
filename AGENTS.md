# Music Factory Pipeline

## วิธีทำงาน
Script produce-song-auto.py ทำทุกอย่าง (creative + API + upload + publish)
Agent แค่สั่ง exec script → script เรียก Spark ทำ creative เอง

## สั่งผลิตเพลง
```bash
exec /usr/bin/python3 /Users/jaochai/.openclaw/workspace-music/scripts/produce-song-auto.py --publish
```

## Script ทำอะไรบ้าง (11 Steps)
Step 0: Credits check (< 100 = หยุด)
Step 1: Spark คิด Concept + Learning Inject
Step 2: Spark เขียนเนื้อเพลง + Quality Gate
Step 3: Image prompt (cinematic retro + no text)
Step 4-6: PARALLEL — Suno V5 + SeedDream 5 Lite + SEO
Step 7: FFmpeg (รูป + เพลง → MP4)
Step 8: KIE Upload
Step 9: Zernio → YouTube
Step 10: Notify Telegram (script ส่งเอง) + Save Lesson

## Style ช่องเจ้าเปา
- Genre: Retro Thai Soul Pop + Lofi Funk
- Tempo: 80 BPM | Key: F#m
- Vocal: Smooth Male Thai + Slow Rap
- Instruments: Electric Piano, Jazz Drums, Warm Bass, Guitar, Saxophone, Synth Pad

## กฎสำคัญ
1. ใช้ produce-song-auto.py เท่านั้น (ไม่ใช้ produce-api.py)
2. Script ส่ง Telegram เอง → delivery: silent
3. ถ้า script error → แจ้ง Telegram อัตโนมัติ
4. ไม่ต้องทำ creative เอง — script + Spark จัดการ

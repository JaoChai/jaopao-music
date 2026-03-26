---
name: feedback-collector
description: เก็บ feedback จาก YouTube (views, likes, comments) ผ่าน Zernio Analytics API + บันทึก JSONL lessons
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: [curl]
---

# Feedback Collector 📊

เก็บ feedback ของเพลงจาก YouTube อัตโนมัติ + บันทึกเป็น JSONL

## Zernio Analytics API
- GET https://zernio.com/api/v1/analytics?platform=youtube&account_id=69b012a6dc8cab9432c8d81d
- Auth: Bearer $ZERNIO_API_KEY
- ข้อจำกัด: ดึงได้ 100 posts ล่าสุด
- ต้อง Build + Analytics plan

## Pipeline

### Step 1: ดึง Analytics
```bash
curl -s "https://zernio.com/api/v1/analytics?platform=youtube&account_id=69b012a6dc8cab9432c8d81d&limit=100&sort_by=date&order=desc" \
  -H "Authorization: Bearer $ZERNIO_API_KEY"
```
Response: posts[].analytics: views, likes, comments, engagementRate

### Step 2: บันทึก feedback table (Neon)
```sql
INSERT INTO feedback (song_id, channel_id, views, likes, comments, engagement_rate)
```

### Step 3: บันทึก JSONL lesson (ถ้ามีข้อมูลน่าสนใจ)
```json
{"stage": "feedback", "category": "content", "severity": "info", "description": "เพลง X views สูงสุด mood=Romantic", "timestamp": "...", "run_id": "..."}
```

### Step 4: แจ้ง Telegram (ถ้ามีอะไรพิเศษ)
- views เพิ่ม > 50 ในวันเดียว
- comment ใหม่
- engagement rate สูงผิดปกติ
- ถ้าไม่มีอะไรพิเศษ → ไม่แจ้ง

## Cron: ทุกวัน 20:00

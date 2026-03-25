---
name: feedback-collector
description: เก็บ feedback จาก YouTube (views, likes, comments, engagement) ผ่าน Zernio Analytics API แล้วบันทึกลง DB
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: [curl]
---

# Feedback Collector 📊

เก็บ feedback ของเพลงทั้งหมดจาก YouTube อัตโนมัติ

## วิธีใช้
เรียกจาก Cron Job: `เก็บ feedback สำหรับช่อง [ชื่อช่อง]`

## Pipeline

### Step 1: ดึง Analytics จาก Zernio
```bash
curl -s "https://zernio.com/api/v1/analytics?platform=youtube&account_id=69b012a6dc8cab9432c8d81d&limit=100&source=all&sort_by=date&order=desc" \
  -H "Authorization: Bearer $ZERNIO_API_KEY"
```
Response มี posts[].analytics: views, likes, comments, engagementRate

### Step 2: จับคู่กับ songs ใน DB
- ใช้ mcp__neon__run_sql query songs table
- จับคู่ด้วย title หรือ youtube_url
- ถ้าเจอ → UPDATE feedback

### Step 3: INSERT/UPDATE feedback table
```sql
INSERT INTO feedback (song_id, channel_id, views, likes, comments, engagement_rate)
VALUES ({song_id}, {channel_id}, {views}, {likes}, {comments}, {engagement_rate})
```
- เก็บ snapshot ณ เวลานั้น → ดู trend ได้

### Step 4: สรุปผล
วิเคราะห์สั้นๆ:
- เพลงไหน views เพิ่มขึ้นมากสุดวันนี้?
- เพลงไหน engagement ดีที่สุด?
- มี comment ใหม่ไหม?

### Step 5: แจ้ง Telegram (ถ้ามีอะไรน่าสนใจ)
ถ้ามีเพลงที่ views เพิ่มขึ้น > 50 ในวันเดียว หรือมี comment ใหม่:
```
📊 Daily Feedback Report — เจ้าเปา
🔥 เพลงที่ views เพิ่มมากสุด: {title} (+{delta} views)
💬 Comments ใหม่: {count}
📈 Top engagement: {title} ({rate}%)
```
ถ้าไม่มีอะไรพิเศษ → ไม่ต้องแจ้ง

## Zernio API
- Base: https://zernio.com/api/v1
- Auth: Bearer $ZERNIO_API_KEY
- Analytics: GET /analytics?platform=youtube&account_id=69b012a6dc8cab9432c8d81d
- ข้อจำกัด: ดึงได้ 100 posts ล่าสุด

## Database
- Neon Project: dawn-frost-22911856
- Table: feedback (song_id, views, likes, comments, engagement_rate, collected_at)

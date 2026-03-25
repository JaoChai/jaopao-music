---
name: style-evolver
description: วิเคราะห์ feedback ของเพลงทั้งสัปดาห์ แล้วปรับ music_prompt + style_prompt อัตโนมัติ เพื่อให้เพลงถัดไป perform ดีขึ้น
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: [curl]
---

# Style Evolver 🧬

วิเคราะห์ performance ของเพลงแล้วปรับ style อัตโนมัติ

## วิธีใช้
เรียกจาก Cron Job: `วิเคราะห์และปรับ style สำหรับช่อง [ชื่อช่อง]`

## Pipeline

### Step 1: ดึง feedback ย้อนหลัง 7 วัน
```sql
SELECT s.title, s.concept, s.lyrics, s.image_prompt,
       f.views, f.likes, f.comments, f.engagement_rate
FROM feedback f
JOIN songs s ON f.song_id = s.id
WHERE f.channel_id = {channel_id}
  AND f.collected_at >= NOW() - INTERVAL '7 days'
ORDER BY f.views DESC
```

### Step 2: ดึง channel config ปัจจุบัน
```sql
SELECT genre, music_prompt, style_prompt FROM channels WHERE id = {channel_id}
```

### Step 3: Spark วิเคราะห์ Pattern
Prompt:
```
คุณเป็นนักวิเคราะห์ข้อมูล YouTube Music Channel
วิเคราะห์ data ต่อไปนี้แล้วตอบเป็น JSON:

เพลงที่ perform ดี (views สูง + engagement สูง):
{top_songs_data}

เพลงที่ perform ไม่ดี (views ต่ำ):
{bottom_songs_data}

Channel config ปัจจุบัน:
- genre: {genre}
- music_prompt: {music_prompt}
- style_prompt: {style_prompt}

วิเคราะห์และตอบ JSON:
{
  "analysis": "สรุปว่าเพลงแบบไหนคนชอบ แบบไหนไม่ชอบ 3-5 ประโยค",
  "top_patterns": ["pattern ที่เพลง views สูงมีร่วมกัน"],
  "weak_patterns": ["pattern ที่เพลง views ต่ำมีร่วมกัน"],
  "recommended_music_prompt": "music prompt ใหม่ที่ปรับตาม pattern ที่ดี",
  "recommended_style_prompt": "style prompt ใหม่สำหรับรูปปก",
  "confidence": "high/medium/low — ถ้า data น้อยเกินให้ตอบ low",
  "changes_summary": "สรุปสิ่งที่เปลี่ยนจากเดิม 1-2 ประโยค"
}
```

### Step 4: ตัดสินใจ
- ถ้า confidence = "high" → UPDATE channels อัตโนมัติ
- ถ้า confidence = "medium" → UPDATE แต่แจ้ง Telegram ให้เจ้านายรู้
- ถ้า confidence = "low" → ไม่เปลี่ยน แจ้ง Telegram ว่า data ไม่พอ

### Step 5: UPDATE channels (ถ้า confidence >= medium)
```sql
UPDATE channels
SET music_prompt = '{recommended_music_prompt}',
    style_prompt = '{recommended_style_prompt}',
    updated_at = NOW()
WHERE id = {channel_id}
```

### Step 6: บันทึก evolution_log
```sql
INSERT INTO evolution_log
(channel_id, old_music_prompt, new_music_prompt, old_style_prompt, new_style_prompt, analysis, reason)
VALUES ({channel_id}, '{old}', '{new}', '{old}', '{new}', '{analysis}', '{changes_summary}')
```

### Step 7: แจ้ง Telegram
```
🧬 Style Evolution Report — เจ้าเปา
📊 วิเคราะห์จาก {count} เพลง (7 วันล่าสุด)

📈 Pattern ที่คนชอบ:
{top_patterns}

📉 Pattern ที่ต้องปรับ:
{weak_patterns}

🔄 สิ่งที่เปลี่ยน:
{changes_summary}

🎵 Music prompt ใหม่: {new_music_prompt}
🖼️ Style prompt ใหม่: {new_style_prompt}

Confidence: {confidence}
```

## กฎสำคัญ
1. ห้ามเปลี่ยน genre หลัก (retro-saxophone-rnb) — ปรับแค่ sub-style
2. ต้องเก็บ log ทุกครั้งที่เปลี่ยน (evolution_log)
3. ถ้า data น้อยกว่า 5 เพลง → confidence = low → ไม่เปลี่ยน
4. ปรับ prompt แบบ incremental ไม่เปลี่ยนหน้ามือเป็นหลังมือ
5. แจ้ง Telegram ทุกครั้ง

## Database
- Neon Project: dawn-frost-22911856
- Read: feedback, songs, channels
- Write: channels (UPDATE), evolution_log (INSERT)

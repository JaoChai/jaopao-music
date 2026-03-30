---
name: style-evolver
description: วิเคราะห์ feedback + PIVOT/REFINE decision + ปรับ style อัตโนมัติ ตาม AutoResearchClaw pattern
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: [curl]
---

# Style Evolver 🧬

วิเคราะห์ performance แล้วปรับ style อัตโนมัติ ตาม AutoResearchClaw pattern

## Pipeline

### Step 1: ดึง feedback + metadata 7 วันล่าสุด
```sql
SELECT s.title, s.concept, s.mood, s.suno_prompt, s.image_prompt, f.views, f.likes, f.comments, f.engagement_rate
FROM feedback f JOIN songs s ON f.song_id = s.id
WHERE f.collected_at >= NOW() - INTERVAL '7 days'
ORDER BY f.views DESC
```

### Step 2: ดึง channel config ปัจจุบัน
```sql
SELECT genre, music_prompt, style_prompt FROM channels WHERE id = {channel_id}
```

### Step 3: วิเคราะห์ Pattern (Spark)
Spark วิเคราะห์แล้วตอบ JSON:
```json
{
  "analysis": "สรุป 3-5 ประโยค",
  "top_patterns": ["pattern ที่เพลง views สูงมี — tags, mood, scene ใน image"],
  "weak_patterns": ["pattern ที่เพลง views ต่ำมี"],
  "top_suno_tags": ["suno tags ที่เพลง views สูงใช้"],
  "top_image_scenes": ["image scene/element ที่เพลง views สูงใช้"],
  "recommended_music_prompt": "prompt ใหม่",
  "recommended_style_prompt": "style ใหม่",
  "recommended_image_template": "image template ที่แนะนำ",
  "confidence": "high/medium/low",
  "decision": "PROCEED/REFINE/PIVOT",
  "decision_reason": "เหตุผล",
  "changes_summary": "สรุปสิ่งที่เปลี่ยน"
}
```

### Step 4: PIVOT/REFINE Decision (ตาม AutoResearchClaw)

**PROCEED** — style ดี ไม่เปลี่ยน
- Views ดีขึ้นหรือคงที่
- บันทึก: "style ปัจจุบันดี"

**REFINE** — ปรับ params เล็กน้อย
- Views ลดลงเล็กน้อย แต่มี pattern ชัด
- confidence >= medium → UPDATE channels
- confidence = low → ไม่เปลี่ยน

**PIVOT** — เปลี่ยนแนวทาง
- Views ลดลงต่อเนื่อง 2+ สัปดาห์
- REFINE ไม่ได้ผล
- Max 2 pivots → เกิน → แจ้งเจ้านายตัดสินใจ

**Hint Detectors (ป้องกัน infinite loop):**
- Degenerate: metrics ไม่เปลี่ยน 2 รอบ → force PROCEED
- Saturation: metrics ดีสุดแล้ว → PROCEED
- No-improve: ไม่ดีขึ้น 2 รอบ → หยุด

### Step 5: UPDATE channels (ถ้า confidence >= medium)
```sql
UPDATE channels SET music_prompt = '...', style_prompt = '...', updated_at = NOW()
```

### Step 5.5: อัพเดท winning tags + image notes ให้ music-producer อ่านได้
บันทึก winning combination ลงไฟล์ `~/code/jaopao-music/knowledge/winning-combos.md`:
- Suno tags ที่เพลง views สูงสุดใช้ (top 5)
- Image scene/element ที่ได้ผลดีสุด (top 5)
- Format: Markdown table ให้ music-producer อ่านง่าย

### Step 6: บันทึก evolution_log + JSONL lesson
```sql
INSERT INTO evolution_log (channel_id, old_music_prompt, new_music_prompt, ...)
```

JSONL lesson:
```json
{"stage": "style_evolve", "category": "content", "severity": "info", "description": "REFINE: ปรับ mood ratio เพิ่ม Romantic 20%", "timestamp": "...", "run_id": "..."}
```

### Step 7: แจ้ง Telegram
```
🧬 Style Evolution Report — เจ้าเปา
📊 วิเคราะห์จาก {count} เพลง
📈 Top patterns: ...
📉 Weak patterns: ...
🔄 Decision: PROCEED/REFINE/PIVOT
💡 Changes: ...
```

## กฎสำคัญ
1. ห้ามเปลี่ยน genre หลัก (Retro Thai Soul Pop + Lofi Funk)
2. เก็บ log ทุกครั้ง (evolution_log + JSONL)
3. Data < 5 เพลง → confidence = low → ไม่เปลี่ยน
4. ปรับ incremental ไม่เปลี่ยนหน้ามือเป็นหลังมือ
5. Max 2 pivots

## Learning Inject
- lessons จาก JSONL inject กลับเข้า concept prompt รอบถัดไป
- Decay: half-life 30 วัน, หมดอายุ 90 วัน

## Cron: ทุกจันทร์ 06:00

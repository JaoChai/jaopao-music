---
name: music-factory
description: ผลิตเพลง AI อัตโนมัติ — Concept → เนื้อเพลง → Suno → รูปปก → FFmpeg → KIE Upload → Zernio YouTube
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: [curl, ffmpeg]
---

# Music Factory 🎷

ผลิตเพลงอัตโนมัติสำหรับช่อง YouTube ทำตาม AGENTS.md ทุกขั้นตอน 10 steps

## วิธีใช้
เรียกโดยระบุชื่อช่อง:
`ผลิตเพลงสำหรับช่อง [ชื่อช่อง]`

## Pipeline 10 Steps
1. อ่าน channel config จาก DB
2. Spark คิด concept (JSON: title, concept, mood, tempo, suno_style)
3. Spark เขียนเนื้อเพลง (Suno format, ภาษาตาม config)
4. KIE → Suno สร้างเพลง (V5, customMode)
5. KIE → NanoBanana 2 สร้างรูปปก (16:9)
6. FFmpeg รวม รูป + เพลง → MP4
7. KIE Upload → public URL
8. Spark เขียน YouTube SEO (title, description, tags)
9. Zernio → YouTube upload
10. แจ้ง Telegram ให้เจ้านาย

## APIs

### KIE Suno (เพลง)
- Endpoint: POST https://api.kie.ai/api/v1/generate
- Auth: Bearer $KIE_API_KEY
- Params: prompt (lyrics), customMode: true, instrumental: false, model: "V5", style, title
- Poll: GET https://api.kie.ai/api/v1/generate/record-info?taskId=

### KIE NanoBanana (รูป)
- Endpoint: POST https://api.kie.ai/api/v1/jobs/createTask
- Auth: Bearer $KIE_API_KEY
- Params: model: "nano-banana-2", task_type: "text-to-image", input: {prompt, aspect_ratio: "16:9"}
- Poll: GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=

### KIE File Upload
- Endpoint: POST https://kieai.redpandaai.co/api/file-stream-upload
- Auth: Bearer $KIE_API_KEY
- Multipart: file, uploadPath, fileName
- Returns: downloadUrl (public, 3 days)

### Zernio YouTube
- Endpoint: POST https://zernio.com/api/v1/posts
- Auth: Bearer $ZERNIO_API_KEY
- Params: content, title, mediaUrls, platforms: [{platform: "youtube", accountId: "69b012a6dc8cab9432c8d81d"}]

### FFmpeg
```bash
ffmpeg -loop 1 -i cover.jpg -i music.mp3 \
  -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
  -pix_fmt yuv420p -shortest -y output.mp4
```

## Database
- Neon Project: dawn-frost-22911856
- channels: config ของแต่ละช่อง
- songs: เพลงที่สร้าง (status tracking)
- jobs: log แต่ละ step

## Prompt Templates

### Concept Prompt
```
คุณเป็นโปรดิวเซอร์เพลงมืออาชีพ เชี่ยวชาญแนว {genre}
คิด concept เพลงใหม่ 1 เพลง ไม่ซ้ำกับ: [existing titles]
แนวเพลง: {music_prompt}
ตอบ JSON: {title, title_en, concept, mood, tempo, suno_style}
```

### Lyrics Prompt
```
นักแต่งเพลงแนว {genre}
เขียนเนื้อเพลง "{title}" concept: {concept} mood: {mood} tempo: {tempo}
ภาษา: {language}
Format: [Verse] [Chorus] [Bridge] [Saxophone Solo] [Outro]
ความยาว 3 นาที ห้ามใส่คำอธิบาย
```

### Image Prompt
```
{style_prompt}, inspired by "{title}" about {concept}, album cover art, 16:9 cinematic
```

### SEO Prompt
```
YouTube SEO สำหรับ "{title}" แนว {genre} concept: {concept}
JSON: {seo_title (≤100 chars + emoji), seo_description (เนื้อเพลง+hashtags), seo_tags}
```

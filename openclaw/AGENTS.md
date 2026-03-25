# Music Factory Pipeline

## วิธีทำงาน
Spark ทำ 2 ส่วน:
1. **Creative** — คิด concept, เขียนเนื้อเพลง, คิด image prompt, เขียน SEO (ใช้สมอง Qwen)
2. **Execute** — เรียก script `produce-song.sh` ที่ทำ API calls ทั้งหมดให้ (Suno, NanoBanana, FFmpeg, Upload, YouTube)

## Pipeline

### Part 1: Creative (Spark คิดเอง)

**Step 1: คิด Concept**
คิดเพลงใหม่ 1 เพลง แนว retro saxophone r&b ตอบเป็น JSON:
```json
{
  "title": "ชื่อเพลงไทย",
  "title_en": "English-Title-No-Spaces",
  "concept": "เรื่องราว 2-3 ประโยค",
  "mood": "อารมณ์",
  "tempo": "BPM",
  "suno_style": "retro r&b, saxophone solo, 70s groove, smooth vocals, ..."
}
```

**Step 2: เขียนเนื้อเพลง**
เขียนเนื้อเพลงตาม concept ภาษาไทย 90% อังกฤษ 10%
Format: [Verse] [Chorus] [Bridge] [Saxophone Solo] [Outro]
ความยาว 3 นาที ห้ามใส่คำอธิบาย เฉพาะ lyrics

**Step 3: คิด Image Prompt**
```
retro vinyl record, saxophone player silhouette, neon lights, 80s aesthetic, warm golden tones, vintage microphone, smoky jazz bar atmosphere, inspired by "{title}" about {concept}, album cover art, 16:9 cinematic
```

**Step 4: เขียน YouTube SEO**
```json
{
  "seo_title": "ชื่อ YouTube ≤100 ตัวอักษร + emoji + keyword",
  "seo_description": "เนื้อเพลง + hashtags + credit เจ้าเปา (JaoPao)"
}
```

### Part 2: Execute (เรียก Script)

หลังจากคิด creative เสร็จ เรียก script:
```bash
/Users/jaochai/.openclaw/workspace-music/scripts/produce-song.sh \
  "CONCEPT" \
  "LYRICS" \
  "SUNO_STYLE" \
  "TITLE" \
  "TITLE_EN" \
  "IMAGE_PROMPT" \
  "SEO_TITLE" \
  "SEO_DESCRIPTION"
```

Script จะทำ:
1. Suno V5 สร้างเพลง (poll จนเสร็จ)
2. NanoBanana 2 สร้างรูปปก
3. FFmpeg รวม → MP4
4. KIE Upload → public URL
5. Zernio → YouTube ช่องเจ้าเปา

### Part 3: แจ้ง Telegram
หลัง script เสร็จ ส่งข้อความ:
```
🎷 เพลงใหม่วันนี้!
ชื่อ: {title}
ช่อง: เจ้าเปา
สถานะ: {status จาก script output}
```

## กฎสำคัญ
1. คิด creative ก่อน แล้วค่อยเรียก script
2. ถ้า script error → แจ้ง Telegram พร้อม error message
3. ห้ามสร้างเพลงชื่อซ้ำ
4. ภาษาไทย 90% อังกฤษ 10%
5. แนวเพลง: retro + saxophone + r&b เท่านั้น

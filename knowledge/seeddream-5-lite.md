# 🎨 คู่มือ SeedDream 5 Lite — รูปปกเพลงเจ้าเปา

> คู่มือฉบับสมบูรณ์สำหรับสร้างรูปปกเพลงด้วย SeedDream 5 Lite ผ่าน KIE API

---

## 📑 สารบัญ

1. [หลักพื้นฐานของ Prompt](#1-หลักพื้นฐานของ-prompt)
2. [สูตร Prompt](#2-สูตร-prompt)
3. [ภาษาทางภาพถ่าย](#3-ภาษาทางภาพถ่าย)
4. [เทมเพลตสำหรับรูปปกเพลง 5 แบบ](#4-เทมเพลตสำหรับรูปปกเพลง-5-แบบ)
5. [การใส่ Elements ไทย](#5-การใส่-elements-ไทย)
6. [Quality Boosters](#6-quality-boosters)
7. [แสงและโทนสี](#7-แสงและโทนสี)
8. [Style References](#8-style-references)
9. [Aspect Ratio และ Settings](#9-aspect-ratio-และ-settings)
10. [เคล็ดลับสำคัญ](#10-เคล็ดลับสำคัญ)

---

## 1. หลักพื้นฐานของ Prompt

### 🎯 Natural Language สำคัญกว่า Keywords

SeedDream 5 ใช้ **natural language ครบประโยค** ไม่ใช่ keyword list:

❌ **ผิด:**
```
young man, thai house, sunset, retro, vintage, film grain, warm tones, cinematic
```

✅ **ถูก:**
```
A young Thai man in his twenties sitting on the wooden porch of a traditional Thai house during golden hour, warm amber sunlight filtering through the trees, shot on Kodak Portra 400 with a 50mm lens, shallow depth of field creating beautiful bokeh in the background, 1970s Thai pop album aesthetic, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

### 🧠 Chain of Thought Reasoning

SeedDream ใช้ Chain of Thought reasoning ก่อน generate:

1. **วิเคราะห์ Subject** — ใคร? อะไร? ลักษณะอย่างไร?
2. **กำหนด Setting** — อยู่ที่ไหน? เวลาไหน? บรรยากาศแบบไหน?
3. **เลือก Camera/Lighting** — เลนส์อะไร? แสงแบบไหน? Film stock อะไร?
4. **เลือก Style** — ยุคไหน? Mood อย่างไร? Color palette อะไร?
5. **เพิ่ม Constraints** — ไม่ต้องการอะไร? Aspect ratio เท่าไหร่?

---

## 2. สูตร Prompt

### 📐 สูตรหลัก

```
[SUBJECT] + [SETTING] + [CAMERA/LIGHT] + [STYLE] + [CONSTRAINTS]
```

### 🔍 แต่ละส่วน

#### SUBJECT (ประธาน)
- ใคร หรือ อะไร เป็นจุดสนใจหลัก
- รายละเอียด: อายุ, เพศ, เสื้อผ้า, ท่าทาง, สีผิว

#### SETTING (สถานที่/บรรยากาศ)
- อยู่ที่ไหน
- เวลา: เช้า, กลางวัน, โพล้เพล้, กลางคืน
- สภาพอากาศ: แดด, เมฆ, ฝน, หมอก

#### CAMERA/LIGHT (กล้อง/แสง)
- Focal length: 35mm, 50mm, 85mm, wide angle
- Film stock: Kodak Portra, Fuji 400H, Kodak Gold
- Lighting: golden hour, soft diffused, rim light, natural light
- Depth of field: shallow, bokeh, deep focus

#### STYLE (สไตล์)
- ยุคสมัย: 70s, 80s, 90s, vintage, retro
- Mood: nostalgic, melancholic, romantic, energetic
- Aesthetic: film grain, warm tones, faded colors

#### CONSTRAINTS (ข้อจำกัด)
- no text, no words, no letters, no watermark
- Aspect ratio: 16:9
- Quality: highly detailed, cinematic

---

## 3. ภาษาทางภาพถ่าย

### 📷 Focal Length (ความยาวโฟกัส)

| Focal Length | การใช้งาน | ตัวอย่าง |
|--------------|----------|---------|
| **24mm / 28mm** | Wide angle, ฉากกว้าง | วิวเมือง, ธรรมชาติกว้าง |
| **35mm** | Street photography, documentary | คนในเมือง, ชีวิตประจำวัน |
| **50mm** | Standard, ใกล้เคียงตามนุษย์ | Portrait ทั่วไป, lifestyle |
| **85mm** | Portrait, background blur สวย | Close-up ใบหน้า |
| **135mm** | Portrait ระยะไกล, compression | Headshot, background blur มาก |

### 🎞️ Film Stock (ฟิล์ม)

#### Kodak Portra Series (Portrait, Skin Tone สวย)
```text
Kodak Portra 160 — ISO ต่ำ, grain น้อย, skin tone นุ่มนวล
Kodak Portra 400 — ISO ปานกลาง, versatile, warm tones
Kodak Portra 800 — ISO สูง, grain มากขึ้น, low light ดี
```

#### Fuji Series (Cool Tones, Contrast ดี)
```text
Fuji 400H — Cool tones, green/blue beautiful, skin tone ดี
Fuji Pro 400H — Version โปร, saturation ต่ำ, elegant
Fuji Velvia 50 — Saturation สูง, contrast สูง, landscape สวย
```

#### Kodak Gold/Chrome (Vintage, Pop)
```text
Kodak Gold 200 — Warm, nostalgic, everyday moments
Kodak Gold 400 — Versatile, warm amber tones
Kodak Ektar 100 — Saturation สูง, color vivid, modern
Kodak Chrome — Vintage 70s-80s aesthetic
```

### 💡 Lighting Setup (การจัดแสง)

#### Natural Light
```text
golden hour — แสงเช้าตรู่หรือเย็น, warm, soft, romantic
blue hour — หลังตะวันตกดินหรือก่อนขึ้น, cool blue tones, moody
midday sun — แสงเที่ยง, hard shadows, high contrast
overcast — วันเมฆ, soft diffused light, even lighting
```

#### Lighting Quality
```text
soft diffused — แสงนุ่ม, ไม่มีเงาแข็ง, flattering
hard light — แสงแข็ง, เงาชัดเจน, dramatic
rim light — แสงขอบ, แยก subject จาก background
backlit — แสงจากด้านหลัง, silhouette หรือ glow effect
side lighting — แสงด้านข้าง, texture, depth
```

### 🌊 Depth of Field (ความชัดลึก)

```text
shallow depth of field — พื้นหลังเบลอ, subject ชัด
bokeh — จุดแสงเบลอสวยๆ ในพื้นหลัง
deep depth of field — ชัดทั้งภาพ, landscape
background blur — พื้นหลังเบลอ (general term)
```

---

## 4. เทมเพลตสำหรับรูปปกเพลง 5 แบบ

### 🏠 แบบที่ 1: Retro Thai Scene

**แนวคิด:** ชายหนุ่ม + บ้านไม้ไทยเก่า + บรรยากาศย้อนยุค

#### Template Prompt:
```text
A [AGE] Thai man [POSTURE/ACTIVITY] [LOCATION] of a traditional Thai wooden house, [LIGHTING DESCRIPTION], shot on [FILM STOCK] with [LENS]mm lens, [DEPTH OF FIELD], [ERA] Thai pop album aesthetic, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

#### ตัวอย่างพร้อม Copy-Paste:

**ตัวอย่าง 1 — นั่งระเบียงบ้าน:**
```text
A young Thai man in his twenties sitting on the wooden porch of a traditional Thai house during golden hour, warm amber sunlight filtering through the trees, shot on Kodak Portra 400 with a 50mm lens, shallow depth of field creating beautiful bokeh in the background, 1970s Thai pop album aesthetic, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 2 — ยืนมองออกไป:**
```text
A handsome Thai man in vintage clothing standing at the edge of an old Thai wooden house, looking out into the distance, soft evening light with warm tones, shot on Fuji 400H with a 35mm lens, nostalgic 1980s Thai music video aesthetic, shallow depth of field, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 3 — นั่งเล่นกีตาร์:**
```text
A young Thai musician playing an acoustic guitar on the wooden steps of a traditional Thai house, surrounded by tropical plants, golden hour sunlight creating warm amber tones, shot on Kodak Gold 200 with a 50mm lens, 1970s Thai folk album cover aesthetic, soft bokeh in background, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

---

### 🏙️ แบบที่ 2: Urban Nostalgia

**แนวคิด:** ตึกเก่ากรุงเทพฯ + แสงตะวันตก + บรรยากาศเมือง

#### Template Prompt:
```text
A [SUBJECT] [LOCATION] in old Bangkok, [BUILDING DESCRIPTION], [TIME/LIGHTING], shot on [FILM STOCK] with [LENS]mm lens, [MOOD/STYLE], [ERA] urban photography aesthetic, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

#### ตัวอย่างพร้อม Copy-Paste:

**ตัวอย่าง 1 — ชายหนุ่มบนดาดฟ้า:**
```text
A young Thai man standing on a rooftop overlooking old Bangkok buildings at sunset, warm orange and amber light bathing the cityscape, vintage concrete buildings with balconies, shot on Kodak Portra 400 with a 35mm lens, 1980s Thai urban photography aesthetic, cinematic lens flare, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 2 — ยืนหน้าตึกเก่า:**
```text
A handsome Thai man in casual vintage clothing standing in front of an old 1970s Bangkok apartment building, golden hour sunlight casting warm amber tones on the weathered concrete facade, shot on Fuji 400H with a 50mm lens, nostalgic urban aesthetic, shallow depth of field, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 3 — มุมกว้างเมือง:**
```text
Old Bangkok streets at golden hour, vintage buildings and balconies bathed in warm amber sunset light, a lone figure walking in the distance, shot on Kodak Gold 200 with a 28mm wide angle lens, 1970s Thai cinema aesthetic, cinematic atmosphere, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

---

### 🌺 แบบที่ 3: Nature Metaphor

**แนวคิด:** ดอกไม้ + ทะเล + ฤดูกาล + ความหมายแฝง

#### Template Prompt:
```text
[SCENE DESCRIPTION] with [FLOWER/NATURE ELEMENT], [LOCATION/SETTING], [SEASON/ATMOSPHERE], [LIGHTING], shot on [FILM STOCK] with [LENS]mm lens, [MOOD], symbolic and poetic, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

#### ตัวอย่างพร้อม Copy-Paste:

**ตัวอย่าง 1 — ดอกไม้ริมทะเล:**
```text
A single white frangipani flower lying on sandy beach at sunset, gentle waves in the background, warm golden hour light creating a romantic and melancholic atmosphere, shot on Kodak Portra 400 with a 85mm lens, shallow depth of field, soft bokeh, symbolic of fleeting beauty, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 2 — ดอกไม้กับทะเล:**
```text
Fresh tropical flowers scattered on a wooden dock overlooking the ocean, soft morning mist, pastel amber and blue tones, shot on Fuji 400H with a 50mm lens, dreamy and nostalgic atmosphere, shallow depth of field with beautiful bokeh, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 3 — ฤดูกาลเปลี่ยน:**
```text
Fallen cherry blossoms floating on calm ocean water at dusk, soft purple and orange sky reflection, shot on Kodak Portra 160 with a 35mm lens, poetic and melancholic mood, shallow depth of field, symbolic of changing seasons and lost love, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

---

### 📸 แบบที่ 4: Intimate Portrait

**แนวคิด:** ใบหน้าใกล้ + อารมณ์ + ความรู้สึก

#### Template Prompt:
```text
Close-up portrait of a [AGE] Thai [GENDER] with [EXPRESSION], [HAIR/APPEARANCE], [LIGHTING], shot on [FILM STOCK] with [LENS]mm lens, [DEPTH OF FIELD], [MOOD/ATMOSPHERE], intimate and emotional, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

#### ตัวอย่างพร้อม Copy-Paste:

**ตัวอย่าง 1 — มองออกไป:**
```text
Close-up portrait of a young Thai man in his twenties with a contemplative expression, soft golden hour light illuminating one side of his face, natural skin texture visible, shot on Kodak Portra 400 with a 85mm lens, very shallow depth of field creating dreamy bokeh, nostalgic and melancholic mood, 1970s Thai pop album aesthetic, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 2 — ยิ้มบางๆ:**
```text
Intimate close-up of a handsome Thai man with a subtle smile, warm amber backlight creating a soft rim light effect, natural skin tones, shot on Fuji 400H with a 135mm lens, shallow depth of field, romantic and hopeful atmosphere, vintage film grain, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 3 — มองกล้อง:**
```text
Direct eye-level portrait of a young Thai man looking into the camera with a gentle expression, soft diffused natural light, visible skin texture and natural imperfections, shot on Kodak Portra 160 with a 50mm lens, intimate and vulnerable mood, 1980s Thai music photography aesthetic, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

---

### 🎬 แบบที่ 5: Cinematic Wide Scene

**แนวคิด:** ฉากกว้าง + Atmosphere + เรื่องราว

#### Template Prompt:
```text
Wide cinematic shot of [SCENE], [LOCATION], [TIME/WEATHER], [ATMOSPHERE DESCRIPTION], shot on [FILM STOCK] with [LENS]mm wide angle lens, [STYLE/ERA], [MOOD], no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

#### ตัวอย่างพร้อม Copy-Paste:

**ตัวอย่าง 1 — ถนนเก่า:**
```text
Wide cinematic shot of an old Bangkok street at golden hour, vintage buildings lining both sides, warm amber sunlight casting long shadows, a motorcycle parked on the side, shot on Kodak Gold 200 with a 24mm wide angle lens, 1970s Thai cinema aesthetic, nostalgic and atmospheric, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 2 — ทะเลตอนเย็น:**
```text
Wide shot of a tranquil Thai beach at sunset, orange and purple sky reflecting on calm water, a lone fishing boat in the distance, shot on Fuji 400H with a 28mm lens, peaceful and melancholic atmosphere, soft pastel tones, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

**ตัวอย่าง 3 — ทุ่งนา:**
```text
Wide cinematic landscape of golden rice fields in rural Thailand at golden hour, traditional wooden houses in the distance, warm amber sunlight, shot on Kodak Portra 400 with a 35mm lens, peaceful and nostalgic atmosphere, 1970s Thai documentary aesthetic, no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

---

## 5. การใส่ Elements ไทย

### 🏛️ สถาปัตยกรรมไทย

#### บ้านไม้ไทย
```text
traditional Thai wooden house — บ้านไม้ไทยทั่วไป
Thai wooden house on stilts — บ้านไม้ยกใต้ถุนสูง
old Thai teak house — บ้านไม้สักเก่า
Thai house with ornate gable — บ้านไทยมีgable ลวดลาย
weathered wooden porch — ระเบียงไม้เก่า
```

#### วัดและสถาปัตยกรรม
```text
Thai temple with golden spire — วัดไทยมีพระธาตุสีทอง
orange-roofed temple building — อาคารวัดหลังคากระเบื้องสีส้ม
Buddha statue silhouette — รูปปั้นพระพุทธรูปเงา
Thai-style pavilion — ลานไทย
```

### 🎎 วัฒนธรรมไทย

#### เครื่องแบบไทย
```text
Thai traditional pattern fabric — ผ้าลายไทย
mud cloth draped nearby — ผ้าหม้อดวางอยู่
vintage Thai clothing — เครื่องแต่งกายไทยย้อนยุค
```

#### วัตถุไทย
```text
acoustic guitar on wooden steps — กีตาร์โปร่งบนขั้นบันไดไม้
Thai ceramic bowl — ชามเซรามิกไทย
buddhist prayer beads — พวงมาลัยพระ
```

### 🌴 ธรรมชาติไทย

#### พืชพรรณ
```text
tropical plants — พืชเขตร้อน
frangipani flower — ดอกมะลิ
banana leaves — ใบกล้วย
bamboo grove — ไม้ไผ่
```

#### ภูมิทัศน์
```text
golden rice fields — ทุ่งนาสีทอง
Andaman Sea — ทะเลอันดามัน
tropical beach — ชายหาดเขตร้อน
```

---

## 6. Quality Boosters

### ✨ ข้อความมาตรฐานที่ควรใส่เสมอ

```text
no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

### 📋 อธิบายแต่ละส่วน

| ข้อความ | ความหมาย |
|---------|----------|
| `no text` | ไม่ให้มีตัวหนังสือ |
| `no words` | ไม่ให้มีคำ |
| `no letters` | ไม่ให้มีตัวอักษร |
| `no watermark` | ไม่ให้มีลายน้ำ |
| `16:9 cinematic` | อัตราส่วนภาพแบบภาพยนตร์ |
| `highly detailed` | รายละเอียดสูง |

### 🔥 Boosters เพิ่มเติม

```text
film grain — เกรนฟิล์ม
vintage film look — ลุคฟิล์มเก่า
retro color grading — สีแบบย้อนยุค
analog warmth — ความอบอุ่นแบบ analog
cinematic lens flare — แสงแฟลร์แบบภาพยนตร์
soft focus — โฟกัสนุ่ม
```

---

## 7. แสงและโทนสี

### 🌅 Lighting Types

#### Golden Hour
```text
golden hour — แสงเช้าหรือเย็น, warm, romantic
soft golden hour light — แสงโกลเด้นฮัวร์นุ่ม
warm golden hour sunlight — แสงแดดโกลเด้นฮัวร์อุ่น
```

#### Time of Day
```text
sunset — ตะวันตกดิน
sunrise — ตะวันขึ้น
evening light — แสงเย็น
morning light — แสงเช้า
blue hour — ชั่วโมงสีน้ำเงิน
```

#### Light Quality
```text
soft diffused light — แสงนุ่มกระจาย
warm amber tones — โทนสีแอมเบอร์อุ่น
natural light — แสงธรรมชาติ
backlight — แสงหลัง
rim light — แสงขอบ
```

### 🎨 Color Palettes

#### Warm/Nostalgic
```text
warm amber tones — โทนแอมเบอร์อุ่น
warm orange tones — โทนสีส้มอุ่น
vintage warm tones — โทนอุ่นแบบวินเทจ
```

#### Cool/Moody
```text
cool blue tones — โทนสีน้ำเงินเย็น
pastel blue and amber — แอมเบอร์และฟ้าพาสเทล
soft purple and orange — สีม่วงและส้มอ่อน
```

#### Cinematic
```text
teal and orange — เทียลและส้ม (cinematic classic)
pastel amber — แอมเบอร์พาสเทล
warm amber with cool shadows — แอมเบอร์อุ่นกับเงาเย็น
```

---

## 8. Style References

### 📺 Eras & Aesthetics

#### 1970s Aesthetic
```text
1970s Thai pop album aesthetic — aesthetic อัลบั้มป๊อปไทยยุค 70
1970s Thai cinema aesthetic — aesthetic ภาพยนตร์ไทยยุค 70
1970s Thai folk album cover aesthetic — aesthetic ปกอัลบั้มโฟล์คไทยยุค 70
```

#### 1980s Aesthetic
```text
1980s Thai urban photography aesthetic — aesthetic ภาพยนตร์เมืองไทยยุค 80
1980s Thai music video aesthetic — aesthetic MV ไทยยุค 80
1980s Thai music photography aesthetic — aesthetic ถ่ายรูปเพลงไทยยุค 80
```

### 🎞️ Film Styles

```text
vintage film grain — เกรนฟิล์มเก่า
retro color grading — สีแบบย้อนยุค
analog warmth — ความอบอุ่นแบบ analog
warm tones — โทนอุ่น
faded colors — สีซีด
soft focus — โฟกัสนุ่ม
```

---

## 9. Aspect Ratio และ Settings

### 📐 Aspect Ratio

#### สำหรับ YouTube/Album Cover:
```text
16:9 cinematic
```

#### อื่นๆ:
```text
1:1 square — สำหรับ Instagram, album art
9:16 vertical — สำหรับ TikTok, Reels, Stories
21:9 ultrawide — สำหรับ cinematic wallpaper
```

### ⚙️ Settings สำหรับ KIE API

#### Recommended Settings:
```json
{
  "output": "2K",
  "quality": "basic",
  "aspect_ratio": "16:9"
}
```

#### อธิบาย:
- **output: 2K** — ความละเอียดสูงเพียงพอสำหรับ YouTube thumbnail
- **quality: basic** — เพียงพอสำหรับ SeedDream 5, เร็วและประหยัด
- **aspect_ratio: 16:9** — อัตราส่วนภาพยนตร์

---

## 10. เคล็ดลับสำคัญ

### ✅ Do's

1. **ใช้ natural language ครบประโยค** — ไม่ใช่ keyword list
2. **ลำดับสำคัญ** — Subject → Setting → Camera/Light → Style → Constraints
3. **รายละเอียดสำคัญ** — อายุ, ท่าทาง, เสื้อผ้า, แสง, film stock
4. **ใส่ constraints เสมอ** — no text, no watermark, 16:9
5. **เลือก film stock ให้เหมาะกับ mood** — Portra สำหรับ skin tone, Fuji สำหรับ cool tones

### ❌ Don'ts

1. **อย่าใช้ keyword list** — SeedDream ต้องการประโยคสมบูรณ์
2. **อย่าใส่ negative prompts** — Model ฉลาดพอ, ไม่ต้องบอก "no ugly"
3. **อย่าลืม aspect ratio** — 16:9 สำคัญสำหรับ YouTube
4. **อย่าใช้ quality สูงเกินจำเป็น** — basic เพียงพอสำหรับ SeedDream 5

### 💡 Pro Tips

1. **Golden hour คือเพื่อน** — ให้ผลลัพธ์สวยงามเสมอ
2. **Kodak Portra 400 คือ universal choice** — ใช้ได้เกือบทุกสถานการณ์
3. **50mm และ 85mm คือ sweet spot** — สำหรับ portrait และ lifestyle
4. **Shallow depth of field เพิ่ม drama** — ทำให้ subject โดดเด่น
5. **Thai elements เพิ่มเอกลักษณ์** — บ้านไม้ไทย, วัด, ธรรมชาติไทย

---

## 📚 Quick Reference

### Prompt Structure Checklist:
- [ ] SUBJECT — ใคร? อะไร?
- [ ] SETTING — ที่ไหน? เวลาไหน?
- [ ] CAMERA/LIGHT — เลนส์? Film? แสง?
- [ ] STYLE — ยุค? Mood?
- [ ] CONSTRAINTS — no text, 16:9, etc.

### Essential Phrases:
```text
no text, no words, no letters, no watermark, 16:9 cinematic, highly detailed
```

### Film Stock Quick Guide:
- **Kodak Portra 400** — Portrait, skin tone, warm
- **Fuji 400H** — Cool tones, urban, moody
- **Kodak Gold 200** — Vintage, nostalgic, everyday
- **Kodak Ektar 100** — Vivid, saturated, modern

---

*คู่มือนี้สร้างสำหรับ Jaopao Music — ใช้ SeedDream 5 Lite ผ่าน KIE API* 
*อัปเดตล่าสุด: มีนาคม 2026*

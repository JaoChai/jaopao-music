#!/bin/bash
# Jaopao Music Factory — Automated Song Production Pipeline
# Usage: ./produce-song.sh "concept" "lyrics" "suno_style" "title" "title_en" "image_prompt" "seo_title" "seo_description"
set -e

CONCEPT="$1"
LYRICS="$2"
SUNO_STYLE="$3"
TITLE="$4"
TITLE_EN="$5"
IMAGE_PROMPT="$6"
SEO_TITLE="$7"
SEO_DESC="$8"

KIE_KEY="${KIE_API_KEY}"
ZERNIO_KEY="${ZERNIO_API_KEY}"
YOUTUBE_ACCOUNT="69b012a6dc8cab9432c8d81d"

echo "🎷 Starting production: $TITLE"

# --- Step 1: Generate Music via Suno ---
echo "📌 Step 1: Generating music via Suno V5..."
SUNO_RESP=$(curl -s -X POST "https://api.kie.ai/api/v1/generate" \
  -H "Authorization: Bearer $KIE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"$(echo "$LYRICS" | sed 's/"/\\"/g')\", \"customMode\": true, \"instrumental\": false, \"model\": \"V5\", \"style\": \"$(echo "$SUNO_STYLE" | sed 's/"/\\"/g')\", \"title\": \"$TITLE\", \"callBackUrl\": \"https://httpbin.org/post\"}")

SUNO_TASK=$(echo "$SUNO_RESP" | jq -r '.data.taskId // empty')
echo "   TaskID: $SUNO_TASK"

if [ -z "$SUNO_TASK" ]; then
  echo "❌ Suno failed: $SUNO_RESP"
  exit 1
fi

# Poll Suno
echo "   Waiting for Suno..."
for i in $(seq 1 20); do
  sleep 30
  SUNO_STATUS=$(curl -s "https://api.kie.ai/api/v1/generate/record-info?taskId=$SUNO_TASK" \
    -H "Authorization: Bearer $KIE_KEY")
  STATUS=$(echo "$SUNO_STATUS" | jq -r '.data.status // "PENDING"')
  echo "   Poll $i: $STATUS"
  if [ "$STATUS" = "SUCCESS" ]; then
    MUSIC_URL=$(echo "$SUNO_STATUS" | jq -r '.data.response.sunoData[0].audioUrl // empty')
    break
  fi
  if echo "$STATUS" | grep -q "FAILED\|ERROR"; then
    echo "❌ Suno failed: $STATUS"
    exit 1
  fi
done

if [ -z "$MUSIC_URL" ]; then
  echo "❌ Suno timeout"
  exit 1
fi
echo "✅ Music: $MUSIC_URL"

# --- Step 2: Generate Cover Image ---
echo "📌 Step 2: Generating cover image..."
IMG_RESP=$(curl -s -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Authorization: Bearer $KIE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"nano-banana-2\", \"task_type\": \"text-to-image\", \"input\": {\"prompt\": \"$(echo "$IMAGE_PROMPT" | sed 's/"/\\"/g')\", \"aspect_ratio\": \"16:9\"}}")

IMG_TASK=$(echo "$IMG_RESP" | jq -r '.data.taskId // empty')
echo "   TaskID: $IMG_TASK"

# Poll Image
echo "   Waiting for image..."
for i in $(seq 1 10); do
  sleep 15
  IMG_STATUS=$(curl -s "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=$IMG_TASK" \
    -H "Authorization: Bearer $KIE_KEY")
  STATE=$(echo "$IMG_STATUS" | jq -r '.data.state // "waiting"')
  echo "   Poll $i: $STATE"
  if [ "$STATE" = "success" ]; then
    IMAGE_URL=$(echo "$IMG_STATUS" | jq -r '.data.resultJson | if . != null then (if type == "string" then fromjson else . end).resultUrls[0] // empty else empty end')
    break
  fi
done

if [ -z "$IMAGE_URL" ]; then
  echo "❌ Image generation failed"
  exit 1
fi
echo "✅ Image: $IMAGE_URL"

# --- Step 3: FFmpeg combine ---
echo "📌 Step 3: FFmpeg combining..."
WORK_DIR="/tmp/jaopao_$(date +%s)"
mkdir -p "$WORK_DIR"
curl -s -o "$WORK_DIR/music.mp3" "$MUSIC_URL"
curl -s -o "$WORK_DIR/cover.jpg" "$IMAGE_URL"

ffmpeg -loop 1 -i "$WORK_DIR/cover.jpg" -i "$WORK_DIR/music.mp3" \
  -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
  -pix_fmt yuv420p -shortest -y "$WORK_DIR/output.mp4" 2>/dev/null

if [ ! -f "$WORK_DIR/output.mp4" ]; then
  echo "❌ FFmpeg failed"
  exit 1
fi
echo "✅ MP4: $WORK_DIR/output.mp4 ($(du -h "$WORK_DIR/output.mp4" | cut -f1))"

# --- Step 4: Upload to KIE ---
echo "📌 Step 4: Uploading to KIE..."
UPLOAD_RESP=$(curl -s -X POST "https://kieai.redpandaai.co/api/file-stream-upload" \
  -H "Authorization: Bearer $KIE_KEY" \
  -F "file=@$WORK_DIR/output.mp4" \
  -F "uploadPath=jaopao" \
  -F "fileName=${TITLE_EN}-$(date +%Y%m%d).mp4")

VIDEO_URL=$(echo "$UPLOAD_RESP" | jq -r '.data.downloadUrl // empty')

if [ -z "$VIDEO_URL" ]; then
  echo "❌ Upload failed: $UPLOAD_RESP"
  exit 1
fi
echo "✅ Public URL: $VIDEO_URL"

# --- Step 5: Post to YouTube via Zernio ---
echo "📌 Step 5: Posting to YouTube via Zernio..."
YT_JSON=$(python3 -c "
import json, sys
print(json.dumps({
    'content': sys.argv[1],
    'title': sys.argv[2],
    'mediaUrls': [sys.argv[3]],
    'platforms': [{'platform': 'youtube', 'accountId': sys.argv[4]}]
}))" "$SEO_DESC" "$SEO_TITLE" "$VIDEO_URL" "$YOUTUBE_ACCOUNT")

YT_RESP=$(curl -s -X POST "https://zernio.com/api/v1/posts" \
  -H "Authorization: Bearer $ZERNIO_KEY" \
  -H "Content-Type: application/json" \
  -d "$YT_JSON")

YT_STATUS=$(echo "$YT_RESP" | jq -r '.post.status // .error // "unknown"')
YT_POST_ID=$(echo "$YT_RESP" | jq -r '.post._id // empty')

echo "✅ YouTube post: $YT_STATUS (ID: $YT_POST_ID)"

# --- Cleanup ---
rm -rf "$WORK_DIR"

echo ""
echo "🎷🎉 Production complete!"
echo "Title: $TITLE"
echo "Music: $MUSIC_URL"
echo "Image: $IMAGE_URL"
echo "Video: $VIDEO_URL"
echo "YouTube Status: $YT_STATUS"

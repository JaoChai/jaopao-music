#!/usr/bin/env python3
"""
Music Analyst Pipeline — Fast deterministic version
Replaces LLM-driven sub-agent with pure CLI steps.

Usage:
  python3 music-analyst-pipeline.py [--analyze]

Options:
  --analyze   Run LLM trend analysis via Ollama (step 4)
  (default)   Steps 1-3 only (~5-10 seconds)

Output: JSON summary to stdout
"""

import json
import os
import sys
import subprocess
import urllib.request
import urllib.error

NEON_QUERY_SH = os.path.expanduser("~/code/jaopao-music/scripts/neon-query.sh")
SEND_TG_PY = os.path.expanduser("~/code/jaopao-music/scripts/send-telegram.py")
OLLAMA_URL = "http://192.168.1.199:11434"


def neon_query(sql: str) -> list[dict]:
    """Run SQL query against Neon DB."""
    result = subprocess.run(
        [NEON_QUERY_SH, sql],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"Neon query error: {result.stderr}", file=sys.stderr)
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def fetch_zernio_analytics() -> list[dict]:
    """Fetch all analytics from Zernio API (handles pagination)."""
    api_key = os.environ.get("ZERNIO_API_KEY", "")
    if not api_key:
        print("ERROR: ZERNIO_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    all_posts = []
    page = 1

    while True:
        url = (
            f"https://zernio.com/api/v1/analytics"
            f"?platform=youtube&account_id=69b012a6dc8cab9432c8d81d"
            f"&page={page}&limit=50"
        )
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {api_key}"
        })

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            print(f"Zernio API error: {e.code} {e.reason}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Zernio fetch error: {e}", file=sys.stderr)
            sys.exit(1)

        posts = data.get("posts", data.get("data", []))
        if not posts:
            break

        all_posts.extend(posts)
        page += 1

    return all_posts


def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return ""


def match_posts_to_songs(posts: list[dict], songs: list[dict]) -> dict:
    """Match Zernio posts to Neon DB songs by youtube_id."""
    yt_lookup = {}
    for s in songs:
        yid = s.get("youtube_id", "")
        if yid:
            yt_lookup[yid] = s

    matched = []
    unmatched = 0

    for post in posts:
        url = post.get("platformPostUrl", "")
        yt_id = extract_youtube_id(url)
        analytics = post.get("analytics", {})

        if yt_id and yt_id in yt_lookup:
            song = yt_lookup[yt_id]
            matched.append({
                "song_id": song["id"],
                "title": song["title"],
                "youtube_id": yt_id,
                "views": analytics.get("views", 0),
                "likes": analytics.get("likes", 0),
                "comments": analytics.get("comments", 0),
                "engagement_rate": analytics.get("engagementRate", 0),
                "url": url,
            })
        else:
            unmatched += 1

    return {"matched": matched, "unmatched_count": unmatched}


def insert_feedback(matches: list[dict]) -> tuple[int, int]:
    """Insert feedback into Neon DB using batch INSERT. Returns (success, failed)."""
    if not matches:
        return 0, 0

    # Build batch VALUES clause
    values_parts = []
    for m in matches:
        values_parts.append(
            f"({m['song_id']}, 1, {m['views']}, {m['likes']}, {m['comments']}, {m['engagement_rate']})"
        )

    sql = (
        f"INSERT INTO feedback (song_id, channel_id, views, likes, comments, engagement_rate) "
        f"VALUES {', '.join(values_parts)} RETURNING id"
    )

    result = subprocess.run(
        [NEON_QUERY_SH, sql],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode == 0:
        try:
            rows = json.loads(result.stdout)
            return len(rows), 0
        except json.JSONDecodeError:
            return 0, len(matches)
    else:
        print(f"Batch insert error: {result.stderr.strip()}", file=sys.stderr)
        return 0, len(matches)


def analyze_trends(matches: list[dict]) -> str:
    """Run LLM analysis via Ollama (fast, no thinking tokens)."""
    total_views = sum(m["views"] for m in matches)
    total_likes = sum(m["likes"] for m in matches)
    total_comments = sum(m["comments"] for m in matches)
    best = max(matches, key=lambda x: x["views"]) if matches else None

    summary = {
        "total_songs": len(matches),
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "best_song": best["title"] if best else None,
        "best_views": best["views"] if best else 0,
        "high_engagement": [m for m in matches if m["engagement_rate"] > 5],
    }

    prompt = (
        "คุณคือ music analyst วิเคราะห์ข้อมูลเพลง YouTube สั้นๆ ภาษาไทย กระชับ\n"
        f"ข้อมูล: {json.dumps(summary, ensure_ascii=False)}\n"
        "วิเคราะห์: 1) เพลงไหนดีสุด 2) trend ที่น่าสนใจ 3) แนะนำอะไร\n"
        "(ตอบสูงสุด 5 บรรทัด)"
    )

    payload = json.dumps({
        "model": "scb10x/typhoon2.1-gemma3-12b:latest",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"num_predict": 300, "temperature": 0.3},
    }).encode()

    try:
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            return data.get("message", {}).get("content", "(no response)")
    except Exception as e:
        return f"Analysis error: {e}"


def main():
    do_analyze = "--analyze" in sys.argv

    # Step 1: Fetch Zernio
    print("=== Step 1: Fetching Zernio Analytics ===", file=sys.stderr)
    posts = fetch_zernio_analytics()
    print(f"Fetched {len(posts)} posts", file=sys.stderr)

    if not posts:
        json.dump({"status": "ok", "posts": 0, "message": "No posts found"}, sys.stdout)
        return

    # Step 2: Match with Neon
    print("=== Step 2: Matching with Neon DB ===", file=sys.stderr)
    songs = neon_query("SELECT id, title, youtube_id FROM songs WHERE youtube_id IS NOT NULL")
    print(f"Found {len(songs)} songs in Neon", file=sys.stderr)

    match_result = match_posts_to_songs(posts, songs)
    matches = match_result["matched"]
    print(f"Matched {len(matches)} songs", file=sys.stderr)

    # Step 3: Insert feedback
    print("=== Step 3: Inserting feedback ===", file=sys.stderr)
    inserted, failed = insert_feedback(matches)
    print(f"Inserted: {inserted}, Failed: {failed}", file=sys.stderr)

    # Step 4: Optional analysis
    analysis = None
    if do_analyze and matches:
        print("=== Step 4: LLM Analysis ===", file=sys.stderr)
        analysis = analyze_trends(matches)
        print(f"Analysis: {analysis}", file=sys.stderr)

    # Output summary
    total_views = sum(m["views"] for m in matches)
    total_likes = sum(m["likes"] for m in matches)
    total_comments = sum(m["comments"] for m in matches)
    best = max(matches, key=lambda x: x["views"]) if matches else None

    output = {
        "status": "ok",
        "posts_fetched": len(posts),
        "matched": len(matches),
        "unmatched": match_result["unmatched_count"],
        "inserted": inserted,
        "failed": failed,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "best_song": best["title"] if best else None,
        "best_views": best["views"] if best else 0,
        "analysis": analysis,
    }

    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

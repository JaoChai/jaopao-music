#!/usr/bin/env python3
"""Trend Research — ดึง trending เพลงไทย + วิเคราะห์ concept pattern"""

# ทำ 3 สิ่ง:
# 1. Search trending Thai songs จาก YouTube Data API (ใช้ web scraping ผ่าน web search)
# 2. Search trending Thai music topics จาก TikTok/Twitter
# 3. สรุป concept patterns ที่กำลัง trending

# Output: JSON ไป stdout
# {
#   "trending_topics": ["ความรักวัยเฒ่า", "ขอแฟนกลับ", ...],
#   "trending_moods": ["melancholic", "hopeful", ...],
#   "trending_themes": ["รักที่ไม่สมหวัง", "คิดถึงคนเก่า", ...],
#   "popular_titles_pattern": "สั้น 2-4 คำ, ใช้คำอารมณ์",
#   "source_count": 5,
#   "collected_at": "2026-03-30"
# }

# Implementation:
# - ใช้ urllib.request เท่านั้น (ไม่ต้องติดตั้ง library พิเศษ)
# - Search ผ่าน DuckDuckGo HTML: https://html.duckduckgo.com/html/?q=เพลงไทย+trending+2026
# - Parse HTML ดึง titles ที่เกี่ยวข้อง
# - วิเคราะห์ keyword frequency
# - สรุป mood + theme ที่พบบ่อย

import json
import sys
import re
import urllib.request
import urllib.parse

def search_duckduckgo(query, max_results=10):
    """Search DuckDuckGo HTML and extract titles/snippets"""
    encoded = urllib.parse.urlencode({"q": query})
    url = f"https://html.duckduckgo.com/html/?{encoded}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[trend] DDG error: {e}", file=sys.stderr)
        return []
    
    # Extract result titles and snippets
    results = []
    # Simple regex parsing for DDG HTML results
    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</.*?>', html, re.DOTALL)
    
    for i, title in enumerate(titles[:max_results]):
        clean = re.sub(r'<[^>]+>', '', title).strip()
        snippet = ""
        if i < len(snippets):
            snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
        if clean:
            results.append({"title": clean, "snippet": snippet})
    
    return results

def analyze_themes(results):
    """Analyze trending themes from search results"""
    # Thai keywords to look for
    mood_keywords = {
        "รัก": "romantic", "คิดถึง": "nostalgic", "เศร้า": "melancholic",
        "หัวใจ": "romantic", "อกหัก": "heartbreak", "เหงา": "lonely",
        "ฝัน": "dreamy", "ไกล": "longing", "รอ": "waiting",
        "จำ": "remembering", "บอกรัก": "confession", "ขอโทษ": "apology",
        "หลับตา": "intimate", "กอด": "intimate", "ยิ้ม": "hopeful",
        "เพลงรัก": "romantic", "เพลงเศร้า": "melancholic",
        "ความทรงจำ": "nostalgic", "วันเก่า": "nostalgic",
        "แฟนเก่า": "nostalgic", "คนเดิม": "nostalgic"
    }
    
    theme_counts = {}
    mood_counts = {}
    
    for r in results:
        text = (r["title"] + " " + r["snippet"]).lower()
        for kw, mood in mood_keywords.items():
            if kw in text:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    # Also extract Thai theme phrases
    for r in results:
        text = r["title"]
        # Common Thai song title patterns
        themes = re.findall(r'เพลง (.*?)(?:\||$)', text)
        for t in themes:
            t = t.strip()[:50]
            if t and len(t) > 2:
                theme_counts[t] = theme_counts.get(t, 0) + 1
    
    return {
        "moods": dict(sorted(mood_counts.items(), key=lambda x: -x[1])[:5]),
        "themes": dict(sorted(theme_counts.items(), key=lambda x: -x[1])[:10])
    }

def main():
    queries = [
        "เพลงไทยยอดนิยม 2026",
        "เพลงไทย trending เพลงรัก",
        "เพลงไทยอกหัก เพลงเศร้า 2026",
        "TikTok เพลงไทย viral 2026",
    ]
    
    all_results = []
    for q in queries:
        results = search_duckduckgo(q, max_results=8)
        all_results.extend(results)
        print(f"[trend] '{q}': {len(results)} results", file=sys.stderr)
    
    # Remove duplicates
    seen = set()
    unique = []
    for r in all_results:
        if r["title"] not in seen:
            seen.add(r["title"])
            unique.append(r)
    
    analysis = analyze_themes(unique)
    
    # Build output
    trending_themes = []
    for theme, count in list(analysis["themes"].items())[:5]:
        trending_themes.append(theme)
    
    # Extract title patterns
    titles_only = [r["title"] for r in unique]
    
    output = {
        "trending_topics": trending_themes,
        "trending_moods": list(analysis["moods"].keys()),
        "trending_themes": trending_themes[:3] if trending_themes else ["ความรัก", "ความทรงจำ"],
        "popular_titles": titles_only[:10],
        "source_count": len(unique),
        "collected_at": ""
    }
    
    # Set timestamp
    from datetime import datetime
    output["collected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

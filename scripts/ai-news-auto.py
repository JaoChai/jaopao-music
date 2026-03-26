#!/usr/bin/env python3
"""AI News Auto — RSS ดึงข่าวจริง + Spark สรุปไทย + Script ควบคุม format + ส่ง Telegram"""

import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

OLLAMA_URL = "http://192.168.1.199:11434"
MODEL = "qwen3.5:27b"
BOT_TOKEN = "8376969560:AAH2rJtldj8fpLaByB20znOghQAPLgiHUPw"
GROUP_CHAT_ID = -5240777332
SENT_FILE = "/Users/jaochai/.openclaw/workspace-ainews/memory/sent-news.md"
LOG_FILE = "/tmp/ai-news-auto.log"

RSS_FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("Ars Technica AI", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
]

AI_KEYWORDS = ["ai", "artificial intelligence", "llm", "gpt", "claude", "gemini",
               "openai", "anthropic", "machine learning", "neural", "model", "agent",
               "deep learning", "chatbot", "copilot"]


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)


def fetch_rss(name, url):
    """Fetch RSS and return articles with title, link, desc, pubdate."""
    articles = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        root = ET.fromstring(resp.read())

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item") or root.findall(".//atom:entry", ns)

        now = datetime.now(timezone.utc)

        for item in items[:10]:
            title = item.findtext("title") or item.findtext("atom:title", namespaces=ns) or ""
            link = item.findtext("link") or ""
            if not link:
                link_el = item.find("atom:link", ns)
                if link_el is not None:
                    link = link_el.get("href", "")

            desc_raw = item.findtext("description") or item.findtext("atom:summary", namespaces=ns) or ""
            desc = re.sub(r'<[^>]+>', '', desc_raw).strip()[:300]

            # Parse publish date
            pub_str = item.findtext("pubDate") or item.findtext("atom:published", namespaces=ns) or ""
            is_recent = True  # default if can't parse
            if pub_str:
                try:
                    from email.utils import parsedate_to_datetime
                    pub_date = parsedate_to_datetime(pub_str)
                    age = now - pub_date
                    is_recent = age.total_seconds() < 86400  # 24 hours
                except:
                    pass

            # Filter: AI-related + recent
            text = (title + " " + desc).lower()
            is_ai = any(kw in text for kw in AI_KEYWORDS)

            if is_ai and is_recent:
                articles.append({
                    "title": title.strip(),
                    "link": link.strip(),
                    "source": name,
                    "desc": desc,
                })
    except Exception as e:
        log(f"RSS error ({name}): {e}")
    return articles


def spark_summarize_thai(title, desc):
    """Ask Spark to summarize in Thai. Returns (summary, benefit)."""
    payload = json.dumps({
        "model": MODEL,
        "stream": False,
        "think": False,
        "options": {"num_ctx": 4096, "num_predict": 300},
        "messages": [
            {"role": "system", "content": "สรุปข่าวเป็นภาษาไทย สั้นกระชับ 3 ประโยค แล้วบอกประโยชน์ 1 ประโยค คั่นด้วย ||| เช่น: สรุปข่าว|||ประโยชน์"},
            {"role": "user", "content": f"สรุปข่าวนี้: {title}. {desc}"},
        ],
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = json.loads(resp.read())
        content = data.get("message", {}).get("content", "")

        if not content:
            return "", ""

        # Split by ||| if present
        if "|||" in content:
            parts = content.split("|||", 1)
            return parts[0].strip(), parts[1].strip()

        # Otherwise split by last line
        lines = [l.strip() for l in content.strip().split("\n") if l.strip()]
        if len(lines) >= 2:
            return "\n".join(lines[:-1]), lines[-1]

        return content.strip(), "ติดตามข่าว AI เพื่อไม่ให้ตกเทรนด์"
    except Exception as e:
        log(f"Spark error: {e}")
        return "", ""


def send_telegram(text):
    """Send message to Telegram group."""
    payload = json.dumps({"chat_id": GROUP_CHAT_ID, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read()).get("ok", False)
    except Exception as e:
        log(f"Telegram error: {e}")
        return False


def get_sent_titles():
    titles = set()
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r") as f:
            for line in f:
                if line.startswith("- "):
                    titles.add(line.split("|")[0].strip("- ").strip())
    return titles


def save_sent(title, source):
    with open(SENT_FILE, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"- {title} | {source} | {ts}\n")


def spark_deep_analyze(title, url):
    """Phase 3: Analyze — Spark อ่าน full article แล้ววิเคราะห์ลึก."""
    # ดึง full article ผ่าน URL
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8", errors="ignore")
        # Strip HTML tags → plain text
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text).strip()[:2000]  # จำกัด 2000 chars
    except:
        text = ""

    if not text:
        return ""

    payload = json.dumps({
        "model": MODEL,
        "stream": False,
        "think": False,
        "options": {"num_ctx": 4096, "num_predict": 200},
        "messages": [
            {"role": "system", "content": "วิเคราะห์ข่าวนี้เป็นภาษาไทย สั้น 2 ประโยค บอกว่าทำไมข่าวนี้สำคัญ"},
            {"role": "user", "content": f"วิเคราะห์: {title}\n\nเนื้อหา: {text[:1000]}"},
        ],
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = json.loads(resp.read())
        return data.get("message", {}).get("content", "").strip()
    except:
        return ""


def learn_trends():
    """Phase 7: Learn — วิเคราะห์ trend จากข่าวที่ส่งไปแล้ว."""
    TRENDS_FILE = os.path.join(os.path.dirname(SENT_FILE), "ai-trends.md")

    if not os.path.exists(SENT_FILE):
        return

    # นับ keywords จากข่าวที่ส่งไป
    keywords_count = {}
    with open(SENT_FILE, "r") as f:
        for line in f:
            if not line.startswith("- "):
                continue
            title = line.split("|")[0].strip("- ").strip().lower()
            for kw in AI_KEYWORDS + ["openai", "google", "meta", "anthropic", "nvidia", "apple", "microsoft"]:
                if kw in title:
                    keywords_count[kw] = keywords_count.get(kw, 0) + 1

    if not keywords_count:
        return

    # เรียงตาม count
    sorted_kw = sorted(keywords_count.items(), key=lambda x: x[1], reverse=True)[:10]

    # เขียน trends file
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(TRENDS_FILE, "w") as f:
        f.write(f"# AI Trends (อัพเดท {ts})\n\n")
        f.write("## Keywords ที่เจอบ่อย:\n")
        for kw, count in sorted_kw:
            f.write(f"- {kw}: {count} ครั้ง\n")
        f.write(f"\n## สรุป:\n")
        if sorted_kw:
            top3 = ", ".join([kw for kw, _ in sorted_kw[:3]])
            f.write(f"หัวข้อที่ hot ที่สุดตอนนี้: {top3}\n")

    log(f"Trends updated: top keywords = {', '.join([f'{kw}({c})' for kw, c in sorted_kw[:5]])}")


def main():
    log("Starting AI News Auto (with Analyze + Learn)...")

    # Phase 1: Search — RSS ดึงข่าวจริง
    all_articles = []
    for name, url in RSS_FEEDS:
        articles = fetch_rss(name, url)
        all_articles.extend(articles)
        log(f"RSS {name}: {len(articles)} new AI articles (24h)")

    if not all_articles:
        log("No new AI articles")
        return

    # Phase 2: Filter — กรอง duplicates
    sent_titles = get_sent_titles()
    new_articles = [a for a in all_articles if a["title"] not in sent_titles]
    log(f"New: {len(new_articles)} (filtered {len(all_articles) - len(new_articles)} duplicates)")

    if not new_articles:
        log("No new articles to send")
        # Phase 7: Learn — วิเคราะห์ trend แม้ไม่มีข่าวใหม่
        learn_trends()
        return

    # Phase 3-5: Analyze + Summarize + Deliver (max 2)
    sent_count = 0
    for article in new_articles[:2]:
        title = article["title"]

        # Phase 3: Analyze — deep dive (ถ้า desc สั้นเกิน)
        extra_analysis = ""
        if len(article["desc"]) < 100:
            log(f"Deep analyzing: {title}")
            extra_analysis = spark_deep_analyze(title, article["link"])

        # Phase 4: Summarize — Spark สรุปไทย
        log(f"Summarizing: {title}")
        desc_for_spark = article["desc"]
        if extra_analysis:
            desc_for_spark = f"{article['desc']} {extra_analysis}"

        summary, benefit = spark_summarize_thai(title, desc_for_spark)

        if not summary:
            log(f"Spark failed, using fallback")
            summary = article["desc"][:200] if article["desc"] else title
            benefit = "ติดตามข่าว AI เพื่อไม่ให้ตกเทรนด์"

        # Phase 5: Deliver — Script ควบคุม format 100%
        msg = f"""🤖 AI News Alert!

📰 {title}
🔗 {article['link']}

📝 สรุป:
{summary}

💡 ประโยชน์:
{benefit}"""

        if send_telegram(msg):
            log(f"Sent: {title}")
            # Phase 6: Remember
            save_sent(title, article["source"])
            sent_count += 1

    # Phase 7: Learn — วิเคราะห์ trend
    learn_trends()

    log(f"Done. Sent {sent_count} news.")


if __name__ == "__main__":
    main()

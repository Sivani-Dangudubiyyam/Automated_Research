import streamlit as st
from transformers import pipeline
import requests
from newspaper import Article
from readability import Document
import feedparser
from urllib.parse import urlparse
import sqlite3
import hashlib
import time
from datetime import datetime
import pandas as pd
import re
import math

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"
DB_PATH = "ai_research_tool.db"

st.set_page_config(page_title="AI Research Tool", layout="wide")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS research (
        id TEXT PRIMARY KEY,
        url TEXT,
        title TEXT,
        content TEXT,
        summary TEXT,
        key_points TEXT,
        fetched_at TEXT
    )
    """)
    conn.commit()
    return conn


def url_to_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def fetch_article_text(url: str, timeout=15) -> (str, str):
    url = url.strip()
    if url.endswith('%20'):
        url = url[:-3]  # remove trailing encoded space

    if not url.startswith('http'):
        raise RuntimeError("Invalid URL. Make sure it starts with http or https.")

    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        content_type = resp.headers.get('content-type', '').lower()

        # Handle RSS/XML feeds using feedparser
        if 'xml' in content_type or 'rss' in content_type or url.endswith('.xml'):
            feed = feedparser.parse(url)
            if feed.entries:
                title = feed.feed.get('title', 'RSS Feed')
                entries = [f"{e.title}: {e.summary}" for e in feed.entries[:5] if hasattr(e, 'title') and hasattr(e, 'summary')]
                text = "\n\n".join(entries)
                return title.strip(), text.strip()
            else:
                raise RuntimeError("RSS feed found but contains no entries.")

    except Exception as e:
        raise RuntimeError(f"Could not fetch the URL: {e}")

    try:
        a = Article(url)
        a.download()
        a.parse()
        text = a.text
        title = a.title or ""
        if text and len(text) > 50:
            return title.strip(), text.strip()
    except Exception:
        pass

    try:
        doc = Document(resp.text)
        title = doc.title() or ""
        summary_html = doc.summary()
        text = re.sub(r'<[^>]+>', '', summary_html)
        if text and len(text) > 50:
            return title.strip(), text.strip()
    except Exception as e:
        raise RuntimeError(f"Could not parse article: {e}")

    raise RuntimeError("Failed to extract article text. The URL may not contain readable content.")


def chunk_text(text: str, max_chunk_chars=3500):
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if len(current) + len(p) + 1 <= max_chunk_chars:
            current = current + "\n" + p if current else p
        else:
            if current:
                chunks.append(current)
            if len(p) > max_chunk_chars:
                for i in range(0, len(p), max_chunk_chars):
                    chunks.append(p[i:i+max_chunk_chars])
                current = ""
            else:
                current = p
    if current:
        chunks.append(current)
    return chunks


def generate_summary(summarizer, text: str) -> (str, list):
    chunks = chunk_text(text)
    summaries = []
    for c in chunks:
        try:
            out = summarizer(c, max_length=130, min_length=30, do_sample=False)
            if isinstance(out, list) and out:
                summaries.append(out[0]['summary_text'])
            elif isinstance(out, dict) and 'summary_text' in out:
                summaries.append(out['summary_text'])
        except Exception:
            summaries.append(c[:800])

    combined = "\n".join(summaries)
    if len(combined) > 1500:
        try:
            final = summarizer(combined, max_length=200, min_length=60, do_sample=False)
            final_text = final[0]['summary_text'] if isinstance(final, list) else final['summary_text']
        except Exception:
            final_text = combined
    else:
        final_text = combined

    sentences = re.split(r'(?<=[\.\!\?])\s+', final_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    key_points = sentences[:6]
    return final_text.strip(), key_points


conn = init_db()
cur = conn.cursor()

@st.cache_resource(show_spinner=False)
def get_summarizer():
    return pipeline("summarization", model=MODEL_NAME, device=-1)

summarizer = get_summarizer()

st.title("🧠 AI Research Tool")
st.markdown("Enter a valid article or RSS feed URL. RSS feeds will show summaries of top entries.")

col1, col2 = st.columns([2, 1])
with col1:
    url_input = st.text_input("URL to research", placeholder="https://example.com/article...", key="url_input")
    fetch_button = st.button("Fetch & Summarize")

with col2:
    st.markdown("**Options**")
    st.write(f"Model: `{MODEL_NAME}`")
    show_history = st.checkbox("Show history", value=True)
    export_button = st.button("Export history to CSV")

if fetch_button and url_input:
    with st.spinner("Fetching article..."):
        try:
            title, content = fetch_article_text(url_input)
        except Exception as e:
            st.error(f"Failed to fetch article: {e}")
            st.stop()

    st.success("Fetched article")
    with st.expander("Article preview"):
        st.subheader(title or "(no title found)")
        st.write(content[:10000])

    with st.spinner("Summarizing (this may take a few seconds)..."):
        try:
            summary, key_points = generate_summary(summarizer, content)
        except Exception as e:
            st.error(f"Summarization failed: {e}")
            summary, key_points = content[:1000], []

    st.subheader("Summary")
    st.write(summary)

    st.subheader("Key points")
    for i, kp in enumerate(key_points, 1):
        st.markdown(f"{i}. {kp}")

    rec_id = url_to_id(url_input)
    now = datetime.utcnow().isoformat() + "Z"
    cur.execute("INSERT OR REPLACE INTO research (id, url, title, content, summary, key_points, fetched_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (rec_id, url_input, title, content, summary, '\n'.join(key_points), now))
    conn.commit()
    st.success("Saved to local history")

if show_history:
    st.markdown("---")
    st.header("History")
    df = pd.read_sql_query("SELECT id, url, title, summary, key_points, fetched_at FROM research ORDER BY fetched_at DESC", conn)
    if df.empty:
        st.info("No saved items yet. Fetch a URL to get started.")
    else:
        st.dataframe(df[['fetched_at', 'title', 'url']].rename(columns={'fetched_at':'Fetched at','title':'Title','url':'URL'}))
        sel = st.text_input("Open by ID or URL", key='open_id')
        open_button = st.button("Open")
        if open_button and sel:
            if sel.startswith('http'):
                qid = url_to_id(sel)
            else:
                qid = sel.strip()
            res = cur.execute("SELECT url, title, content, summary, key_points, fetched_at FROM research WHERE id=?", (qid,)).fetchone()
            if res:
                url, title, content, summary, key_points, fetched_at = res
                st.subheader(title or url)
                st.write(f"Saved at: {fetched_at}")
                with st.expander("Full content"):
                    st.write(content)
                st.subheader("Summary (saved)")
                st.write(summary)
                st.subheader("Key points (saved)")
                for k in (key_points or "").split('\n'):
                    if k.strip():
                        st.markdown(f"- {k}")
            else:
                st.error("No record found for that ID/URL")

if export_button:
    df_all = pd.read_sql_query("SELECT url, title, summary, key_points, fetched_at FROM research ORDER BY fetched_at DESC", conn)
    if df_all.empty:
        st.warning("No history to export")
    else:
        csv = df_all.to_csv(index=False)
        st.download_button("Download CSV", data=csv, file_name="ai_research_history.csv", mime='text/csv')

st.markdown("---")
st.markdown("**Tips:** Provide article or RSS feed URLs. The tool supports summarizing top entries from RSS feeds like arXiv.")

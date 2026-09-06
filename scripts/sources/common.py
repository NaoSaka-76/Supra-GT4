"""Supra GT4 Watch ダッシュボード用の共通ヘルパー。

公式APIキー(YouTube Data API / X API / Facebook Graph API)を使わずに、
Google News RSS・YouTube検索ページの軽量スクレイピングで代替データを収集する。
取得元は無料公開エンドポイントのみで、構造変化やレート制限により結果が空になる
場合がある。
"""

from __future__ import annotations

import random
import re
import time
import urllib.parse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests

USER_AGENT = "Mozilla/5.0 (compatible; SupraGT4WatchBot/1.0; +https://github.com/NaoSaka-76/Supra-GT4)"

REQUEST_TIMEOUT = 15

# 一時的なサーバー側エラー。Google News RSS は混雑時に 429/503 を返すことがあり、
# 数秒待って再試行すると成功することが多い。
_TRANSIENT_STATUS = {429, 500, 502, 503, 504}
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 2.0  # 秒(指数バックオフの基準)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def _get_with_retry(session: requests.Session, url: str) -> requests.Response:
    """一時的なエラー(429/5xx・接続エラー)を指数バックオフで再試行しながら GET する。"""
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code in _TRANSIENT_STATUS and attempt < _MAX_RETRIES:
                last_exc = requests.HTTPError(f"{resp.status_code} {resp.reason}", response=resp)
            else:
                resp.raise_for_status()
                return resp
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            if attempt >= _MAX_RETRIES:
                raise
        time.sleep(_RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 1))
    raise last_exc if last_exc else RuntimeError("request failed")


def fetch_google_news_rss(query: str, hl: str = "en-US", gl: str = "US", ceid: str = "US:en", limit: int = 10) -> list[dict]:
    """Google News RSS検索。APIキー不要の公開フィード。"""
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl={hl}&gl={gl}&ceid={ceid}"
    items: list[dict] = []
    try:
        resp = _get_with_retry(_session(), url)
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:limit]:
            source = ""
            if hasattr(entry, "source") and hasattr(entry.source, "title"):
                source = entry.source.title
            items.append(
                {
                    "title": entry.get("title", "").strip(),
                    "url": entry.get("link", ""),
                    "source": source or "Google News",
                    "published": entry.get("published", ""),
                }
            )
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] Google News RSS 取得失敗（再試行後）: {query!r} -> {exc}")
    return items


def dedupe_by_url(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for item in items:
        key = item.get("url") or item.get("title")
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def sort_by_recency(items: list[dict]) -> list[dict]:
    """"published"(RFC822形式)を新しい順に並べ替える。解析できないものは末尾に回す。"""

    def _key(item: dict) -> datetime:
        raw = item.get("published", "")
        if not raw:
            return datetime.min.replace(tzinfo=timezone.utc)
        try:
            dt = parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            return datetime.min.replace(tzinfo=timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    return sorted(items, key=_key, reverse=True)


_VIEW_MULTIPLIERS = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}


def parse_view_count(text: str) -> int:
    """'1.2M回視聴' や '45K views' のようなテキストを数値に変換する。"""
    if not text:
        return 0
    match = re.search(r"([\d,.]+)\s*([kKmMbB]?)", text.replace(",", ""))
    if not match:
        return 0
    number_str, suffix = match.group(1), match.group(2).lower()
    try:
        number = float(number_str)
    except ValueError:
        return 0
    return int(number * _VIEW_MULTIPLIERS.get(suffix, 1))


_RELATIVE_UNITS = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
    "day": 86400,
    "week": 604800,
    "month": 2629800,
    "year": 31557600,
}


_RELATIVE_UNITS_JP = [
    ("秒", 1),
    ("分", 60),
    ("時間", 3600),
    ("週間", 604800),
    ("ヶ月", 2629800),
    ("か月", 2629800),
    ("カ月", 2629800),
    ("日", 86400),
    ("月", 2629800),
    ("年", 31557600),
]


def parse_relative_seconds_ago(text: str) -> int:
    """'3 hours ago' や '4時間前' のような相対時刻テキストを秒数に変換する(新しいほど小さい値)。"""
    if not text:
        return 10**12

    match = re.search(r"(\d+)\s*(second|minute|hour|day|week|month|year)", text.lower())
    if match:
        value, unit = int(match.group(1)), match.group(2)
        return value * _RELATIVE_UNITS.get(unit, 10**9)

    # 日本語表記(例: "4時間前", "13日前", "11か月前")。単位は長いものから順に照合する。
    for unit, seconds in _RELATIVE_UNITS_JP:
        jp_match = re.search(rf"(\d+)\s*{unit}", text)
        if jp_match:
            return int(jp_match.group(1)) * seconds

    return 10**12

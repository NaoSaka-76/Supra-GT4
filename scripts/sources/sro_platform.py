"""SRO Motorsports Group系列(共通CMS)の複数サイトから実データを取得する汎用ヘルパー。

tcamerica.us / gt4-america.com / gt4series.com / gt4australia.com.au /
gt-world-challenge-asia.com / gt-world-challenge-america.com 等は、いずれも
同一プラットフォーム上で運用されており、以下の構造を共通で持つ:

- 順位表ページ: `filter_season_id` / `filter_standing_type` の<select>で
  シーズン/クラスを動的に選択でき、順位表は `<table class="table standing...">`
  という静的HTMLテーブルで提供される。
- カレンダーページ: `calendar__list-item`(開催予定)と `past-events__list-item`
  (開催済み)のブロックが並び、各ブロックに `calendar__date-number` /
  `calendar__date-month` / `calendar__date-year` の3つ組が開始日・終了日の分
  繰り返される。

一度どれか1サイトでパターンを検証できれば、同じ主催者(SRO)の他サイトにも
ほぼそのまま使い回せる。個別サイトの差異(クラス名の候補文字列、既定の
standing_type等)だけを呼び出し側で指定する。
"""

from __future__ import annotations

import html as html_module
import re
from datetime import date, datetime, timezone, timedelta

import requests

from .common import REQUEST_TIMEOUT, USER_AGENT

JST = timezone(timedelta(hours=9))

_MONTH_NUM = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def _month_num(text: str) -> int:
    return _MONTH_NUM.get(text.strip()[:3].upper(), 0)


def _status(sort_key: int) -> str:
    today_key = date.today().year * 10000 + date.today().month * 100 + date.today().day
    return "upcoming" if sort_key >= today_key else "completed"


def _extract_select_options(html_text: str, select_name: str) -> list[tuple[str, str]]:
    block = re.search(rf'<select[^>]*name="{select_name}"[^>]*>(.*?)</select>', html_text, re.S)
    if not block:
        return []
    options = re.findall(r'<option\s+value="([^"]*)"[^>]*>([^<]*)</option>', block.group(1))
    return [(value, html_module.unescape(label.strip())) for value, label in options]


def fetch_standings(
    standings_url: str,
    standing_type_match: str,
    limit: int = 15,
    year: int | None = None,
) -> dict:
    """順位表ページから {position, name, points} のリストを実データで取得する。

    standing_type_match: filter_standing_typeの<option>ラベルに含まれる部分文字列
    (例: "Silver Teams"、"GT3 Teams Championship")。完全一致ではなく部分一致で
    最初にマッチしたクラスを採用する。
    """
    session = _session()
    year = year or datetime.now(JST).year
    try:
        base_resp = session.get(standings_url, timeout=REQUEST_TIMEOUT)
        base_resp.raise_for_status()
        base_html = base_resp.text

        season_id = None
        for value, label in _extract_select_options(base_html, "filter_season_id"):
            if str(year) in label:
                season_id = value
                break

        standing_type_id = None
        for value, label in _extract_select_options(base_html, "filter_standing_type"):
            if standing_type_match.lower() in label.lower():
                standing_type_id = value
                break

        if not season_id or not standing_type_id:
            return {"standings": [], "error": "対象シーズン/クラスを公式サイト上で特定できませんでした"}

        resp = session.get(
            standings_url,
            params={"filter_standing_type": standing_type_id, "filter_season_id": season_id},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        html_text = resp.text

        table_m = re.search(r'<table class="table standing[^"]*">.*?</table>', html_text, re.S)
        rows: list[dict] = []
        if table_m:
            trs = re.findall(r"<tr[^>]*>(.*?)</tr>", table_m.group(0), re.S)
            for row in trs[1:]:
                cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
                cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
                if len(cells) < 3 or not cells[0].isdigit():
                    continue
                points_raw = re.sub(r"[^\d.]", "", cells[2]) or "0"
                rows.append(
                    {
                        "position": int(cells[0]),
                        "name": html_module.unescape(cells[1]),
                        "points": float(points_raw),
                    }
                )
        rows = rows[:limit]

        return {
            "standings": rows,
            "error": None if rows else "現在、順位データが空です(シーズン開幕前などの可能性があります)",
        }
    except Exception as exc:  # noqa: BLE001
        return {"standings": [], "error": f"取得エラー: {exc}"}


def fetch_calendar(calendar_url: str) -> list[dict]:
    """カレンダーページから開催予定+開催済みの年間日程を実データで取得する。"""
    session = _session()
    events: list[dict] = []
    try:
        resp = session.get(calendar_url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        html_text = resp.text

        date_block_re = re.compile(
            r'"calendar__date-number">(\d+)</span>\s*'
            r'<span class="calendar__date-month">([A-Z]+)</span>\s*'
            r'<span class="calendar__date-year">(\d+)</span>',
            re.S,
        )

        for chunk in html_text.split('calendar__list-item')[1:]:
            chunk = chunk[:3000]
            dates = date_block_re.findall(chunk)
            track_m = re.search(r'calendar__race-header">([^<]*)</h3', chunk)
            round_m = re.search(r'calendar__race-text">([^<]*)</span', chunk)
            if not dates or not track_m:
                continue
            s_day, s_month, s_year = dates[0]
            sort_key = int(s_year) * 10000 + _month_num(s_month) * 100 + int(s_day)
            if len(dates) >= 2:
                e_day, e_month, e_year = dates[1]
                date_range = (
                    f"{s_month} {s_day}–{e_day}, {e_year}"
                    if s_month == e_month
                    else f"{s_month} {s_day}–{e_month} {e_day}, {e_year}"
                )
            else:
                date_range = f"{s_month} {s_day}, {s_year}"
            events.append(
                {
                    "round": html_module.unescape(round_m.group(1).strip() if round_m else ""),
                    "track": html_module.unescape(track_m.group(1).strip()),
                    "date_range": date_range,
                    "status": "upcoming",
                    "sort_key": sort_key,
                }
            )

        full_month_re = re.compile(r"(\d{1,2})\s*-\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})")
        single_day_re = re.compile(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})")

        for chunk in html_text.split("past-events__list-item")[1:]:
            chunk = chunk[:2000]
            spans = re.findall(r'piped-list-span">(.*?)</span>', chunk, re.S)
            spans = [re.sub(r"<[^>]+>", " ", s).strip() for s in spans]
            if len(spans) < 3:
                continue
            date_text, track_country, round_text = spans[0], spans[1], spans[2]
            m = full_month_re.search(date_text)
            if m:
                s_day, _e_day, month_name, year = m.groups()
            else:
                m = single_day_re.search(date_text)
                if not m:
                    continue
                s_day, month_name, year = m.groups()
            sort_key = int(year) * 10000 + _month_num(month_name) * 100 + int(s_day)
            events.append(
                {
                    "round": html_module.unescape(round_text),
                    "track": html_module.unescape(re.sub(r"\s+", " ", track_country).strip()),
                    "date_range": date_text,
                    "status": "completed",
                    "sort_key": sort_key,
                }
            )
    except Exception:  # noqa: BLE001
        return []

    events.sort(key=lambda e: e["sort_key"])
    for e in events:
        e["status"] = _status(e["sort_key"])
        del e["sort_key"]
    return events

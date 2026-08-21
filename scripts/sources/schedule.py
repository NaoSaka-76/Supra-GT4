"""GR Supra GT4が参戦するレースの年間日程を取得する。

スーパー耐久(日本・アジア/ ST-Zクラス)は公式レース一覧ページに開催日・サーキット名・
大会名が静的HTMLで明記されており、比較的安定して取得できるため実際にスクレイピングして
一覧表示する。他シリーズの日程は各シリーズ公式サイトへの直接リンクを motorsports.py 側で
静的に保持している(サイトごとに構造が異なりJavaScript描画される部分も多いため)。
"""

from __future__ import annotations

import re
from datetime import date

import requests

from .common import REQUEST_TIMEOUT, USER_AGENT

SUPER_TAIKYU_INDEX_URL = "https://supertaikyu.com/race/index.html"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def _status(sort_key: int) -> str:
    today_key = date.today().year * 10000 + date.today().month * 100 + date.today().day
    return "upcoming" if sort_key >= today_key else "completed"


def fetch_super_taikyu_schedule() -> list[dict]:
    """スーパー耐久公式レース一覧(テストデー含む全ラウンド)を取得する。

    全クラス共通の開催日程であり、ST-Zクラス(GR Supra GT4)にもそのまま適用される。
    """
    session = _session()
    events: list[dict] = []
    try:
        resp = session.get(SUPER_TAIKYU_INDEX_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        # サーバーがcharsetを明示しないため、requestsの既定(ISO-8859-1)ではなく
        # 実際の文字コード推定を使う(このサイトは実質UTF-8)。
        resp.encoding = resp.apparent_encoding or "utf-8"
        html_text = resp.text

        blocks = re.findall(
            r'<div class="Race_BX_Wrapp">.*?(?=<div class="Race_BX_Wrapp">|\Z)', html_text, re.S
        )
        for block in blocks:
            rd_m = re.search(r'Race_BX_Rd">([^<]*)<', block)
            date_m = re.search(r'Race_BX_Date">\s*([^<]*)<', block)
            circuit_m = re.search(r'Race_BX_Circuit">([^<]*)<', block)
            name_m = re.search(r'Race_BX_Name">(.*?)</div>', block, re.S)
            if not (rd_m and date_m):
                continue
            date_text = date_m.group(1).strip()
            dm = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})(?:-(\d{1,2}))?", date_text)
            if not dm:
                continue
            year, month, day, _end_day = dm.groups()
            sort_key = int(year) * 10000 + int(month) * 100 + int(day)
            name_txt = re.sub(r"<!--.*?-->", "", name_m.group(1)) if name_m else ""
            name_txt = re.sub(r"<[^>]+>", "", name_txt).strip()
            events.append(
                {
                    "round": rd_m.group(1).strip(),
                    "track": (circuit_m.group(1).strip() if circuit_m else ""),
                    "name": name_txt,
                    "date_range": date_text.replace("/", "."),
                    "status": _status(sort_key),
                    "sort_key": sort_key,
                }
            )
    except Exception:  # noqa: BLE001
        return []

    events.sort(key=lambda e: e["sort_key"])
    for e in events:
        del e["sort_key"]
    return events

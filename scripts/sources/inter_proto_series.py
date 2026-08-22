"""インタープロトシリーズ(IPS)SUPRAクラスの日程・ランキングを実データで取得する。

公式サイト(interprotoseries.jp)は他のGT4系シリーズ(SRO系列)とは別プラットフォームだが、
以下の点で静的HTMLとして安定して取得できることを確認済み:

- トップページに年間日程が `sche_box` ブロックで並んでいる(開催回・日付・サーキット名)。
- ランキングページ(/ranking/)に `id="suppa_professional"` セクションがあり、
  SUPRA[PROFESSIONAL]クラス(GR Supra GT4 EVOのワンメイククラス)の全順位が
  `<table class="stali_ranktable">` として掲載されている。SUPRA[GENTLEMAN]クラスも
  別途あるが、Professionalクラスを代表として表示する(GT4 Americaの"Silver Teams"
  採用と同じ考え方: 複数クラスに分かれる場合は機械的に安定して取得できる1クラスを選ぶ)。

SUPRAクラスは全車がGR Supra GT4 EVOのワンメイククラスのため、特定チーム/ドライバーを
ハイライトする意味がなく、is_supra_gt4フラグは常にFalseとしている。
"""

from __future__ import annotations

import re
from datetime import date

import requests

from .common import REQUEST_TIMEOUT, USER_AGENT

HOME_URL = "https://interprotoseries.jp/"
RANKING_URL = "https://interprotoseries.jp/ranking/"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def _status(sort_key: int) -> str:
    today_key = date.today().year * 10000 + date.today().month * 100 + date.today().day
    return "upcoming" if sort_key >= today_key else "completed"


def fetch_schedule() -> list[dict]:
    """トップページの年間日程(全ラウンド共通、SUPRAクラスにもそのまま適用)を取得する。"""
    session = _session()
    events: list[dict] = []
    try:
        resp = session.get(HOME_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        html_text = resp.text

        for block in html_text.split('class="sche_box')[1:]:
            block = block[:1200]
            round_nums = re.findall(r"<span>(\d+)</span>", block)
            date1_m = re.search(r'sche_date01">(\d{4})<strong>\.(\d{2})\.(\d{2})\.</strong>', block)
            date2_m = re.search(r'sche_date02">.*?(\d{4})\.<strong>(\d{2})\.(\d{2})</strong>', block, re.S)
            circuit_m = re.search(r'sche_circuit">([^<]*)<', block)
            if not date1_m or not round_nums:
                continue
            y1, m1, d1 = date1_m.groups()
            sort_key = int(y1) * 10000 + int(m1) * 100 + int(d1)
            if date2_m:
                y2, m2, d2 = date2_m.groups()
                date_range = f"{y1}.{m1}.{d1}〜{y2}.{m2}.{d2}"
            else:
                date_range = f"{y1}.{m1}.{d1}"
            round_label = "Rd." + "&".join(round_nums)
            events.append(
                {
                    "round": round_label,
                    "track": circuit_m.group(1).strip() if circuit_m else "",
                    "date_range": date_range,
                    "status": _status(sort_key),
                }
            )
    except Exception:  # noqa: BLE001
        return []
    return events


def fetch_supra_standings(limit: int = 15) -> dict:
    """SUPRA[PROFESSIONAL]クラスの現在の順位表(公式サイト実データ)を取得する。"""
    session = _session()
    try:
        resp = session.get(RANKING_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        html_text = resp.text

        section_m = re.search(r'id="suppa_professional".*?</table>', html_text, re.S)
        if not section_m:
            return {"standings": [], "error": "SUPRAクラスのランキング表が見つかりませんでした"}

        table_m = re.search(r'<table class="stali_ranktable">.*?</table>', section_m.group(0), re.S)
        if not table_m:
            return {"standings": [], "error": "SUPRAクラスのランキング表が見つかりませんでした"}

        rows = re.findall(r"<tr>(.*?)</tr>", table_m.group(0), re.S)
        results: list[dict] = []
        for row in rows[1:]:
            cells = re.findall(r"<t[dh]>(.*?)</t[dh]>", row, re.S)
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            if len(cells) < 3 or not cells[0].isdigit():
                continue
            points_raw = re.sub(r"[^\d.]", "", cells[-1]) or "0"
            results.append(
                {
                    "position": int(cells[0]),
                    "name": f"No.{cells[1]} {cells[2]}",
                    "points": float(points_raw),
                }
            )
        rows_limited = results[:limit]
        return {
            "standings": rows_limited,
            "error": None if rows_limited else "現在、順位データが空です(シーズン開幕前などの可能性があります)",
        }
    except Exception as exc:  # noqa: BLE001
        return {"standings": [], "error": f"取得エラー: {exc}"}

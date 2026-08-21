"""モータースポーツのシリーズランキング(実データ)を取得する。

Pirelli/Fanatec GT4 America(gt4-america.com)は、TC America(tcamerica.us)と同じ
SRO Motorsports America系列の共通CMSで運用されており、シーズン/クラスをHTMLの
<select>から動的に解決でき、順位表も静的HTMLテーブルとして提供されているため、
実データでのグラフ化が可能。"Silver Teams"クラスにGR Supra GT4のエントリーが
確認できたため、このクラスのチームランキングをグラフ表示する。

一方、以下2地域は誤ったランキングを表示するリスクを避けるため意図的に対象外としている:
  - GT4 European Series(gt4series.com): クラス別フィルターがなく、シーズン混成の
    地域別ページ(例: "standing-europe-2021")が年度ごとに構造化されているなど、
    安定した機械的解釈がしづらい。
  - Monochrome GT4 Australia Series(gt4australia.com.au): 同じCMS系列だが、
    チーム別の使用車種(メーカー)を確定するための実績ページの構造を確認できておらず、
    誤ってSupra以外のチームをハイライトするリスクを避けるため非対応。
  いずれも「公式ランキングを見る」リンクから実際の順位を確認できる。
"""

from __future__ import annotations

import html as html_module
import re
from datetime import datetime, timezone, timedelta

import requests

from .common import REQUEST_TIMEOUT, USER_AGENT

BASE_URL = "https://www.gt4-america.com"
STANDINGS_URL = f"{BASE_URL}/standings"
RESULTS_URL = f"{BASE_URL}/results"
TARGET_CLASS_LABEL = "Silver Teams"
JST = timezone(timedelta(hours=9))
MAX_TRACKS_FOR_CAR_MAP = 10


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def _extract_select_options(html_text: str, select_name: str) -> list[tuple[str, str]]:
    block = re.search(rf'<select[^>]*name="{select_name}"[^>]*>(.*?)</select>', html_text, re.S)
    if not block:
        return []
    options = re.findall(r'<option\s+value="([^"]*)"[^>]*>([^<]*)</option>', block.group(1))
    return [(value, html_module.unescape(label.strip())) for value, label in options]


def _current_season_id(html_text: str, year: int) -> str | None:
    for value, label in _extract_select_options(html_text, "filter_season_id"):
        if str(year) in label:
            return value
    return None


def _target_standing_type_id(html_text: str) -> str | None:
    for value, label in _extract_select_options(html_text, "filter_standing_type"):
        if label.strip() == TARGET_CLASS_LABEL:
            return value
    return None


def _parse_standings_table(html_text: str) -> list[dict]:
    table = re.search(r'<table class="table standing[^"]*">.*?</table>', html_text, re.S)
    if not table:
        return []
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table.group(0), re.S)
    results: list[dict] = []
    for row in rows[1:]:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        if len(cells) < 3 or not cells[0].isdigit():
            continue
        points_raw = re.sub(r"[^\d]", "", cells[2]) or "0"
        results.append({"position": int(cells[0]), "name": html_module.unescape(cells[1]), "points": int(points_raw)})
    return results


def _parse_race_classification(html_text: str) -> list[dict]:
    """個別レースの完全クラシフィケーション表から team/car を抽出する。"""
    table = re.search(r"<table.*?</table>", html_text, re.S)
    if not table:
        return []
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table.group(0), re.S)
    if not rows:
        return []
    header = [re.sub(r"<[^>]+>", "", c).strip().lower() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", rows[0], re.S)]
    try:
        team_idx = header.index("team")
        car_idx = header.index("car")
    except ValueError:
        return []

    entries: list[dict] = []
    for row in rows[1:]:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        if len(cells) <= max(team_idx, car_idx):
            continue
        team, car = cells[team_idx], cells[car_idx]
        if team and car:
            entries.append({"team": html_module.unescape(team), "car": html_module.unescape(car)})
    return entries


def fetch_gt4_america_car_map() -> dict[str, str]:
    """GT4 Americaの各レース完全結果から team名 -> car(メーカー/モデル) のマップを組み立てる。

    ランキング表そのものにはチーム/車種の列が存在しないため、シーズン中の各レース
    ウィークエンドの完全クラシフィケーション(結果ページ)を巡回して補完する。
    """
    session = _session()
    car_map: dict[str, str] = {}
    try:
        index_resp = session.get(RESULTS_URL, timeout=REQUEST_TIMEOUT)
        index_resp.raise_for_status()
        track_paths = list(dict.fromkeys(re.findall(r'href="(/results/\d{4}/[a-z0-9-]+)"', index_resp.text)))

        for track_path in track_paths[:MAX_TRACKS_FOR_CAR_MAP]:
            try:
                track_resp = session.get(f"{BASE_URL}{track_path}", timeout=REQUEST_TIMEOUT)
                if not track_resp.ok:
                    continue
                race_paths = re.findall(rf'href="({re.escape(track_path)}/race-\d+)"', track_resp.text)
                if not race_paths:
                    continue
                race_resp = session.get(f"{BASE_URL}{race_paths[0]}", timeout=REQUEST_TIMEOUT)
                if not race_resp.ok:
                    continue
                for entry in _parse_race_classification(race_resp.text):
                    car_map[entry["team"]] = entry["car"]
            except requests.RequestException:
                continue
    except Exception:  # noqa: BLE001
        return car_map
    return car_map


def fetch_gt4_america_team_standings(limit: int = 15) -> dict:
    """GT4 America "Silver Teams" チームランキング(公式サイト実データ)。

    ランキング表自体にはチーム/車種の列がないため、各レースの完全結果ページから
    補完した team -> car マップで各行に "car" / "is_supra_gt4" を付与する。
    """
    session = _session()
    try:
        base_resp = session.get(STANDINGS_URL, timeout=REQUEST_TIMEOUT)
        base_resp.raise_for_status()
        base_html = base_resp.text

        season_id = _current_season_id(base_html, datetime.now(JST).year)
        standing_type_id = _target_standing_type_id(base_html)
        if not season_id or not standing_type_id:
            return {"standings": [], "error": "対象シーズン/クラスを公式サイト上で特定できませんでした"}

        resp = session.get(
            STANDINGS_URL,
            params={"filter_standing_type": standing_type_id, "filter_season_id": season_id},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        rows = _parse_standings_table(resp.text)[:limit]

        if rows:
            car_map = fetch_gt4_america_car_map()
            for row in rows:
                car = car_map.get(row["name"], "")
                row["car"] = car
                row["is_supra_gt4"] = "supra" in car.lower()

        return {
            "standings": rows,
            "error": None if rows else "現在、順位データが空です(シーズン開幕前などの可能性があります)",
        }
    except Exception as exc:  # noqa: BLE001
        return {"standings": [], "error": f"取得エラー: {exc}"}

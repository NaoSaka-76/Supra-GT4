"""GR Supra GT4が参戦するGT4カテゴリーのレース情報を地域別に集約する。

日本・アジア(スーパー耐久 ST-Zクラス)、米国(Pirelli/Fanatec GT4 America)、
欧州(GT4 European Series)、オセアニア(Monochrome GT4 Australia Series)の
4地域に整理。各シリーズ公式サイトの結果・ランキング表は構造がそれぞれ異なり安定した
スクレイピングが難しいため、ニュース記事(Google News RSS)ベースでトピックス・
レース結果・ランキング関連の話題を集約する。米国(GT4 America Silver Teams)のみ
公式サイトの実データからチームランキングをグラフ表示し、GR Supra GT4で参戦する
チームを目立たせて表示する(理由は standings.py 参照)。日本・アジア(スーパー耐久)は
公式レース一覧から年間スケジュールを実データで取得する。
"""

from __future__ import annotations

import urllib.parse

from .common import dedupe_by_url, fetch_google_news_rss, sort_by_recency
from .schedule import fetch_all as fetch_all_schedules
from .standings import fetch_gt4_america_team_standings


def _search_link(query: str) -> str:
    return "https://www.google.com/search?q=" + urllib.parse.quote(query)


REGIONS = {
    "japan_asia": {
        "label": "日本・アジア — スーパー耐久 ST-Zクラス",
        "flag": "🇯🇵",
        "queries": {
            "topics": [
                ("GRスープラ GT4 OR \"GR Supra GT4\" スーパー耐久 OR ST-Z", "ja", "JP", "JP:ja"),
                ("\"GR Supra GT4\" \"Super Taikyu\" OR \"ST-Z\"", "en-US", "US", "US:en"),
            ],
            "results": [
                ("スーパー耐久 ST-Z GRスープラ OR スープラGT4 決勝 OR レース結果 OR 表彰台 OR 優勝", "ja", "JP", "JP:ja"),
            ],
            "standings": [
                ("スーパー耐久 ST-Zクラス ランキング OR ポイントランキング スープラ", "ja", "JP", "JP:ja"),
            ],
        },
        "standings_url": "https://supertaikyu.com/race/standing.html",
        "standings_search": "スーパー耐久 ST-Zクラス ランキング Supra GT4 2026",
    },
    "us": {
        "label": "米国 — Pirelli/Fanatec GT4 America",
        "flag": "🇺🇸",
        "queries": {
            "topics": [
                ("\"GR Supra GT4\" \"GT4 America\"", "en-US", "US", "US:en"),
                ("\"GR Supra GT4\" \"GT World Challenge America\"", "en-US", "US", "US:en"),
            ],
            "results": [
                ("\"GR Supra GT4\" GT4 America race result OR podium OR win OR finish", "en-US", "US", "US:en"),
            ],
            "standings": [
                ("\"GT4 America\" championship standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
            ],
        },
        "standings_url": "https://www.gt4-america.com/standings",
        "standings_search": "GT4 America championship points standings 2026 Toyota GR Supra",
    },
    "europe": {
        "label": "欧州 — GT4 European Series",
        "flag": "🇪🇺",
        "queries": {
            "topics": [
                ("\"GR Supra GT4\" \"GT4 European Series\"", "en-GB", "GB", "GB:en"),
            ],
            "results": [
                ("\"GR Supra GT4\" \"GT4 European Series\" race result OR podium OR win", "en-GB", "GB", "GB:en"),
            ],
            "standings": [
                ("\"GT4 European Series\" championship standings Toyota OR \"GR Supra\"", "en-GB", "GB", "GB:en"),
            ],
        },
        "standings_url": "https://www.gt4series.com/standings",
        "standings_search": "GT4 European Series championship standings 2026 Toyota GR Supra",
    },
    "oceania": {
        "label": "オセアニア — Monochrome GT4 Australia Series",
        "flag": "🇦🇺",
        "queries": {
            "topics": [
                ("\"GR Supra GT4\" \"GT4 Australia\" OR \"Monochrome GT4\"", "en-AU", "AU", "AU:en"),
            ],
            "results": [
                ("\"GR Supra GT4\" GT4 Australia race result OR podium OR win", "en-AU", "AU", "AU:en"),
            ],
            "standings": [
                ("\"GT4 Australia\" championship standings Toyota OR \"GR Supra\"", "en-AU", "AU", "AU:en"),
            ],
        },
        "standings_url": "https://gt4australia.com.au/standings",
        "standings_search": "Monochrome GT4 Australia championship standings 2026 Toyota GR Supra",
    },
}


def _fetch_group(query_list: list[tuple], limit: int = 5) -> list[dict]:
    items: list[dict] = []
    for query, hl, gl, ceid in query_list:
        items.extend(fetch_google_news_rss(query, hl=hl, gl=gl, ceid=ceid, limit=limit))
    return sort_by_recency(dedupe_by_url(items))


def fetch() -> dict:
    result: dict = {}
    for key, region in REGIONS.items():
        result[key] = {
            "label": region["label"],
            "flag": region["flag"],
            "topics": _fetch_group(region["queries"]["topics"]),
            "results": _fetch_group(region["queries"]["results"]),
            "standings": _fetch_group(region["queries"]["standings"]),
            "standings_url": region["standings_url"],
            "standings_search_url": _search_link(region["standings_search"]),
            "standings_chart": None,
            "standings_chart_note": None,
            "schedule": [],
            "schedule_link": None,
        }

    us_chart = fetch_gt4_america_team_standings(limit=15)
    result["us"]["standings_chart"] = us_chart["standings"]
    result["us"]["standings_chart_note"] = (
        us_chart["error"]
        or "GT4 America \"Silver Teams\" チームランキング(公式サイト実データ)。"
        "各レースの完全結果ページから使用車種を補完しており、Toyota GR Supra GT4で"
        "参戦するチームには目印を付けています。"
    )
    result["japan_asia"]["standings_chart_note"] = (
        "スーパー耐久 公式サイトのST-Zクラス別ランキング表は機械的な構造解釈が難しいため、"
        "グラフ化は行っていません。「公式ランキングを見る」からご確認ください。"
    )
    result["europe"]["standings_chart_note"] = (
        "GT4 European Series公式サイトはクラス別フィルターの構造が年度により変わりやすいため、"
        "誤表示リスクを避けグラフ化は行っていません。「公式ランキングを見る」からご確認ください。"
    )
    result["oceania"]["standings_chart_note"] = (
        "Monochrome GT4 Australia公式サイトはチーム別使用車種を確定する実績ページの構造を"
        "確認できていないため、誤ってSupra以外のチームをハイライトするリスクを避けグラフ化は"
        "行っていません。「公式ランキングを見る」からご確認ください。"
    )

    schedules = fetch_all_schedules()
    result["japan_asia"]["schedule"] = schedules["japan_asia"]
    result["us"]["schedule_link"] = schedules["us"]["link"]
    result["europe"]["schedule_link"] = schedules["europe"]["link"]
    result["oceania"]["schedule_link"] = schedules["oceania"]["link"]

    return result

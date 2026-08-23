"""GR Supra GT4を含むGT4カテゴリーのレース情報を地域別・シリーズ別に集約する。

日本・アジア、米国、欧州、オセアニア、中東の5地域、計19シリーズ(GT3主体の
GT World Challenge各地域シリーズ4つを含む、同一大会ウィークエンドの上位カテゴリーとして
掲載)に整理。各シリーズ
公式サイトの結果・ランキング表は構造がそれぞれ異なり安定したスクレイピングが難しいため、
基本はニュース記事(Google News RSS)ベースでトピックス・レース結果・ランキング関連の
話題を集約し、公式サイトのスケジュール/ランキングページへの直接リンクを添える
(URLは実装時に実在を確認済み)。例外的に、以下11シリーズは日程・ランキングとも
公式サイトから実データで取得している。
  - スーパー耐久(日本・アジア、ST-Zクラス) : schedule.py / st_supra_teams.py
  - インタープロトシリーズ(SUPRA[PROFESSIONAL]クラス) : inter_proto_series.py
  - 以下9シリーズはSRO Motorsports Group系列共通のCMSプラットフォームのため
    sro_platform.py(SRO系公式サイト共通の日程・ランキング取得モジュール)で取得:
    GT World Challenge Asia・GT World Challenge America・GT World Challenge Australia
    (いずれもGT3主体、参考掲載)、SRO Japan Cup、GT4 European Series、
    British GT Championship(GT4クラス)、French GT4 Cup(FFSA GT)、
    Monochrome GT4 Australia Series(いずれもGT4クラス、順位表に使用車種の記載が
    ないためSupra GT4ハイライトなし)
また米国のGT4 America(Silver Teams)はチームランキングのみ公式サイトから実データで
取得している(理由は standings.py 参照)。
残るシリーズ(SRO GT Cup China、IMSA Michelin Pilot Challenge、GT4 Italian Series、
ADAC GT4 Germany、ニュルブルクリンクNLS、GT4 Winter Series、24H Series Middle East)は、
公式サイト自体は特定できているものの、Cloudflareボット対策・PDF専用配布・共通季間
順位表の非存在などにより安定したスクレイピングができないため、公式サイトへの直接
リンクのみを掲載している(2026年8月時点で全リンクの実在を再確認済み)。

各シリーズの"topics"クエリは、"GR Supra GT4"との共起を要求する狭いクエリに加えて、
シリーズ名単独の一般クエリも必ず1つ以上含めている。Supra GT4個別の話題が少ない
シリーズでもレースウィークエンド毎の一般的な話題(プレビュー/リザルト速報/日程発表等)が
拾えるようにし、トピックスが長期間更新されないことを防ぐ狙い。
"""

from __future__ import annotations

import urllib.parse

from .common import dedupe_by_url, fetch_google_news_rss, sort_by_recency
from .inter_proto_series import fetch_schedule as fetch_ips_schedule
from .inter_proto_series import fetch_supra_standings as fetch_ips_standings
from .schedule import fetch_super_taikyu_schedule
from .sro_platform import fetch_calendar as fetch_sro_calendar
from .sro_platform import fetch_standings as fetch_sro_standings
from .st_supra_teams import fetch_st_z_full_standings
from .standings import fetch_gt4_america_team_standings


def _search_link(query: str) -> str:
    return "https://www.google.com/search?q=" + urllib.parse.quote(query)


REGIONS = {
    "japan_asia": {
        "label": "日本・アジア",
        "flag": "🇯🇵",
        "series": [
            {
                "key": "gt_world_challenge_asia",
                "label": "GT World Challenge Asia",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"GT World Challenge Asia\"", "en-US", "US", "US:en"),
                        ("\"GT World Challenge Asia\"", "en-US", "US", "US:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"GT World Challenge Asia\" race result OR podium OR win", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"GT World Challenge Asia\" standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": "https://www.gt-world-challenge-asia.com/calendar",
                "standings_url": "https://www.gt-world-challenge-asia.com/standings",
            },
            {
                "key": "super_taikyu",
                "label": "スーパー耐久 ST-Zクラス(日本)",
                "queries": {
                    "topics": [
                        ("GRスープラ GT4 OR \"GR Supra GT4\" スーパー耐久 OR ST-Z", "ja", "JP", "JP:ja"),
                        ("\"GR Supra GT4\" \"Super Taikyu\" OR \"ST-Z\"", "en-US", "US", "US:en"),
                        ("スーパー耐久 ST-Z", "ja", "JP", "JP:ja"),
                    ],
                    "results": [
                        ("スーパー耐久 ST-Z GRスープラ OR スープラGT4 決勝 OR レース結果 OR 表彰台 OR 優勝", "ja", "JP", "JP:ja"),
                    ],
                    "standings": [
                        ("スーパー耐久 ST-Zクラス ランキング OR ポイントランキング スープラ", "ja", "JP", "JP:ja"),
                    ],
                },
                "schedule_link": None,  # 公式サイトから実データ取得(has_real_schedule)
                "has_real_schedule": True,
                "standings_url": "https://supertaikyu.com/race/standing.html",
            },
            {
                "key": "inter_proto_series",
                "label": "インタープロトシリーズ SUPRAクラス(日本)",
                "queries": {
                    "topics": [
                        ("インタープロトシリーズ スープラクラス OR GRスープラGT4", "ja", "JP", "JP:ja"),
                        ("インタープロトシリーズ", "ja", "JP", "JP:ja"),
                    ],
                    "results": [
                        ("インタープロトシリーズ スープラクラス 決勝 OR レース結果 OR 表彰台 OR 優勝", "ja", "JP", "JP:ja"),
                    ],
                    "standings": [
                        ("インタープロトシリーズ スープラクラス ランキング OR ポイントランキング", "ja", "JP", "JP:ja"),
                    ],
                },
                "schedule_link": "https://interprotoseries.jp/",
                "standings_url": "https://interprotoseries.jp/ranking/",
            },
            {
                "key": "sro_japan_cup",
                "label": "SRO Japan Cup GT4クラス(日本)",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"SRO Japan Cup\" OR SROジャパンカップ", "ja", "JP", "JP:ja"),
                        ("SROジャパンカップ OR \"SRO Japan Cup\"", "ja", "JP", "JP:ja"),
                    ],
                    "results": [
                        ("SROジャパンカップ GT4クラス GRスープラ OR スープラGT4 決勝 OR 表彰台 OR 優勝", "ja", "JP", "JP:ja"),
                    ],
                    "standings": [
                        ("SROジャパンカップ GT4クラス ランキング スープラ", "ja", "JP", "JP:ja"),
                    ],
                },
                "schedule_link": None,  # 公式サイトから実データ取得(has_real_schedule)
                "has_real_schedule": True,
                "standings_url": "https://japancup.co/standings",
            },
            {
                "key": "sro_gt_cup_china",
                "label": "SRO GT Cup(中国)",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"SRO GT Cup\" China", "en-US", "US", "US:en"),
                        ("\"SRO GT Cup\" China", "en-US", "US", "US:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"SRO GT Cup\" race result OR podium OR win", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"SRO GT Cup\" China championship standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": _search_link("SRO GT Cup China 2026 calendar official"),
                "standings_url": _search_link("SRO GT Cup China 2026 standings official"),
            },
        ],
    },
    "us": {
        "label": "米国",
        "flag": "🇺🇸",
        "series": [
            {
                "key": "gt_world_challenge_america",
                "label": "GT World Challenge America",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"GT World Challenge America\"", "en-US", "US", "US:en"),
                        ("\"GT World Challenge America\"", "en-US", "US", "US:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"GT World Challenge America\" race result OR podium OR win", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"GT World Challenge America\" standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": "https://www.gt-world-challenge-america.com/calendar",
                "standings_url": "https://www.gt-world-challenge-america.com/standings",
            },
            {
                "key": "gt4_america",
                "label": "Pirelli/Fanatec GT4 America(Silver Teams)",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"GT4 America\"", "en-US", "US", "US:en"),
                        ("\"GR Supra GT4\" \"GT World Challenge America\"", "en-US", "US", "US:en"),
                        ("\"GT4 America\" OR \"Pirelli GT4 America\"", "en-US", "US", "US:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" GT4 America race result OR podium OR win OR finish", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"GT4 America\" championship standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": "https://www.gt4-america.com/calendar",
                "has_real_standings": True,  # fetch_gt4_america_team_standings で補完
                "standings_url": "https://www.gt4-america.com/standings",
            },
            {
                "key": "imsa_michelin_pilot_challenge",
                "label": "IMSA Michelin Pilot Challenge(GSクラス)",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"Michelin Pilot Challenge\"", "en-US", "US", "US:en"),
                        ("\"Michelin Pilot Challenge\"", "en-US", "US", "US:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"Michelin Pilot Challenge\" race result OR podium OR win", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"Michelin Pilot Challenge\" GS class standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": "https://www.imsa.com/michelinpilotchallenge/imsa-michelin-pilot-challenge-2026-schedule/",
                "standings_url": "https://www.imsa.com/standings/",
            },
        ],
    },
    "europe": {
        "label": "欧州",
        "flag": "🇪🇺",
        "series": [
            {
                "key": "gt_world_challenge_europe",
                "label": "GT World Challenge Europe",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"GT World Challenge Europe\"", "en-GB", "GB", "GB:en"),
                        ("\"GT World Challenge Europe\"", "en-GB", "GB", "GB:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"GT World Challenge Europe\" race result OR podium OR win", "en-GB", "GB", "GB:en"),
                    ],
                    "standings": [
                        ("\"GT World Challenge Europe\" standings Toyota OR \"GR Supra\"", "en-GB", "GB", "GB:en"),
                    ],
                },
                "schedule_link": "https://www.gt-world-challenge-europe.com/calendar",
                "standings_url": "https://www.gt-world-challenge-europe.com/standings",
            },
            {
                "key": "gt4_european_series",
                "label": "GT4 European Series",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"GT4 European Series\"", "en-GB", "GB", "GB:en"),
                        ("\"GT4 European Series\"", "en-GB", "GB", "GB:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"GT4 European Series\" race result OR podium OR win", "en-GB", "GB", "GB:en"),
                    ],
                    "standings": [
                        ("\"GT4 European Series\" championship standings Toyota OR \"GR Supra\"", "en-GB", "GB", "GB:en"),
                    ],
                },
                "schedule_link": None,  # 公式サイトから実データ取得(has_real_schedule)
                "has_real_schedule": True,
                "standings_url": "https://www.gt4europeanseries.com/standings",
            },
            {
                "key": "british_gt4",
                "label": "British GT Championship(GT4クラス)",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"British GT\"", "en-GB", "GB", "GB:en"),
                        ("\"British GT\" GT4", "en-GB", "GB", "GB:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"British GT\" race result OR podium OR win", "en-GB", "GB", "GB:en"),
                    ],
                    "standings": [
                        ("\"British GT\" GT4 championship standings Toyota OR \"GR Supra\"", "en-GB", "GB", "GB:en"),
                    ],
                },
                "schedule_link": None,  # 公式サイトから実データ取得(has_real_schedule)
                "has_real_schedule": True,
                "standings_url": "https://www.britishgt.com/standings",
            },
            {
                "key": "french_gt4_cup",
                "label": "French GT4 Cup",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"French GT4 Cup\"", "en-US", "US", "US:en"),
                        ("GRスープラ GT4 OR \"GR Supra GT4\" \"French GT4 Cup\"", "fr", "FR", "FR:fr"),
                        ("\"French GT4 Cup\"", "fr", "FR", "FR:fr"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"French GT4 Cup\" race result OR podium OR win", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"French GT4 Cup\" championship standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": None,  # 公式サイトから実データ取得(has_real_schedule)
                "has_real_schedule": True,
                "standings_url": "https://ffsagt.gt4series.com/standings",
            },
            {
                "key": "gt4_italian_series",
                "label": "GT4 Italian Series",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"GT4 Italian Series\"", "en-US", "US", "US:en"),
                        ("\"GT4 Italian Series\"", "en-US", "US", "US:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"GT4 Italian Series\" race result OR podium OR win", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"GT4 Italian Series\" championship standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": "https://www.acisport.it/it/CIGT/calendario-e-risultati/2026/1045/GT4-Italy-Series",
                "standings_url": "https://www.acisport.it/it/CIGT/classifiche/2026",
            },
            {
                "key": "adac_gt4_germany",
                "label": "ADAC GT4 Germany",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"ADAC GT4 Germany\"", "en-US", "US", "US:en"),
                        ("\"GR Supra GT4\" \"ADAC GT4 Germany\"", "de-DE", "DE", "DE:de"),
                        ("\"ADAC GT4 Germany\"", "de-DE", "DE", "DE:de"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"ADAC GT4 Germany\" race result OR podium OR win", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"ADAC GT4 Germany\" championship standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": "https://www.adac-motorsport.de/en/adac-gt4-germany/race-calendar/",
                "standings_url": "https://www.adac-motorsport.de/en/adac-gt4-germany/rankings/2026/",
            },
            {
                "key": "nls_nuerburgring",
                "label": "ニュルブルクリンク NLS・24h(SP10クラス)",
                "queries": {
                    "topics": [
                        ("GR Supra GT4 Nürburgring Langstreckenserie OR NLS OR SP10", "de-DE", "DE", "DE:de"),
                        ("\"GR Supra GT4\" Nürburgring 24 Hours OR NLS", "en-US", "US", "US:en"),
                        ("Nürburgring Langstreckenserie OR NLS", "de-DE", "DE", "DE:de"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" Nürburgring race result OR podium OR win OR Sieg", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("NLS SP10 championship standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": "https://www.nuerburgring-langstrecken-serie.de/language/en/calendar-nurburgring-langstrecken-serie-2026/",
                "standings_url": "https://www.nuerburgring-langstrecken-serie.de/language/en/class-winners/",
            },
            {
                "key": "gt4_winter_series",
                "label": "GT4 Winter Series(イベリア半島)",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"GT4 Winter Series\"", "en-US", "US", "US:en"),
                        ("\"GT4 Winter Series\"", "en-US", "US", "US:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"GT4 Winter Series\" race result OR podium OR win", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"GT4 Winter Series\" championship standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": "https://winter-series.racing/gt4-winter-series/",
                "standings_url": "https://winter-series.racing/gt4-winter-series/results/",
            },
        ],
    },
    "oceania": {
        "label": "オセアニア",
        "flag": "🇦🇺",
        "series": [
            {
                "key": "gt_world_challenge_australia",
                "label": "GT World Challenge Australia",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"GT World Challenge Australia\"", "en-AU", "AU", "AU:en"),
                        ("\"GT World Challenge Australia\"", "en-AU", "AU", "AU:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" \"GT World Challenge Australia\" race result OR podium OR win", "en-AU", "AU", "AU:en"),
                    ],
                    "standings": [
                        ("\"GT World Challenge Australia\" standings Toyota OR \"GR Supra\"", "en-AU", "AU", "AU:en"),
                    ],
                },
                "schedule_link": None,  # 公式サイトから実データ取得(has_real_schedule)
                "has_real_schedule": True,
                "standings_url": "https://www.gt-world-challenge-australia.com/standings",
            },
            {
                "key": "gt4_australia",
                "label": "Monochrome GT4 Australia Series",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"GT4 Australia\" OR \"Monochrome GT4\"", "en-AU", "AU", "AU:en"),
                        ("\"Monochrome GT4 Australia\" OR \"GT4 Australia\"", "en-AU", "AU", "AU:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" GT4 Australia race result OR podium OR win", "en-AU", "AU", "AU:en"),
                    ],
                    "standings": [
                        ("\"GT4 Australia\" championship standings Toyota OR \"GR Supra\"", "en-AU", "AU", "AU:en"),
                    ],
                },
                "schedule_link": None,  # 公式サイトから実データ取得(has_real_schedule)
                "has_real_schedule": True,
                "standings_url": "https://gt4australia.com.au/standings",
            },
        ],
    },
    "middle_east": {
        "label": "中東",
        "flag": "🇦🇪",
        "series": [
            {
                "key": "24h_series_middle_east",
                "label": "24H Series Middle East(GT4クラス)",
                "queries": {
                    "topics": [
                        ("\"GR Supra GT4\" \"24H Series\" Middle East OR Dubai OR \"Abu Dhabi\"", "en-US", "US", "US:en"),
                        ("\"24H Series\" Middle East", "en-US", "US", "US:en"),
                    ],
                    "results": [
                        ("\"GR Supra GT4\" Dubai OR \"Abu Dhabi\" race result OR podium OR win", "en-US", "US", "US:en"),
                    ],
                    "standings": [
                        ("\"24H Series\" Middle East GT4 standings Toyota OR \"GR Supra\"", "en-US", "US", "US:en"),
                    ],
                },
                "schedule_link": "https://www.24hseries.com/races",
                "standings_url": "https://www.24hseries.com/standings",
            },
        ],
    },
}


def _fetch_group(query_list: list[tuple], limit: int = 5) -> list[dict]:
    items: list[dict] = []
    for query, hl, gl, ceid in query_list:
        items.extend(fetch_google_news_rss(query, hl=hl, gl=gl, ceid=ceid, limit=limit))
    return sort_by_recency(dedupe_by_url(items))


def _build_series(series_cfg: dict) -> dict:
    return {
        "key": series_cfg["key"],
        "label": series_cfg["label"],
        "topics": _fetch_group(series_cfg["queries"]["topics"]),
        "results": _fetch_group(series_cfg["queries"]["results"]),
        "standings": _fetch_group(series_cfg["queries"]["standings"]),
        "standings_url": series_cfg["standings_url"],
        "standings_chart": None,
        "standings_chart_note": None,
        "standings_error": False,
        "schedule": [],
        "schedule_link": series_cfg.get("schedule_link"),
    }


def fetch() -> dict:
    result: dict = {}
    for region_key, region in REGIONS.items():
        result[region_key] = {
            "label": region["label"],
            "flag": region["flag"],
            "series": [_build_series(s) for s in region["series"]],
        }

    def _set(region_key: str, series_key: str, **fields: object) -> None:
        for series in result[region_key]["series"]:
            if series["key"] == series_key:
                series.update(fields)
                return

    # 日本・アジア: スーパー耐久(ST-Z)は年間スケジュール・順位表とも公式サイトから
    # 実データ取得する(順位表のパース方法は st_supra_teams.py 参照)。
    taikyu_chart = fetch_st_z_full_standings(limit=15)
    _set(
        "japan_asia",
        "super_taikyu",
        schedule=fetch_super_taikyu_schedule(),
        standings_chart=taikyu_chart["standings"],
        standings_error=bool(taikyu_chart["error"]),
        standings_chart_note=(
            taikyu_chart["error"]
            or "スーパー耐久 ST-Zクラス チームランキング(公式サイト実データ)。"
            "GR Supra GT4で参戦するチームには目印を付けています。"
        ),
    )

    # 日本・アジア: GT World Challenge Asiaは、米国GT4 America等と同じSRO系列の共通
    # プラットフォームのため、日程・順位表(GT3 Teams Championship)とも実データ取得できる。
    # GT3主体のシリーズのためSupra GT4のハイライトは対象外。
    gtwca_chart = fetch_sro_standings(
        "https://www.gt-world-challenge-asia.com/standings", "GT3 Teams Championship", limit=15
    )
    _set(
        "japan_asia",
        "gt_world_challenge_asia",
        schedule_link=None,
        schedule=fetch_sro_calendar("https://www.gt-world-challenge-asia.com/calendar"),
        standings_chart=gtwca_chart["standings"],
        standings_error=bool(gtwca_chart["error"]),
        standings_chart_note=(
            gtwca_chart["error"]
            or "GT World Challenge Asia GT3 Teams Championship(公式サイト実データ)。"
            "GT3主体のシリーズのためSupra GT4(GT4クラス)のハイライトは対象外です。"
        ),
    )

    # 日本・アジア: インタープロトシリーズ SUPRAクラスも、日程・順位表(SUPRA
    # [PROFESSIONAL]クラス)とも公式サイトから実データ取得できる。全車GR Supra GT4 EVOの
    # ワンメイククラスのため、Supra GT4のハイライトは意味を持たない。
    ips_chart = fetch_ips_standings(limit=15)
    _set(
        "japan_asia",
        "inter_proto_series",
        schedule_link=None,
        schedule=fetch_ips_schedule(),
        standings_chart=ips_chart["standings"],
        standings_error=bool(ips_chart["error"]),
        standings_chart_note=(
            ips_chart["error"]
            or "SUPRA[PROFESSIONAL]クラス ドライバーランキング(公式サイト実データ)。"
            "全車GR Supra GT4 EVOのワンメイククラスのため、特定車両のハイライトはありません。"
        ),
    )

    # 日本・アジア: SRO Japan Cup(GT4クラス)は、2024年にGT World Challenge AsiaのGT4クラスを
    # 引き継いだ際に専用の公式サイト(japancup.co)が新設されており、同じSRO系列プラットフォームの
    # ため日程・順位表(GT4 Teams Championship)とも実データ取得できる。順位表に使用車種の記載が
    # ないため、Supra GT4のハイライトは行わない。
    sjc_chart = fetch_sro_standings("https://japancup.co/standings", "GT4 Teams Championship", limit=15)
    _set(
        "japan_asia",
        "sro_japan_cup",
        schedule_link=None,
        schedule=fetch_sro_calendar("https://japancup.co/calendar"),
        standings_chart=sjc_chart["standings"],
        standings_error=bool(sjc_chart["error"]),
        standings_chart_note=(
            sjc_chart["error"]
            or "SRO Japan Cup GT4 Teams Championship(公式サイト実データ)。"
            "順位表に使用車種の記載がないため、Supra GT4のハイライトは行っていません。"
        ),
    )

    # 米国: GT4 America(Silver Teams)は公式サイトからチームランキングを実データ取得する。
    us_chart = fetch_gt4_america_team_standings(limit=15)
    _set(
        "us",
        "gt4_america",
        standings_chart=us_chart["standings"],
        standings_error=bool(us_chart["error"]),
        standings_chart_note=(
            us_chart["error"]
            or "GT4 America \"Silver Teams\" チームランキング(公式サイト実データ)。"
            "各レースの完全結果ページから使用車種を補完しており、Toyota GR Supra GT4で"
            "参戦するチームには目印を付けています。"
        ),
    )

    # 米国: GT World Challenge Americaも同じSRO系列プラットフォームのため実データ取得できる。
    # GT3主体のシリーズのためSupra GT4のハイライトは対象外。
    gtwcam_chart = fetch_sro_standings(
        "https://www.gt-world-challenge-america.com/standings", "Pro-Am Teams", limit=15
    )
    _set(
        "us",
        "gt_world_challenge_america",
        schedule_link=None,
        schedule=fetch_sro_calendar("https://www.gt-world-challenge-america.com/calendar"),
        standings_chart=gtwcam_chart["standings"],
        standings_error=bool(gtwcam_chart["error"]),
        standings_chart_note=(
            gtwcam_chart["error"]
            or "GT World Challenge America Pro-Am Teams(公式サイト実データ)。"
            "GT3主体のシリーズのためSupra GT4(GT4クラス)のハイライトは対象外です。"
        ),
    )

    # 欧州: British GT ChampionshipのGT4クラスも同じSRO系列プラットフォームのため実データ
    # 取得できる。順位表に使用車種の記載がないため、Supra GT4のハイライトは行わない。
    bgt4_chart = fetch_sro_standings("https://www.britishgt.com/standings", "GT4 Teams Championship", limit=15)
    _set(
        "europe",
        "british_gt4",
        schedule_link=None,
        schedule=fetch_sro_calendar("https://www.britishgt.com/calendar"),
        standings_chart=bgt4_chart["standings"],
        standings_error=bool(bgt4_chart["error"]),
        standings_chart_note=(
            bgt4_chart["error"]
            or "British GT Championship GT4 Teams Championship(公式サイト実データ)。"
            "順位表に使用車種の記載がないため、Supra GT4のハイライトは行っていません。"
        ),
    )

    # 欧州: GT4 European Seriesは、gt4series.com(GT4メーカーランキング集計サイト、別法人)とは
    # 別に専用の公式サイト(gt4europeanseries.com)を持ち、同じSRO系列プラットフォームのため
    # 実データ取得できる。クラスはAM/PRO-AM/SILVERの3つに分かれ、PRO-AMを代表値として採用。
    # 順位表に使用車種の記載がないため、Supra GT4のハイライトは行わない。
    gt4eu_chart = fetch_sro_standings("https://www.gt4europeanseries.com/standings", "PRO-AM", limit=15)
    _set(
        "europe",
        "gt4_european_series",
        schedule_link=None,
        schedule=fetch_sro_calendar("https://www.gt4europeanseries.com/calendar"),
        standings_chart=gt4eu_chart["standings"],
        standings_error=bool(gt4eu_chart["error"]),
        standings_chart_note=(
            gt4eu_chart["error"]
            or "GT4 European Series PRO-AMクラス ランキング(公式サイト実データ)。"
            "順位表に使用車種の記載がないため、Supra GT4のハイライトは行っていません。"
        ),
    )

    # 欧州: French GT4 Cup(FFSA GT)も同じSRO系列プラットフォーム(gt4series.com系サブドメイン)
    # のため実データ取得できる。順位表に使用車種の記載がないため、Supra GT4のハイライトは行わない。
    fgt4_chart = fetch_sro_standings("https://ffsagt.gt4series.com/standings", "GT4 Général", limit=15)
    _set(
        "europe",
        "french_gt4_cup",
        schedule_link=None,
        schedule=fetch_sro_calendar("https://ffsagt.gt4series.com/calendar"),
        standings_chart=fgt4_chart["standings"],
        standings_error=bool(fgt4_chart["error"]),
        standings_chart_note=(
            fgt4_chart["error"]
            or "French GT4 Cup(FFSA GT)ランキング(公式サイト実データ)。"
            "順位表に使用車種の記載がないため、Supra GT4のハイライトは行っていません。"
        ),
    )

    # オセアニア: GT World Challenge Australiaも同じSRO系列プラットフォームのため実データ
    # 取得できる。GT3主体のシリーズのためSupra GT4のハイライトは対象外。
    gtwcau_chart = fetch_sro_standings(
        "https://www.gt-world-challenge-australia.com/standings", "Overall Teams Championship", limit=15
    )
    _set(
        "oceania",
        "gt_world_challenge_australia",
        schedule_link=None,
        schedule=fetch_sro_calendar("https://www.gt-world-challenge-australia.com/calendar"),
        standings_chart=gtwcau_chart["standings"],
        standings_error=bool(gtwcau_chart["error"]),
        standings_chart_note=(
            gtwcau_chart["error"]
            or "GT World Challenge Australia Overall Teams Championship(公式サイト実データ)。"
            "GT3主体のシリーズのためSupra GT4(GT4クラス)のハイライトは対象外です。"
        ),
    )

    # オセアニア: Monochrome GT4 Australia Seriesも同じSRO系列プラットフォームのため実データ
    # 取得できる。順位表に使用車種の記載がないため、Supra GT4のハイライトは行わない。
    gt4au_chart = fetch_sro_standings(
        "https://gt4australia.com.au/standings", "Overall Teams Championship", limit=15
    )
    _set(
        "oceania",
        "gt4_australia",
        schedule_link=None,
        schedule=fetch_sro_calendar("https://gt4australia.com.au/calendar"),
        standings_chart=gt4au_chart["standings"],
        standings_error=bool(gt4au_chart["error"]),
        standings_chart_note=(
            gt4au_chart["error"]
            or "Monochrome GT4 Australia Series Overall Teams Championship(公式サイト実データ)。"
            "順位表に使用車種の記載がないため、Supra GT4のハイライトは行っていません。"
        ),
    )

    # それ以外のシリーズは、順位表のクラス別フィルター構造やチーム別使用車種の確定方法を
    # 安定的に確認できていないため、誤表示リスクを避けグラフ化は行わず、公式ランキング
    # ページへの直接リンクのみを表示する。
    default_note = (
        "このシリーズの公式サイトは順位表の構造を安定的に解釈できないため、グラフ化は"
        "行っていません。「公式ランキングを見る」からご確認ください。"
    )
    for region in result.values():
        for series in region["series"]:
            if series["standings_chart_note"] is None:
                series["standings_chart_note"] = default_note

    return result

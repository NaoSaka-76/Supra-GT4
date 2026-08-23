"""Supra GT4 Watchダッシュボード用データを収集し、site/data/latest.jsonへ出力する。

1日3回(7時/12時/17時 JST)、GitHub Actionsから実行される想定。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from sources import complaints, gt4_topics, motorsports, sentiment, social_buzz, st_supra_teams, youtube

JST = timezone(timedelta(hours=9))
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "site" / "data" / "latest.json"

YOUTUBE_QUERIES_EN = [
    "Toyota GR Supra GT4",
    "GT4 America racing Supra",
    "GT4 European Series racing",
]
YOUTUBE_QUERIES_JA = [
    "トヨタ スープラ GT4",
    "GT4 レース スーパー耐久",
]


def _with_sentiment(items: list[dict]) -> list[dict]:
    return sentiment.attach_sentiment(items)


def _motorsports_section() -> dict:
    regions = motorsports.fetch()
    for r in regions.values():
        for series in r["series"]:
            series["topics"] = _with_sentiment(series["topics"])
            series["results"] = _with_sentiment(series["results"])
            series["standings"] = _with_sentiment(series["standings"])
    return {
        "label": "GR Supra GT4 参戦レース(地域別・全19シリーズ)",
        "regions": regions,
        "note": (
            "トピックス/レース結果はニュース記事ベースで集約しています。11シリーズ"
            "(スーパー耐久・インタープロトシリーズ・SRO Japan Cup・GT World Challenge"
            "Asia/America/Australia・GT4 European Series・British GT・French GT4 Cup・"
            "Monochrome GT4 Australia)は日程とランキングを、米国のGT4 America(Silver"
            "Teams)はチームランキングを、それぞれ公式サイトの実データで取得しています"
            "(他シリーズを図示しない理由は各カード内に記載)。"
        ),
    }


def _merge_youtube(a: dict, b: dict, top_n: int = 20) -> dict:
    def merge_list(list_a: list[dict], list_b: list[dict], sort_key, reverse: bool) -> list[dict]:
        merged: dict[str, dict] = {}
        for item in list_a + list_b:
            vid = item.get("video_id")
            if not vid:
                continue
            merged[vid] = item
        return sorted(merged.values(), key=sort_key, reverse=reverse)[:top_n]

    popular = merge_list(a["popular"], b["popular"], lambda v: v.get("view_count", 0), True)
    new = merge_list(a["new"], b["new"], lambda v: v.get("recency_seconds", 10**12), False)

    if not popular:
        popular = a["popular"] or b["popular"]
    if not new:
        new = a["new"] or b["new"]

    return {"popular": popular, "new": new}


def build_dashboard() -> dict:
    now_utc = datetime.now(timezone.utc)
    now_jst = now_utc.astimezone(JST)

    youtube_en = youtube.fetch(queries=YOUTUBE_QUERIES_EN, hl="en", gl="US")
    youtube_ja = youtube.fetch(queries=YOUTUBE_QUERIES_JA, hl="ja", gl="JP")
    youtube_data = _merge_youtube(youtube_en, youtube_ja)

    buzz_data = social_buzz.fetch()
    complaint_data = complaints.fetch()
    st_teams = st_supra_teams.fetch()

    return {
        "generated_at_utc": now_utc.isoformat(),
        "generated_at_jst": now_jst.strftime("%Y-%m-%d %H:%M JST"),
        "sections": {
            "st_supra_teams": {
                "label": "スーパー耐久 ST-Zクラス Supra GT4参戦チーム",
                "teams": st_teams,
            },
            "motorsports": _motorsports_section(),
            "gt4_topics": {
                "label": "GT4カテゴリー最新トピックス",
                "items": gt4_topics.fetch(),
                "note": (
                    "GT4ホモロゲーション/レギュレーション、競合GT4(BMW・Mercedes-AMG・Porsche・"
                    "Ford・Aston Martin・Audi・McLaren等)の開発・アップデート、技術情報、"
                    "Supra GT4や競合車の不具合情報をカテゴリー別バッジ付きで集約しています。"
                ),
            },
            "youtube_popular": {
                "label": "YouTube 人気動画(Supra GT4・競合GT4)",
                "items": _with_sentiment(youtube_data["popular"]),
            },
            "youtube_new": {
                "label": "YouTube 新着動画(Supra GT4・競合GT4)",
                "items": _with_sentiment(youtube_data["new"]),
            },
            "social_buzz": {
                "label": "SNSでの話題(X/Facebook 代替指標)",
                "items": _with_sentiment(buzz_data["items_latest"]),
                "items_buzz": _with_sentiment(buzz_data["items_buzz"]),
                "note": buzz_data["note"],
            },
            "complaints": {
                "label": "Supra GT4 お客様の声・クレーム関連情報",
                "items": _with_sentiment(complaint_data["items_latest"]),
                "items_buzz": _with_sentiment(complaint_data["items_buzz"]),
                "note": complaint_data["note"],
            },
        },
    }


def main() -> None:
    dashboard = build_dashboard()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote dashboard data to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

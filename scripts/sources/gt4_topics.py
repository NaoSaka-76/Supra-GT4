"""GT4カテゴリー全体の最新情報トピックス。

GT4ホモロゲーション/レギュレーション、競合GT4(BMW・Mercedes-AMG・Porsche・
Ford・Aston Martin・Audi・McLaren等)の開発・アップデート情報、GT4の技術情報、
Supra GT4や競合車の不具合情報をGoogle News RSSベースで集約する。
カテゴリーごとにタグ付けし、ダッシュボード上でバッジ表示する。
"""

from __future__ import annotations

from .common import dedupe_by_url, fetch_google_news_rss, sort_by_recency

_COMPETITOR_NAMES = (
    '"BMW M4 GT4" OR "Mercedes-AMG GT4" OR "Porsche Cayman GT4" OR "Ford Mustang GT4" '
    'OR "Aston Martin Vantage GT4" OR "Audi R8 LMS GT4" OR "McLaren Artura GT4" '
    'OR "Chevrolet Camaro GT4" OR "KTM X-Bow GT4"'
)

CATEGORIES = [
    {
        "key": "homologation",
        "label": "ホモロゲーション",
        "queries": [
            ("GT4 homologation OR \"Balance of Performance\" OR BoP SRO", "en-US", "US", "US:en"),
            ("GT4 ホモロゲーション OR BoP OR 性能調整", "ja", "JP", "JP:ja"),
        ],
    },
    {
        "key": "regulation",
        "label": "レギュレーション",
        "queries": [
            ("GT4 regulations OR \"rule change\" SRO Motorsports", "en-US", "US", "US:en"),
            ("GT4 レギュレーション OR 規則変更 OR 車両規定", "ja", "JP", "JP:ja"),
        ],
    },
    {
        "key": "competitor",
        "label": "競合GT4の開発",
        "queries": [
            (f"({_COMPETITOR_NAMES}) development OR update OR launch OR new", "en-US", "US", "US:en"),
        ],
    },
    {
        "key": "technical",
        "label": "技術情報",
        "queries": [
            (
                "GT4 technical OR engine OR aero OR chassis (Toyota OR BMW OR Mercedes OR Porsche OR Ford)",
                "en-US",
                "US",
                "US:en",
            ),
            ("GT4 技術 OR エンジン OR 空力 OR シャシー", "ja", "JP", "JP:ja"),
        ],
    },
    {
        "key": "issue",
        "label": "不具合情報",
        "queries": [
            (
                f'GT4 recall OR complaint OR issue OR problem OR defect ("GR Supra" OR {_COMPETITOR_NAMES})',
                "en-US",
                "US",
                "US:en",
            ),
            ("GT4 スープラ OR 競合 不具合 OR クレーム OR リコール", "ja", "JP", "JP:ja"),
        ],
    },
]


def fetch(limit_per_query: int = 6) -> list[dict]:
    items: list[dict] = []
    for category in CATEGORIES:
        for query, hl, gl, ceid in category["queries"]:
            results = fetch_google_news_rss(query, hl=hl, gl=gl, ceid=ceid, limit=limit_per_query)
            for item in results:
                item["category"] = category["key"]
                item["category_label"] = category["label"]
            items.extend(results)
    return sort_by_recency(dedupe_by_url(items))

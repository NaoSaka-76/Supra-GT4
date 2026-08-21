"""X(旧Twitter)/FacebookでのSupra GT4含む競合GT4の話題の代替情報を収集する。

X API・Facebook Graph APIの公式キーを利用しないため、SNS投稿そのものは取得できない。
代替として、ニュース/ブログでの言及(Google News RSS)を「話題度」の指標として使う。
「最新順」「話題順」の2タブで表示する(話題順は検索結果内での上位表示度を代替指標とする)。
"""

from __future__ import annotations

from .common import dedupe_by_url, fetch_google_news_rss, sort_by_recency

NEWS_QUERIES = [
    ("\"GR Supra GT4\" viral OR trending OR buzz OR \"social media\"", "en-US", "US", "US:en"),
    (
        "GT4 (\"BMW M4 GT4\" OR \"Mercedes-AMG GT4\" OR \"Porsche Cayman GT4\" OR \"Ford Mustang GT4\") "
        "viral OR trending OR buzz",
        "en-US",
        "US",
        "US:en",
    ),
    ("スープラ GT4 OR GT4 話題 OR バズ OR SNS", "ja", "JP", "JP:ja"),
]


def _dedupe_keep_best_rank(items: list[dict]) -> list[dict]:
    """URL重複時は、より上位(_rankが小さい=検索結果内で目立つ)の方を残す。"""
    best: dict[str, dict] = {}
    for item in items:
        key = item.get("url") or item.get("title")
        if not key:
            continue
        if key not in best or item["_rank"] < best[key]["_rank"]:
            best[key] = item
    return list(best.values())


def fetch(limit_per_query: int = 8) -> dict:
    items: list[dict] = []
    for query, hl, gl, ceid in NEWS_QUERIES:
        results = fetch_google_news_rss(query, hl=hl, gl=gl, ceid=ceid, limit=limit_per_query)
        for rank, item in enumerate(results):
            item["_rank"] = rank
        items.extend(results)

    deduped = _dedupe_keep_best_rank(items)
    items_latest = sort_by_recency(deduped)
    # "_rank"(検索結果内の上位表示度)が小さい順 = 話題になっている/注目度が高い順の代替指標
    items_buzz = sorted(deduped, key=lambda x: x["_rank"])
    for item in deduped:
        item.pop("_rank", None)

    return {
        "items_latest": items_latest,
        "items_buzz": items_buzz,
        "note": (
            "X/Facebookの公式APIキーが未設定のため、投稿本体は取得できません。"
            "ニュース・ブログでの言及数を話題性の代替指標として表示しています。"
            "「話題順」は検索結果内での上位表示度を注目度の代替指標として用いています"
            "(実際のSNS拡散数やエンゲージメント数ではありません)。"
        ),
    }

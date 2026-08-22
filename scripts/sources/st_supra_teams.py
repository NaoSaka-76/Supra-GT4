"""日本のスーパー耐久 ST-Zクラスに参戦するGR Supra GT4チームの情報を集約する。

チームの背景(運営母体・オーナー)は手動収集した静的データとしてこのファイル内の
TEAMS定数に保持する(公式サイトに構造化データがないため)。一方、現在のシリーズ
ポイント/順位、およびドライバー名は公式サイト(supertaikyu.com)から毎回実データで
取得する。

ドライバー名は、直近開催されたラウンドの公式エントリーリストページ
(race/round_XX.html内のST-Zクラス表)から取得する。当初はチーム個別ページ
(teams/2026_XXX.html)を情報源にしていたが、そちらは一部チームでドライバー名が
伏字("※※※※※")のまま更新されないケースがあり、実際にはラウンドのエントリー
リスト側に確定済みの氏名が掲載されていることを確認したため切り替えた
(決勝正式結果PDFはフォントの文字コードマッピングが非標準で文字化けし信頼できる
抽出ができなかったため使用していない)。

ドライバーのプロ/アマ区分について: 公式サイトには個々のドライバーのライセンス
グレード(プラチナ/エキスパート/ジェントルマン)は掲載されていない。ただし
スーパー耐久のレギュレーション上、ST-Zクラスは「A driverとして最低1名の
ジェントルマンドライバー登録」が義務付けられているため、この規則に基づき
A driverを「ジェントルマン(アマチュア)」、B/C/D driverを「エキスパート/プラチナ
(プロを含む上位ライセンス)」として区分する。個々のドライバーの正式なグレードでは
なく、レギュレーションに基づく推定であることに留意。
"""

from __future__ import annotations

import re
from datetime import date

import requests

from .common import REQUEST_TIMEOUT, USER_AGENT

STANDINGS_URL = "https://supertaikyu.com/race/standing.html"
ROUND_ENTRY_LIST_URL = "https://supertaikyu.com/race/round_{num:02d}.html"

# 2026年シーズンの各ラウンド最終日(この日を過ぎたら「開催済み」とみなす)。
# 直近の開催済みラウンドのエントリーリストを、現時点で確定しているドライバー
# 名簿とみなして使用する。
ROUND_END_DATES = [
    (1, date(2026, 3, 22)),
    (2, date(2026, 4, 19)),
    (3, date(2026, 6, 7)),
    (4, date(2026, 7, 5)),
    (5, date(2026, 7, 26)),
    (6, date(2026, 10, 25)),
    (7, date(2026, 11, 15)),
]


def _latest_completed_round(today: date | None = None) -> int | None:
    today = today or date.today()
    completed = [n for n, end in ROUND_END_DATES if today >= end]
    return max(completed) if completed else None

TEAMS = [
    {
        "key": "saitama_green_brave",
        "car_no": "052",
        "team_name": "埼玉Green Brave",
        "description": {
            "ja": "運営母体は埼玉トヨペット(トヨタ販売会社)。2013年発足の同社モータースポーツ推進部が運営し、"
            "チーム代表・チーフエンジニア・メカニックは全員が埼玉トヨペットの社員というディーラー直営チーム。"
            "ST-Zクラスで2023〜2025年に3連覇中(2026年は4連覇を目指す)。",
            "en": "Backed by Saitama Toyopet, a Toyota dealership. Run by the dealer's own Motorsports Promotion "
            "Division (est. 2013); the team principal, chief engineer, and mechanics are all Saitama Toyopet "
            "employees. Won the ST-Z class title three years running (2023-2025) and is chasing a fourth in 2026.",
        },
        "official_url": "https://supertaikyu.com/teams/2026_052.html",
        "photo": {
            "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/No.52_SAITAMA_GB_GR_Supra_GT4_after_ENEOS_Super_Taikyu_Series_2024_Empowered_by_BRIDGESTONE_Rd.5_SUZUKA_S-tai.jpg/960px-No.52_SAITAMA_GB_GR_Supra_GT4_after_ENEOS_Super_Taikyu_Series_2024_Empowered_by_BRIDGESTONE_Rd.5_SUZUKA_S-tai.jpg",
            "credit": "Tokumeigakarinoaoshima",
            "license": "CC BY-SA 4.0",
            "source_url": "https://commons.wikimedia.org/wiki/File:No.52_SAITAMA_GB_GR_Supra_GT4_after_ENEOS_Super_Taikyu_Series_2024_Empowered_by_BRIDGESTONE_Rd.5_SUZUKA_S-tai.jpg",
        },
    },
    {
        "key": "shade_racing",
        "car_no": "885",
        "team_name": "SHADE RACING",
        "description": {
            "ja": "運営母体は愛知県名古屋市の自動車内装部品サプライヤー「林テレンプ株式会社」。2015年に同社が設立した"
            "レーシングチームで、SUPER GT(GT300)にも参戦する。静岡県小山町の富士モータースポーツフォレストに"
            "自社ファクトリーを構える。",
            "en": "Backed by Hayashi Telempu Corporation, a Nagoya-based automotive interior parts supplier, which "
            "founded the team in 2015. Also competes in Super GT's GT300 class, and operates its own factory at "
            "Fuji Motorsports Forest in Oyama, Shizuoka.",
        },
        "official_url": "https://supertaikyu.com/teams/2026_885.html",
        "photo": {
            "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/No.885_SHADE_RACING_GR_SUPRA_GT4_after_2022_ENEOS_Super_Taikyu_Series_Powered_by_Hankook.jpg/960px-No.885_SHADE_RACING_GR_SUPRA_GT4_after_2022_ENEOS_Super_Taikyu_Series_Powered_by_Hankook.jpg",
            "credit": "Tokumeigakarinoaoshima",
            "license": "CC BY-SA 4.0",
            "source_url": "https://commons.wikimedia.org/wiki/File:No.885_SHADE_RACING_GR_SUPRA_GT4_after_2022_ENEOS_Super_Taikyu_Series_Powered_by_Hankook.jpg",
        },
    },
    {
        "key": "wing_hin_motorsports_japan",
        "car_no": "338",
        "team_name": "WING HIN MOTORSPORTS JAPAN",
        "description": {
            "ja": "マレーシアのトヨタ販売店系GRガレージ「GR Garage Balakong」を母体とする海外チーム。2026年に日本の"
            "モータースポーツへの参戦体制を発表し、マレーシアから遠征する形でスーパー耐久ST-Zクラスに参戦している。",
            "en": "An overseas team backed by GR Garage Balakong, a Toyota-dealership-affiliated GR Garage in "
            "Malaysia. Announced its entry into Japanese motorsport in 2026, campaigning the ST-Z class as a "
            "visiting team from Malaysia.",
        },
        "official_url": "https://supertaikyu.com/teams/2026_338.html",
    },
    {
        "key": "aoyama_gakuin_university",
        "car_no": "008",
        "team_name": "青山学院大学自動車部S耐チーム",
        "description": {
            "ja": "企業チームではなく、青山学院大学の学生自動車部が運営するクラブチーム。学生が主体となって車両整備・"
            "運営を行い、スーパー耐久ST-Zクラスに参戦する数少ない学生チームの一つ。",
            "en": "Not a corporate team — run by Aoyama Gakuin University's student automobile club. One of the few "
            "student-run teams competing in the ST-Z class, with students handling car preparation and operations.",
        },
        "official_url": "https://supertaikyu.com/teams/2026_008.html",
    },
    {
        "key": "team_noah",
        "car_no": "005",
        "team_name": "チームノア",
        "description": {
            "ja": "福岡拠点、代表は清瀧雄二。「九州にモータースポーツの元気を」をコンセプトに2018年設立された九州発の"
            "レーシングチーム。",
            "en": "Based in Fukuoka and led by team representative Yuji Seikitaki. Founded in 2018 under the "
            "concept of \"bringing motorsport energy to Kyushu.\"",
        },
        "official_url": "https://supertaikyu.com/teams/2026_005.html",
        "photo": {
            "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/No.5_MACH_SYAKEN_GR_Supra_GT4_EVO_after_ENEOS_Super_Taikyu_Series_2024_Empowered_by_BRIDGESTONE_Rd.5_SUZUKA_S-tai.jpg/960px-No.5_MACH_SYAKEN_GR_Supra_GT4_EVO_after_ENEOS_Super_Taikyu_Series_2024_Empowered_by_BRIDGESTONE_Rd.5_SUZUKA_S-tai.jpg",
            "credit": "Tokumeigakarinoaoshima",
            "license": "CC BY-SA 4.0",
            "source_url": "https://commons.wikimedia.org/wiki/File:No.5_MACH_SYAKEN_GR_Supra_GT4_EVO_after_ENEOS_Super_Taikyu_Series_2024_Empowered_by_BRIDGESTONE_Rd.5_SUZUKA_S-tai.jpg",
        },
    },
    {
        "key": "tracy_sports",
        "car_no": "038",
        "team_name": "TRACY SPORTS",
        "description": {
            "ja": "チームオーナーは兵頭昭一。「クルマを作るのが楽しい」を理念に37年にわたり自社でマシン製作からレース"
            "運営まで手掛ける老舗プライベーターチームで、多くのドライバーをSUPER GT等の上位カテゴリーへ送り出して"
            "きた人材育成にも定評がある。",
            "en": "Owned by Shoichi Hyodo. A veteran privateer team with 37 years of in-house car-building and race "
            "operations under the philosophy \"building cars is fun,\" also known for developing drivers who have "
            "gone on to Super GT and other top categories.",
        },
        "official_url": "https://supertaikyu.com/teams/2026_038.html",
    },
    {
        "key": "okabe_jidosha",
        "car_no": "015",
        "team_name": "OKABEJIDOSHA motorsport",
        "description": {
            "ja": "整備・販売を手掛ける岡部自動車を母体とするローカルチーム。詳細な運営体制は公表されていない。",
            "en": "A local team backed by Okabe Jidosha, a vehicle maintenance and sales company. Detailed "
            "organizational information is not publicly disclosed.",
        },
        "official_url": "https://supertaikyu.com/teams/2026_015.html",
    },
]


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def fetch_st_z_full_standings(limit: int = 15) -> dict:
    """ST-Zクラスの現在の順位表全体(順位/チーム名/使用車種/ポイント)を実データで取得する。

    Supra GT4(is_supra_gt4)は使用車種の文字列に"Supra"を含むかで判定する。
    """
    session = _session()
    try:
        resp = session.get(STANDINGS_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        html_text = resp.text

        block_match = re.search(r'<li class="mix st2">.*?</table>', html_text, re.S)
        if not block_match:
            return {"standings": [], "error": "ST-Zクラスの順位表が見つかりませんでした"}
        rows = re.findall(r"<tr>(.*?)</tr>", block_match.group(0), re.S)
        results: list[dict] = []
        for row in rows[1:]:
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            if len(cells) < 4 or not cells[0].isdigit():
                continue
            car_no, team, car = cells[1], cells[2], cells[3]
            points_raw = re.sub(r"[^\d.]", "", cells[-1]) or "0"
            results.append(
                {
                    "position": int(cells[0]),
                    "car_no": car_no,
                    "name": team,
                    "car": car,
                    "points": float(points_raw),
                    "is_supra_gt4": "supra" in car.lower(),
                }
            )
        rows_limited = results[:limit]
        return {
            "standings": rows_limited,
            "error": None if rows_limited else "現在、順位データが空です(シーズン開幕前などの可能性があります)",
        }
    except Exception as exc:  # noqa: BLE001
        return {"standings": [], "error": f"取得エラー: {exc}"}


def fetch_st_z_standings() -> dict[str, dict]:
    """ST-Zクラスの現在のシリーズ順位/ポイントを car_no -> {rank, points} で返す。

    参戦チーム一覧パネル(TEAMS)向けのcar_no引き当て用。実データ本体は
    fetch_st_z_full_standings() で取得し、ここではそれを car_no キーの辞書に変換する。
    """
    full = fetch_st_z_full_standings(limit=100)
    return {
        row["car_no"]: {"rank": row["position"], "points": row["points"]}
        for row in full["standings"]
    }


_SLOT_LABELS = ["A.driver", "B.driver", "C.driver", "D.driver", "E.driver", "F.driver"]
_TBN_MARKERS = ("tbn", "※", "&nbsp;", "")


def fetch_round_st_z_drivers(round_no: int) -> dict[str, list[dict]]:
    """指定ラウンドの公式エントリーリストから、ST-Zクラスの car_no -> ドライバー一覧 を返す。"""
    session = _session()
    try:
        resp = session.get(ROUND_ENTRY_LIST_URL.format(num=round_no), timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        html_text = resp.text

        block_match = re.search(r'Standing_Class"> ST-Z.*?</table>', html_text, re.S)
        if not block_match:
            return {}
        rows = re.findall(r"<tr>(.*?)</tr>", block_match.group(0), re.S)
        result: dict[str, list[dict]] = {}
        for row in rows[1:]:
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            if len(cells) < 5:
                continue
            car_no = cells[1].lstrip("0") or "0"
            driver_names = cells[4:]
            drivers: list[dict] = []
            for i, name in enumerate(driver_names):
                if i >= len(_SLOT_LABELS):
                    break
                if name.strip().lower() in _TBN_MARKERS:
                    continue
                drivers.append(
                    {
                        "slot": _SLOT_LABELS[i],
                        "name": name.strip(),
                        "grade": "gentleman" if i == 0 else "expert_platinum",
                    }
                )
            if drivers:
                result[car_no] = drivers
        return result
    except Exception:  # noqa: BLE001
        return {}


def fetch_season_st_z_drivers() -> dict[str, list[dict]]:
    """開幕(第1戦)から直近の開催済みラウンドまでの全エントリーリストを集計し、
    car_no -> 今シーズンここまでに参戦した全ドライバー(重複除去済み)を返す。

    同一人物が複数ラウンドでA driver(ジェントルマン)として登録されていれば
    ジェントルマン、一度もA driverでなければエキスパート/プラチナとして区分する。
    """
    latest = _latest_completed_round()
    if latest is None:
        return {}

    seen: dict[str, dict[str, dict]] = {}  # car_no -> {name: driver_dict}
    for round_no in range(1, latest + 1):
        round_drivers = fetch_round_st_z_drivers(round_no)
        for car_no, drivers in round_drivers.items():
            bucket = seen.setdefault(car_no, {})
            for driver in drivers:
                existing = bucket.get(driver["name"])
                if existing is None:
                    bucket[driver["name"]] = dict(driver)
                elif driver["grade"] == "gentleman":
                    # 一度でもA driver(ジェントルマン)として登録されていれば、その区分を優先する。
                    existing["grade"] = "gentleman"

    result: dict[str, list[dict]] = {}
    for car_no, bucket in seen.items():
        # ジェントルマン→エキスパート/プラチナの順に並べる。season集計のためA/B/C/Dの
        # ラウンド毎スロットは意味を持たないので、表示用のslotは付与しない。
        drivers = sorted(bucket.values(), key=lambda d: 0 if d["grade"] == "gentleman" else 1)
        for driver in drivers:
            driver.pop("slot", None)
        result[car_no] = drivers
    return result


def fetch() -> list[dict]:
    standings = fetch_st_z_standings()
    season_drivers = fetch_season_st_z_drivers()

    result: list[dict] = []
    for team in TEAMS:
        entry = dict(team)
        entry.setdefault("photo", None)
        lookup_no = team["car_no"].lstrip("0") or "0"
        st = standings.get(lookup_no, {})
        entry["rank"] = st.get("rank")
        entry["points"] = st.get("points")
        entry["drivers"] = season_drivers.get(lookup_no) or team.get("fallback_drivers", [])
        entry.pop("fallback_drivers", None)
        result.append(entry)
    return result

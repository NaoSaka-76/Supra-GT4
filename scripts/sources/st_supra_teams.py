"""日本のスーパー耐久 ST-Zクラスに参戦するGR Supra GT4チームの情報を集約する。

チームの背景(運営母体・オーナー)は手動収集した静的データとしてこのファイル内の
TEAMS定数に保持する(公式サイトに構造化データがないため)。一方、現在のシリーズ
ポイント/順位、およびドライバー名は公式サイト(supertaikyu.com)から毎回実データで
取得する。

ドライバーのプロ/アマ区分について: 公式サイトのチームページには個々のドライバーの
ライセンスグレード(プラチナ/エキスパート/ジェントルマン)は掲載されていない。
ただしスーパー耐久のレギュレーション上、ST-Zクラスは「A driverとして最低1名の
ジェントルマンドライバー登録」が義務付けられているため、この規則に基づき
A driverを「ジェントルマン(アマチュア)」、B/C/D driverを「エキスパート/プラチナ
(プロを含む上位ライセンス)」として区分する。個々のドライバーの正式なグレードでは
なく、レギュレーションに基づく推定であることに留意。
"""

from __future__ import annotations

import re
import html as html_module

import requests

from .common import REQUEST_TIMEOUT, USER_AGENT

STANDINGS_URL = "https://supertaikyu.com/race/standing.html"
TEAM_PAGE_URL = "https://supertaikyu.com/teams/2026_{num}.html"

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
        # 公式サイトのチームページは記事作成時点で伏字("※※※※※")のため、2026年参戦体制発表時の
        # 報道(autosport web)を情報源とした静的フォールバック。公式ページが更新され次第、
        # fetch_team_drivers() の実データが優先される。
        "fallback_drivers": [
            {"slot": "A.driver", "name": "前嶋 秀司", "grade": "gentleman"},
            {"slot": "B.driver", "name": "Azlan Naquib", "grade": "expert_platinum"},
            {"slot": "C.driver", "name": "Amer Harris", "grade": "expert_platinum"},
        ],
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


def fetch_st_z_standings() -> dict[str, dict]:
    """ST-Zクラスの現在のシリーズ順位/ポイントを car_no -> {rank, points} で返す。"""
    session = _session()
    try:
        resp = session.get(STANDINGS_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        html_text = resp.text

        block_match = re.search(r'<li class="mix st2">.*?</table>', html_text, re.S)
        if not block_match:
            return {}
        rows = re.findall(r"<tr>(.*?)</tr>", block_match.group(0), re.S)
        result: dict[str, dict] = {}
        for row in rows[1:]:
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            if len(cells) < 3 or not cells[0].isdigit():
                continue
            car_no = cells[1].lstrip("0") or "0"  # 表側は先頭ゼロなし表記("052"ではなく"52")
            points_raw = re.sub(r"[^\d.]", "", cells[-1]) or "0"
            result[car_no] = {"rank": int(cells[0]), "points": float(points_raw)}
        return result
    except Exception:  # noqa: BLE001
        return {}


def fetch_team_drivers(car_no: str) -> list[dict]:
    """チームページからドライバー名を取得し、A/B/C/D driverの並びで返す。

    公式サイトが未発表(「※※※※※」等の伏字)の場合はそのドライバーを除外する。
    """
    session = _session()
    try:
        resp = session.get(TEAM_PAGE_URL.format(num=car_no), timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        html_text = resp.text

        slots = re.findall(r'Team_Add_Dr_TXT">\s*([^<]*)<', html_text)
        names = re.findall(r'Team_Add_Dr_Name">([^<]*)<', html_text)
        drivers: list[dict] = []
        for slot, name in zip(slots, names):
            slot = slot.strip()
            name = html_module.unescape(name.strip())
            if not name or "※" in name:
                continue
            is_a_driver = slot.upper().startswith("A")
            drivers.append(
                {
                    "slot": slot,
                    "name": name,
                    "grade": "gentleman" if is_a_driver else "expert_platinum",
                }
            )
        return drivers
    except Exception:  # noqa: BLE001
        return []


def fetch() -> list[dict]:
    standings = fetch_st_z_standings()
    result: list[dict] = []
    for team in TEAMS:
        entry = dict(team)
        entry.setdefault("photo", None)
        lookup_no = team["car_no"].lstrip("0") or "0"
        st = standings.get(lookup_no, {})
        entry["rank"] = st.get("rank")
        entry["points"] = st.get("points")
        drivers = fetch_team_drivers(team["car_no"])
        entry["drivers"] = drivers or team.get("fallback_drivers", [])
        entry.pop("fallback_drivers", None)
        result.append(entry)
    return result

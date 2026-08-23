(function () {
  "use strict";

  var LANG_STORAGE_KEY = "supraGt4WatchLang";

  var ICONS = {
    flag:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3v18"/><path d="M5 4h14l-3 3.5 3 3.5H5z"/></svg>',
    gear:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 13a1.7 1.7 0 000-2l1.4-1.2-2-3.4-1.8.6a1.7 1.7 0 00-1.7-1L15 4h-6l-.3 1.9a1.7 1.7 0 00-1.7 1l-1.8-.6-2 3.4L4.6 11a1.7 1.7 0 000 2l-1.4 1.2 2 3.4 1.8-.6a1.7 1.7 0 001.7 1L9 20h6l.3-1.9a1.7 1.7 0 001.7-1l1.8.6 2-3.4z"/></svg>',
    play:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M10 8.5l6 3.5-6 3.5z" fill="currentColor" stroke="none"/></svg>',
    chat:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H8l-4 4z"/></svg>',
    alert:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4l9.5 16H2.5z"/><line x1="12" y1="10" x2="12" y2="14.5"/><circle cx="12" cy="17.3" r="0.9" fill="currentColor" stroke="none"/></svg>',
    car:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 16.5V12l1.8-5A2 2 0 017.7 5.5h8.6a2 2 0 011.9 1.5l1.8 5v4.5"/><path d="M4 16.5h16"/><path d="M4 16.5v2.3a1 1 0 001 1h1.2a1 1 0 001-1v-2.3"/><path d="M16.8 16.5v2.3a1 1 0 001 1H19a1 1 0 001-1v-2.3"/><circle cx="7.5" cy="13.2" r="1.1" fill="currentColor" stroke="none"/><circle cx="16.5" cy="13.2" r="1.1" fill="currentColor" stroke="none"/></svg>',
  };

  // 表示順: GT4参戦車両一覧 → GT4カテゴリー最新トピックス → YouTube → SNS → お客様の声/クレーム
  // → GR Supra GT4参戦レース(この順にboard内へ並ぶ)。gt4_carsはdata.sections経由ではなく
  // 別JSON(gt4_cars.json)から読み込むため、render()内で先頭に個別配置する。
  var LAYOUT = [
    { key: "gt4_topics", size: "full", icon: "gear" },
    { key: "youtube", size: "full", icon: "play" },
    { key: "social_buzz", size: "full", icon: "chat" },
    { key: "complaints", size: "full", icon: "alert" },
    { key: "motorsports", size: "full", icon: "flag" },
  ];

  // ---- i18n --------------------------------------------------------------
  // 画面の文言(パネル見出し・ボタン・注記・地域/シリーズ名等)はここで一元管理する。
  // data/latest.json 側の label/note は日本語固定で生成されるため、表示には使わず
  // 安定した key(section/region/series key)をもとにこの辞書から引く。
  // ニュース記事・動画のタイトルなど集約コンテンツ自体は翻訳しない(原文のまま)。

  var I18N = {
    ja: {
      loading: "データを取得しています…",
      updateInterval: "30分毎",
      chipLabel: "自動更新",
      lastUpdatedPrefix: "最終更新: ",
      lastUpdatedUnknown: "不明",
      fetchErrorPrefix: "ダッシュボードデータの読み込みに失敗しました(",
      fetchErrorSuffix: ")。",
      statusFetchFailed: "更新情報を取得できませんでした",
      footer:
        "本ダッシュボードは公開情報源(Googleニュース検索・YouTube検索結果・各シリーズ公式サイト)を自動集計した非公式のモニタリングツールです。" +
        "トヨタ自動車の公式発表とは異なる場合があります。X/Facebookの投稿本体、および社内クレームシステムのデータは含まれません。" +
        "ポジティブ/ネガティブ表示は見出し文のみに基づく自動推定(簡易辞書・VADER)であり、参考値です。" +
        "モータースポーツ(日本・アジア/米国/欧州/オセアニア/中東)のレース結果・ランキングはニュース記事ベースの速報、" +
        "または各シリーズ公式サイトへのリンクです。正式な記録は各シリーズ公式サイトをご確認ください。",
      statTotal: "本日の総情報件数",
      statYoutube: "YouTube動画(Supra GT4・競合GT4)",
      statMotorsports: "参戦レース関連話題(5地域・{n}シリーズ)",
      unitItems: "件",
      unitVideos: "本",
      unitSeries: "シリーズ",
      emptyGeneric: "現在、該当する情報はありません。",
      emptyGroup: "該当情報なし",
      emptySchedule: "日程情報を取得できませんでした。",
      tabLatest: "最新順",
      tabBuzz: "話題順",
      tabYoutubeNew: "新着順",
      tabYoutubePopular: "話題順",
      groupTopics: "トピックス",
      groupResults: "最新レース結果",
      groupStandings: "ランキング関連ニュース",
      groupSchedule: "レース日程",
      groupRanking: "シリーズランキング",
      nextRace: "次戦",
      linkCalendar: "公式カレンダーを見る ↗",
      linkStandings: "公式ランキングを見る ↗",
      linkOfficial: "公式サイトを見る ↗",
      scheduleLinkNote: "日程データの構造が不安定なため一覧化を見送っています。公式カレンダーは以下のリンクからご確認ください。",
      standingsNoteSuperTaikyu:
        "スーパー耐久 ST-Zクラス チームランキング(公式サイト実データ)。GR Supra GT4で参戦するチームには" +
        "目印を付けています。",
      standingsNoteGt4America:
        "GT4 America \"Silver Teams\" チームランキング(公式サイト実データ)。各レースの完全結果ページから使用車種を補完しており、" +
        "Toyota GR Supra GT4で参戦するチームには目印を付けています。",
      standingsNoteGtWorldChallengeAsia:
        "GT World Challenge Asia GT3 Teams Championship(公式サイト実データ)。GT3主体のシリーズのため" +
        "Supra GT4(GT4クラス)のハイライトは対象外です。",
      standingsNoteGtWorldChallengeAmerica:
        "GT World Challenge America Pro-Am Teams(公式サイト実データ)。GT3主体のシリーズのため" +
        "Supra GT4(GT4クラス)のハイライトは対象外です。",
      standingsNoteInterProtoSeries:
        "SUPRA[PROFESSIONAL]クラス ドライバーランキング(公式サイト実データ)。全車GR Supra GT4 EVOの" +
        "ワンメイククラスのため、特定車両のハイライトはありません。",
      standingsNoteSroJapanCup:
        "SRO Japan Cup GT4 Teams Championship(公式サイト実データ)。順位表に使用車種の記載がないため、" +
        "Supra GT4のハイライトは行っていません。",
      standingsNoteBritishGt4:
        "British GT Championship GT4 Teams Championship(公式サイト実データ)。順位表に使用車種の記載がないため、" +
        "Supra GT4のハイライトは行っていません。",
      standingsNoteGt4EuropeanSeries:
        "GT4 European Series PRO-AMクラス ランキング(公式サイト実データ)。順位表に使用車種の記載がないため、" +
        "Supra GT4のハイライトは行っていません。",
      standingsNoteFrenchGt4Cup:
        "French GT4 Cup(FFSA GT)ランキング(公式サイト実データ)。順位表に使用車種の記載がないため、" +
        "Supra GT4のハイライトは行っていません。",
      standingsNoteGtWorldChallengeAustralia:
        "GT World Challenge Australia Overall Teams Championship(公式サイト実データ)。GT3主体のシリーズのため" +
        "Supra GT4(GT4クラス)のハイライトは対象外です。",
      standingsNoteGt4Australia:
        "Monochrome GT4 Australia Series Overall Teams Championship(公式サイト実データ)。順位表に使用車種の記載がないため、" +
        "Supra GT4のハイライトは行っていません。",
      standingsNoteDefault:
        "このシリーズの公式サイトは順位表の構造を安定的に解釈できないため、グラフ化は行っていません。" +
        "「公式ランキングを見る」からご確認ください。",
      standingsNoteError: "ランキングの取得中にエラーが発生しました。「公式ランキングを見る」からご確認ください。",
      sentimentPositive: "ポジティブ",
      sentimentNegative: "ネガティブ",
      sentimentReasonsPrefix: "判定根拠: ",
      sentimentSuffixPositive: " という語がポジティブと判定されました",
      sentimentSuffixNegative: " という語がネガティブと判定されました",
      titleUnknown: "(タイトル不明)",
      photoCredit: "写真: ",
      viaCommons: "、Wikimedia Commonsより",
      analysisUpdatedPrefix: "分析更新: ",
      sections: {
        st_supra_teams: {
          title: "スーパー耐久 ST-Zクラス Supra GT4参戦チーム",
          note:
            "2026年シーズンのスーパー耐久ST-Zクラスに参戦する、GR Supra GT4を使用する全チームを掲載。" +
            "順位/ポイントは公式サイト(supertaikyu.com)から毎回実データで取得しています。ドライバーは、" +
            "開幕戦から直近の開催済みラウンドまでの全公式エントリーリストを集計し、今シーズンここまでに" +
            "参戦した全ドライバーを重複なく掲載しています。区分は、ST-Zクラスのレギュレーション上A driver" +
            "にジェントルマン(アマチュア)登録が義務付けられていることに基づく推定であり(1度でもA driver" +
            "登録があればジェントルマンと表示)、個々のライセンスグレードを公式に確認したものではありません。",
        },
        motorsports: {
          title: "GR Supra GT4 参戦レース(地域別・全19シリーズ)",
          note:
            "トピックス/レース結果はニュース記事ベースで集約しています。スーパー耐久(日本・アジア)は年間スケジュール、" +
            "米国のGT4 America(Silver Teams)はチームランキングを公式サイトの実データで取得しています" +
            "(他シリーズを図示しない理由は各カード内に記載)。",
        },
        gt4_topics: {
          title: "GT4カテゴリー最新トピックス",
          note:
            "GT4ホモロゲーション/レギュレーション、競合GT4(BMW・Mercedes-AMG・Porsche・Ford・Aston Martin・Audi・McLaren等)の" +
            "開発・アップデート、技術情報、Supra GT4や競合車の不具合情報をカテゴリー別バッジ付きで集約しています。",
        },
        youtube_popular: { title: "YouTube 人気動画(Supra GT4・競合GT4)" },
        youtube_new: { title: "YouTube 新着動画(Supra GT4・競合GT4)" },
        youtube: { title: "YouTube動画(Supra GT4・競合GT4)" },
        social_buzz: {
          title: "SNSでの話題(X/Facebook 代替指標)",
          note:
            "X/Facebookの公式APIキーが未設定のため、投稿本体は取得できません。ニュース・ブログでの言及数を話題性の代替指標として" +
            "表示しています。「話題順」は検索結果内での上位表示度を注目度の代替指標として用いています" +
            "(実際のSNS拡散数やエンゲージメント数ではありません)。",
        },
        complaints: {
          title: "Supra GT4 お客様の声・クレーム関連情報",
          note:
            "社内クレーム管理システムとは未連携です。ニュース報道(リコール等)で公開されている情報のみを集約した簡易" +
            "モニタリングです。「話題順」は検索結果内での上位表示度を注目度の代替指標として用いています" +
            "(実際のSNS拡散数やエンゲージメント数ではありません)。",
        },
        gt4_cars: { title: "GT4参戦車両一覧", analysisTitle: "GT4グローバル戦況・BOP動向分析" },
      },
      regions: {
        japan_asia: "日本・アジア",
        us: "米国",
        europe: "欧州",
        oceania: "オセアニア",
        middle_east: "中東",
      },
      series: {
        gt_world_challenge_asia: {
          label: "GT World Challenge Asia",
          desc: "SRO主催のアジア地域GT3統一シリーズ。2024年からGT4クラスはSRO Japan Cupに移管されたため、本シリーズ自体はGT3が主体。",
        },
        super_taikyu: {
          label: "スーパー耐久 ST-Zクラス(日本)",
          desc: "日本の人気耐久レースシリーズ。GT4規定車両が属するST-Zクラスがあり、GR Supra GT4は2023年にクラスチャンピオンを獲得するなど高い戦闘力を発揮している。",
        },
        inter_proto_series: {
          label: "インタープロトシリーズ SUPRAクラス(日本)",
          desc: "富士スピードウェイを舞台にプロとジェントルマンドライバーがマシンをシェアして戦うワンメイクレース。GR Supra GT4 EVOを使用する「SUPRAクラス」が設置されている。",
        },
        sro_japan_cup: {
          label: "SRO Japan Cup GT4クラス(日本)",
          desc: "日本国内でGT3/GTC/GT4規定車両が混走するSRO主催シリーズ。2024年からGT World Challenge AsiaのGT4クラスを引き継いだ。",
        },
        sro_gt_cup_china: {
          label: "SRO GT Cup(中国)",
          desc: "2025年に開幕した中国拠点のGT4専用スプリントシリーズ。上海・北京・珠海など主要サーキットを転戦する。",
        },
        gt_world_challenge_america: {
          label: "GT World Challenge America",
          desc: "北米のGT3主体の国際格式シリーズ。GT4 Americaと同一の大会ウィークエンドで開催される。",
        },
        gt4_america: {
          label: "Pirelli/Fanatec GT4 America(Silver Teams)",
          desc: "SRO Motorsports America主催のGT4専用シリーズ。Silver/Pro-Am/Amの3クラスに分かれ、GR Supra GT4は米国でもクラスチャンピオンを獲得した実績を持つ。",
        },
        imsa_michelin_pilot_challenge: {
          label: "IMSA Michelin Pilot Challenge(GSクラス)",
          desc: "IMSA主催の耐久シリーズにおけるGT4規定車両クラス(GS)。デイトナ24時間などの伝統レースを含み、GR Supra GT4 EVO2は2026年にも優勝実績を残している。",
        },
        gt_world_challenge_europe: {
          label: "GT World Challenge Europe",
          desc: "スパ24時間などを含む欧州最高峰のGT3シリーズ。GT4 European Seriesは同一大会ウィークエンドの併催カテゴリー。",
        },
        gt4_european_series: {
          label: "GT4 European Series",
          desc: "SRO主催の汎欧州GT4選手権。GR Supra GT4は欧州でもクラスチャンピオンを獲得しており、競争力の高いシリーズ。",
        },
        british_gt4: {
          label: "British GT Championship(GT4クラス)",
          desc: "英国伝統のGT選手権に設置されたGT4クラス。スプリント/耐久が混在し、参戦コンストラクターの層が厚い。",
        },
        french_gt4_cup: {
          label: "French GT4 Cup",
          desc: "フランス国内で開催されるSRO主催のGT4カップ。スパ・スピードウィークなど国際色のあるラウンドも含む。",
        },
        gt4_italian_series: {
          label: "GT4 Italian Series",
          desc: "2026年にACI SportとSROの提携で新設されたイタリア国内GT4選手権。ミサノ・モンツァ等の名門サーキットを転戦。",
        },
        adac_gt4_germany: {
          label: "ADAC GT4 Germany",
          desc: "ドイツ国内のDTM併催GT4選手権。ADAC GT Mastersへのステップアップを目指す若手ドライバーの登竜門。",
        },
        nls_nuerburgring: {
          label: "ニュルブルクリンク NLS・24h(SP10クラス)",
          desc: "ニュルブルクリンク・ノルドシュライフェを舞台にした伝統の耐久レースシリーズ。GT4車両はSP10クラスに統合され、GR Supra GT4は過去にクラスチャンピオンを獲得している。",
        },
        gt4_winter_series: {
          label: "GT4 Winter Series(イベリア半島)",
          desc: "12月〜3月にイベリア半島(スペイン・ポルトガル)で開催される冬季限定のGT4シリーズ。オフシーズンの実戦テストの場として活用される。",
        },
        gt_world_challenge_australia: {
          label: "GT World Challenge Australia",
          desc: "オセアニア地域のGT3主体シリーズ。GT4 Australia(Monochrome GT4 Australia)と同一大会ウィークエンドで開催される。",
        },
        gt4_australia: {
          label: "Monochrome GT4 Australia Series",
          desc: "SRO主催のオーストラリア/ニュージーランドGT4選手権。GR Supra GT4はTOYOTA GAZOO Racing Australiaのサポートを受け参戦している。",
        },
        "24h_series_middle_east": {
          label: "24H Series Middle East(GT4クラス)",
          desc: "Creventic主催、ドバイ24時間などを含む中東の耐久レースシリーズ。GT3/GT4等が混走するマルチクラス編成。",
        },
      },
      categories: {
        homologation: "ホモロゲーション",
        regulation: "レギュレーション",
        competitor: "競合GT4の開発",
        technical: "技術情報",
        issue: "不具合情報",
      },
      carSpecs: {
        engine: "エンジン",
        power: "最高出力",
        torque: "最大トルク",
        weight: "車両重量",
        transmission: "トランスミッション",
      },
      teamDrivers: "ドライバー",
      teamResults: "ST-Zクラス戦績",
      teamResultsRank: "現在{rank}位 / {points}pt(全12台中)",
      teamResultsUnknown: "順位データを取得できませんでした",
      teamDriversUnannounced: "ドライバー未発表",
      driverGradeGentleman: "ジェントルマン(アマ)",
      driverGradeExpertPlatinum: "エキスパート/プラチナ",
      carNoLabel: "No.",
    },
    en: {
      loading: "Loading data…",
      updateInterval: "Every 30 min",
      chipLabel: "auto-update",
      lastUpdatedPrefix: "Last updated: ",
      lastUpdatedUnknown: "unknown",
      fetchErrorPrefix: "Failed to load dashboard data (",
      fetchErrorSuffix: ").",
      statusFetchFailed: "Could not fetch update status",
      footer:
        "This dashboard is an unofficial monitoring tool that automatically aggregates public sources " +
        "(Google News search, YouTube search results, and each series' official site). It may differ from Toyota Motor " +
        "Corporation's official announcements. It does not include actual X/Facebook posts or internal complaint-system data. " +
        "Positive/negative labels are automatic estimates based on headline text only (a simple lexicon and VADER) and are " +
        "reference values only. Motorsports race results and rankings (Japan/Asia, US, Europe, Oceania, Middle East) are " +
        "either news-based bulletins or links to each series' official site. Please check each series' official site for the " +
        "official record.",
      statTotal: "Total items today",
      statYoutube: "YouTube Videos (Supra GT4 & Rival GT4)",
      statMotorsports: "Race-related topics (5 regions, {n} series)",
      unitItems: "items",
      unitVideos: "videos",
      unitSeries: "series",
      emptyGeneric: "No matching information right now.",
      emptyGroup: "Nothing to show",
      emptySchedule: "Could not fetch schedule information.",
      tabLatest: "Latest",
      tabBuzz: "Trending",
      tabYoutubeNew: "Newest",
      tabYoutubePopular: "Trending",
      groupTopics: "Topics",
      groupResults: "Latest Results",
      groupStandings: "Ranking News",
      groupSchedule: "Race Schedule",
      groupRanking: "Series Ranking",
      nextRace: "Next round",
      linkCalendar: "View official calendar ↗",
      linkStandings: "View official ranking ↗",
      linkOfficial: "Visit official site ↗",
      scheduleLinkNote: "The schedule data structure is unstable, so it isn't listed here. Please check the official calendar via the link below.",
      standingsNoteSuperTaikyu:
        "Super Taikyu ST-Z class team ranking (live data from the official site). Teams running the Toyota GR Supra " +
        "GT4 are highlighted.",
      standingsNoteGt4America:
        "GT4 America \"Silver Teams\" team ranking (live data from the official site). Car models are filled in from each " +
        "race's full results page, and teams running the Toyota GR Supra GT4 are highlighted.",
      standingsNoteGtWorldChallengeAsia:
        "GT World Challenge Asia GT3 Teams Championship (live data from the official site). Since this is a " +
        "GT3-based series, there's no Supra GT4 (GT4-class) highlighting.",
      standingsNoteGtWorldChallengeAmerica:
        "GT World Challenge America Pro-Am Teams (live data from the official site). Since this is a GT3-based " +
        "series, there's no Supra GT4 (GT4-class) highlighting.",
      standingsNoteInterProtoSeries:
        "SUPRA [PROFESSIONAL] class driver ranking (live data from the official site). Since every car is a GR " +
        "Supra GT4 EVO in this one-make class, there's no single-car highlighting.",
      standingsNoteSroJapanCup:
        "SRO Japan Cup GT4 Teams Championship (live data from the official site). Car models aren't listed in the " +
        "standings table, so there's no Supra GT4 highlighting.",
      standingsNoteBritishGt4:
        "British GT Championship GT4 Teams Championship (live data from the official site). Car models aren't " +
        "listed in the standings table, so there's no Supra GT4 highlighting.",
      standingsNoteGt4EuropeanSeries:
        "GT4 European Series PRO-AM class ranking (live data from the official site). Car models aren't listed in " +
        "the standings table, so there's no Supra GT4 highlighting.",
      standingsNoteFrenchGt4Cup:
        "French GT4 Cup (FFSA GT) ranking (live data from the official site). Car models aren't listed in the " +
        "standings table, so there's no Supra GT4 highlighting.",
      standingsNoteGtWorldChallengeAustralia:
        "GT World Challenge Australia Overall Teams Championship (live data from the official site). Since this " +
        "is a GT3-based series, there's no Supra GT4 (GT4-class) highlighting.",
      standingsNoteGt4Australia:
        "Monochrome GT4 Australia Series Overall Teams Championship (live data from the official site). Car models " +
        "aren't listed in the standings table, so there's no Supra GT4 highlighting.",
      standingsNoteDefault:
        "This series' official site ranking table can't be parsed reliably, so it isn't charted here. Please check via " +
        "\"View official ranking.\"",
      standingsNoteError: "An error occurred while fetching the ranking. Please check via \"View official ranking.\"",
      sentimentPositive: "Positive",
      sentimentNegative: "Negative",
      sentimentReasonsPrefix: "Detected words: ",
      sentimentSuffixPositive: " — classified as positive",
      sentimentSuffixNegative: " — classified as negative",
      titleUnknown: "(untitled)",
      photoCredit: "Photo: ",
      viaCommons: ", via Wikimedia Commons",
      analysisUpdatedPrefix: "Analysis updated: ",
      sections: {
        st_supra_teams: {
          title: "Super Taikyu ST-Z Class — Supra GT4 Teams",
          note:
            "All teams running a GR Supra GT4 in the 2026 Super Taikyu ST-Z class. Standings/points are fetched live " +
            "from the official site (supertaikyu.com) on every update. Drivers are aggregated from every official " +
            "entry list published so far this season (round 1 through the latest completed round), listing everyone " +
            "who has raced for that car with no duplicates. Grading is inferred from the ST-Z regulation requiring a " +
            "Gentleman (amateur) driver in the A-driver slot (anyone registered as A-driver in any round is shown as " +
            "Gentleman) — it is not an officially confirmed individual license grade.",
        },
        motorsports: {
          title: "GR Supra GT4 Races (by Region, 19 Series)",
          note:
            "Topics and race results are aggregated from news articles. Super Taikyu (Japan/Asia) provides a real season " +
            "schedule, and GT4 America (Silver Teams, US) provides a real team-ranking chart, both sourced directly from " +
            "official sites (reasons other series aren't charted are noted on each card).",
        },
        gt4_topics: {
          title: "Latest GT4 Category Topics",
          note:
            "Aggregates GT4 homologation/regulation news, rival GT4 development and updates (BMW, Mercedes-AMG, Porsche, " +
            "Ford, Aston Martin, Audi, McLaren, etc.), technical information, and defect/issue reports for Supra GT4 and " +
            "rivals, tagged with category badges.",
        },
        youtube_popular: { title: "YouTube Popular Videos (Supra GT4 & Rival GT4)" },
        youtube_new: { title: "YouTube Latest Videos (Supra GT4 & Rival GT4)" },
        youtube: { title: "YouTube Videos (Supra GT4 & Rival GT4)" },
        social_buzz: {
          title: "Social Media Buzz (X/Facebook Proxy)",
          note:
            "X/Facebook official API keys aren't configured, so posts themselves can't be retrieved. News/blog mention " +
            "counts are shown as a proxy for buzz. \"Trending\" order uses search-result ranking as a proxy for attention " +
            "(not actual share/engagement counts).",
        },
        complaints: {
          title: "Supra GT4 Customer Feedback & Complaints",
          note:
            "Not connected to any internal complaint-management system. This is a lightweight monitor aggregating only " +
            "publicly reported news (e.g. recalls). \"Trending\" order uses search-result ranking as a proxy for attention " +
            "(not actual share/engagement counts).",
        },
        gt4_cars: { title: "GT4 Car Catalog", analysisTitle: "Global GT4 Landscape & BOP Trend Analysis" },
      },
      regions: {
        japan_asia: "Japan / Asia",
        us: "United States",
        europe: "Europe",
        oceania: "Oceania",
        middle_east: "Middle East",
      },
      series: {
        gt_world_challenge_asia: {
          label: "GT World Challenge Asia",
          desc: "An SRO-organized GT3 series spanning Asia. GT4 was folded into the SRO Japan Cup in 2024, so this series itself is now GT3-focused.",
        },
        super_taikyu: {
          label: "Super Taikyu ST-Z Class (Japan)",
          desc: "Japan's popular endurance racing series. GT4-spec cars compete in the ST-Z class, where the GR Supra GT4 won the class championship in 2023, showing strong competitiveness.",
        },
        inter_proto_series: {
          label: "Inter Proto Series SUPRA Class (Japan)",
          desc: "A one-make race at Fuji Speedway where a pro driver and a gentleman driver share the same car. Its \"SUPRA class\" is run exclusively with GR Supra GT4 EVO cars.",
        },
        sro_japan_cup: {
          label: "SRO Japan Cup GT4 Class (Japan)",
          desc: "An SRO-organized series in Japan running GT3/GTC/GT4-spec cars together. It absorbed GT World Challenge Asia's GT4 class from 2024.",
        },
        sro_gt_cup_china: {
          label: "SRO GT Cup (China)",
          desc: "A China-based GT4-only sprint series launched in 2025, touring major circuits including Shanghai, Beijing, and Zhuhai.",
        },
        gt_world_challenge_america: {
          label: "GT World Challenge America",
          desc: "North America's international GT3-based series, held on the same event weekends as GT4 America.",
        },
        gt4_america: {
          label: "Pirelli/Fanatec GT4 America (Silver Teams)",
          desc: "A GT4-only series run by SRO Motorsports America, split into Silver/Pro-Am/Am classes. The GR Supra GT4 has also won a class championship here in the US.",
        },
        imsa_michelin_pilot_challenge: {
          label: "IMSA Michelin Pilot Challenge (GS Class)",
          desc: "The GT4-spec class (GS) of IMSA's own endurance series, which includes classic races like the Daytona 24 Hours. The GR Supra GT4 EVO2 has scored wins as recently as 2026.",
        },
        gt_world_challenge_europe: {
          label: "GT World Challenge Europe",
          desc: "Europe's top-tier GT3 series, including the Spa 24 Hours. The GT4 European Series runs as a support category on the same event weekends.",
        },
        gt4_european_series: {
          label: "GT4 European Series",
          desc: "SRO's pan-European GT4 championship. A highly competitive series where the GR Supra GT4 has also taken class championships in Europe.",
        },
        british_gt4: {
          label: "British GT Championship (GT4 Class)",
          desc: "The GT4 class within Britain's storied GT championship, mixing sprint and endurance formats with a deep field of constructors.",
        },
        french_gt4_cup: {
          label: "French GT4 Cup",
          desc: "An SRO-organized GT4 cup held in France, including internationally flavored rounds such as the Spa Speedweek.",
        },
        gt4_italian_series: {
          label: "GT4 Italian Series",
          desc: "A new Italian GT4 championship launched in 2026 through a partnership between ACI Sport and SRO, touring historic circuits like Misano and Monza.",
        },
        adac_gt4_germany: {
          label: "ADAC GT4 Germany",
          desc: "A German GT4 championship run alongside DTM weekends, serving as a proving ground for young drivers aiming to step up to ADAC GT Masters.",
        },
        nls_nuerburgring: {
          label: "Nürburgring NLS / 24h (SP10 Class)",
          desc: "A storied endurance series held on the Nürburgring Nordschleife. GT4 cars are consolidated into the SP10 class, where the GR Supra GT4 has previously won the class title.",
        },
        gt4_winter_series: {
          label: "GT4 Winter Series (Iberian Peninsula)",
          desc: "A winter-only GT4 series held December through March on the Iberian Peninsula (Spain and Portugal), used as an off-season proving ground.",
        },
        gt_world_challenge_australia: {
          label: "GT World Challenge Australia",
          desc: "Oceania's GT3-based series, held on the same event weekends as GT4 Australia (Monochrome GT4 Australia).",
        },
        gt4_australia: {
          label: "Monochrome GT4 Australia Series",
          desc: "SRO's Australia/New Zealand GT4 championship. The GR Supra GT4 competes here with support from Toyota Gazoo Racing Australia.",
        },
        "24h_series_middle_east": {
          label: "24H Series Middle East (GT4 Class)",
          desc: "A Creventic-run endurance series in the Middle East including the Dubai 24 Hours, run as a multi-class field alongside GT3 and other categories.",
        },
      },
      categories: {
        homologation: "Homologation",
        regulation: "Regulations",
        competitor: "Rival GT4 Development",
        technical: "Technical",
        issue: "Issues & Defects",
      },
      carSpecs: {
        engine: "Engine",
        power: "Max Power",
        torque: "Max Torque",
        weight: "Weight",
        transmission: "Transmission",
      },
      teamDrivers: "Drivers",
      teamResults: "ST-Z Class Results",
      teamResultsRank: "Currently P{rank} / {points}pt (of 12 cars)",
      teamResultsUnknown: "Standings unavailable",
      teamDriversUnannounced: "Drivers not yet announced",
      driverGradeGentleman: "Gentleman (Am)",
      driverGradeExpertPlatinum: "Expert/Platinum",
      carNoLabel: "No.",
    },
  };

  var LANG = (function () {
    try {
      var saved = window.localStorage.getItem(LANG_STORAGE_KEY);
      if (saved === "ja" || saved === "en") return saved;
    } catch (e) {
      /* localStorage unavailable */
    }
    return "ja";
  })();

  function t() {
    return I18N[LANG] || I18N.ja;
  }

  // JSON側のバイリンガルフィールド({ja, en})、または通常の文字列(固有名詞等)を
  // 現在の言語に応じて解決する。
  function pick(value) {
    if (value && typeof value === "object" && !Array.isArray(value)) {
      return value[LANG] || value.ja || value.en || "";
    }
    return value || "";
  }

  var board = document.getElementById("board");
  var statsEl = document.getElementById("stats");
  var lastUpdatedEl = document.getElementById("last-updated");
  var statusDot = document.getElementById("status-dot");
  var chipLabelEl = document.getElementById("chip-label");
  var updateIntervalChipEl = document.getElementById("update-interval-chip");
  var loadingEl = document.getElementById("loading");
  var footerTextEl = document.getElementById("footer-text");
  var langToggleEl = document.getElementById("lang-toggle");

  var lastData = null;
  var lastCarsData = null;

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function formatPublished(raw) {
    if (!raw) return "";
    var parsed = new Date(raw);
    if (!isNaN(parsed.getTime()) && /\d{4}/.test(raw)) {
      return parsed.toLocaleString(LANG === "en" ? "en-US" : "ja-JP", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    }
    return raw;
  }

  function sentimentPill(sentiment) {
    if (!sentiment || sentiment.label === "neutral") return null;
    var s = t();
    var isPositive = sentiment.label === "positive";
    var pill = el(
      "span",
      "sentiment-pill sentiment-pill--" + sentiment.label,
      (isPositive ? "▲ " : "▼ ") + (isPositive ? s.sentimentPositive : s.sentimentNegative)
    );
    var reasons = sentiment.reasons || [];
    if (reasons.length > 0) {
      var tip = s.sentimentReasonsPrefix + reasons.join(" / ") + (isPositive ? s.sentimentSuffixPositive : s.sentimentSuffixNegative);
      pill.setAttribute("data-tip", tip);
      pill.tabIndex = 0;
    }
    return pill;
  }

  function buildItem(item) {
    var s = t();
    var sentimentLabel = item.sentiment ? item.sentiment.label : "neutral";
    var a = el("a", "item item--" + sentimentLabel);
    a.href = item.url || "#";
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    if (!item.url) {
      a.removeAttribute("href");
      a.style.cursor = "default";
    }

    if (item.thumbnail) {
      var img = el("img", "item__thumb");
      img.src = item.thumbnail;
      img.alt = "";
      img.loading = "lazy";
      a.appendChild(img);
    }

    var body = el("div", "item__body");
    body.appendChild(el("span", "item__title", item.title || s.titleUnknown));

    var meta = el("div", "item__meta");
    if (item.category) {
      var categoryLabel = s.categories[item.category];
      if (categoryLabel) meta.appendChild(el("span", "topic-chip topic-chip--" + item.category, categoryLabel));
    }
    var pill = sentimentPill(item.sentiment);
    if (pill) meta.appendChild(pill);
    if (item.source) meta.appendChild(el("span", null, item.source));
    var published = formatPublished(item.published);
    if (published) meta.appendChild(el("span", null, published));
    if (item.view_count_text) {
      meta.appendChild(el("span", "item__metric", item.view_count_text));
    }
    body.appendChild(meta);
    a.appendChild(body);

    return a;
  }

  function buildList(items) {
    var list = el("ul", "panel__list");
    items.forEach(function (item) {
      var li = el("li");
      li.appendChild(buildItem(item));
      list.appendChild(li);
    });
    return list;
  }

  function buildPanelHeader(icon, label, count) {
    var header = el("div", "panel__header");
    var iconWrap = el("div", "panel__icon");
    iconWrap.innerHTML = ICONS[icon] || "";
    header.appendChild(iconWrap);
    header.appendChild(el("h2", "panel__title", label));
    if (count !== undefined) header.appendChild(el("span", "panel__count", count + " " + t().unitItems));
    return header;
  }

  function buildGenericPanel(icon, sectionKey, section, size) {
    var s = t();
    var meta = s.sections[sectionKey] || {};
    var panel = el("section", "panel panel--" + size);
    var items = section.items || [];
    panel.appendChild(buildPanelHeader(icon, meta.title || sectionKey, items.length));

    if (meta.note) panel.appendChild(el("p", "panel__note", meta.note));

    if (items.length === 0) {
      panel.appendChild(el("p", "panel__empty", s.emptyGeneric));
      return panel;
    }
    panel.appendChild(buildList(items));
    return panel;
  }

  function buildTabbedPanel(icon, sectionKey, section) {
    var s = t();
    var meta = s.sections[sectionKey] || {};
    var panel = el("section", "panel panel--full");
    var latestItems = section.items || [];
    var buzzItems = section.items_buzz || [];
    panel.appendChild(buildPanelHeader(icon, meta.title || sectionKey, latestItems.length));
    if (meta.note) panel.appendChild(el("p", "panel__note", meta.note));

    var tabs = el("div", "tab-group");
    var tabLatest = el("button", "tab-group__btn is-active", s.tabLatest);
    var tabBuzz = el("button", "tab-group__btn", s.tabBuzz);
    tabs.appendChild(tabLatest);
    tabs.appendChild(tabBuzz);
    panel.appendChild(tabs);

    var listWrap = el("div");
    function renderList(items) {
      listWrap.innerHTML = "";
      if (items.length === 0) {
        listWrap.appendChild(el("p", "panel__empty", s.emptyGeneric));
      } else {
        listWrap.appendChild(buildList(items));
      }
    }
    renderList(latestItems);
    panel.appendChild(listWrap);

    tabLatest.addEventListener("click", function () {
      tabLatest.classList.add("is-active");
      tabBuzz.classList.remove("is-active");
      renderList(latestItems);
    });
    tabBuzz.addEventListener("click", function () {
      tabBuzz.classList.add("is-active");
      tabLatest.classList.remove("is-active");
      renderList(buzzItems);
    });

    return panel;
  }

  function buildYoutubePanel(icon, data) {
    var s = t();
    var meta = s.sections.youtube || {};
    var newItems = (data.sections.youtube_new && data.sections.youtube_new.items) || [];
    var popularItems = (data.sections.youtube_popular && data.sections.youtube_popular.items) || [];
    var panel = el("section", "panel panel--full");
    panel.appendChild(buildPanelHeader(icon, meta.title, newItems.length));

    var tabs = el("div", "tab-group");
    var tabNew = el("button", "tab-group__btn is-active", s.tabYoutubeNew);
    var tabPopular = el("button", "tab-group__btn", s.tabYoutubePopular);
    tabs.appendChild(tabNew);
    tabs.appendChild(tabPopular);
    panel.appendChild(tabs);

    var listWrap = el("div");
    function renderList(items) {
      listWrap.innerHTML = "";
      if (items.length === 0) {
        listWrap.appendChild(el("p", "panel__empty", s.emptyGeneric));
      } else {
        listWrap.appendChild(buildList(items));
      }
    }
    renderList(newItems);
    panel.appendChild(listWrap);

    tabNew.addEventListener("click", function () {
      tabNew.classList.add("is-active");
      tabPopular.classList.remove("is-active");
      renderList(newItems);
    });
    tabPopular.addEventListener("click", function () {
      tabPopular.classList.add("is-active");
      tabNew.classList.remove("is-active");
      renderList(popularItems);
    });

    return panel;
  }

  function buildSeriesGroup(title, items) {
    var group = el("div", "series-card__group");
    group.appendChild(el("div", "series-card__group-title", title));
    if (items.length === 0) {
      group.appendChild(el("p", "panel__empty", t().emptyGroup));
    } else {
      group.appendChild(buildList(items));
    }
    return group;
  }

  function buildStandingsChart(rows) {
    var maxPoints = rows.reduce(function (m, r) { return Math.max(m, r.points); }, 1);
    var chart = el("div", "standings-chart");
    rows.forEach(function (row) {
      var rowEl = el("div", "standings-chart__row" + (row.is_supra_gt4 ? " standings-chart__row--spotlight" : ""));
      rowEl.appendChild(el("span", "standings-chart__pos", String(row.position)));

      var main = el("div", "standings-chart__main");
      var nameLine = el("div", "standings-chart__name-line");
      nameLine.appendChild(el("span", "standings-chart__name", row.name));
      if (row.is_supra_gt4) {
        nameLine.appendChild(el("span", "supra-tag", "GR SUPRA GT4"));
      }
      main.appendChild(nameLine);

      if (row.car) {
        main.appendChild(el("span", "standings-chart__sub", row.car));
      }

      var track = el("div", "standings-chart__track");
      var fill = el("div", "standings-chart__fill");
      fill.style.width = Math.max(4, (100 * row.points) / maxPoints) + "%";
      track.appendChild(fill);
      main.appendChild(track);

      rowEl.appendChild(main);
      rowEl.appendChild(el("span", "standings-chart__points", String(row.points)));
      chart.appendChild(rowEl);
    });
    return chart;
  }

  function buildScheduleBlock(s) {
    var i18n = t();
    var wrap = el("div", "series-card__toggle-content");

    if (s.schedule_link) {
      wrap.appendChild(el("p", "panel__note series-card__chart-note", i18n.scheduleLinkNote));
      var link = el("a", "series-card__link", i18n.linkCalendar);
      link.href = s.schedule_link;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      wrap.appendChild(link);
      return wrap;
    }

    var rounds = s.schedule || [];
    if (rounds.length === 0) {
      wrap.appendChild(el("p", "panel__empty", i18n.emptySchedule));
      return wrap;
    }

    var nextRace = rounds.filter(function (round) { return round.status === "upcoming"; })[0];
    if (nextRace) {
      var next = el("div", "schedule-next");
      next.appendChild(el("span", "schedule-next__label", i18n.nextRace));
      next.appendChild(el("span", "schedule-next__date", nextRace.date_range));
      next.appendChild(
        el("span", "schedule-next__track", [nextRace.round, nextRace.name, nextRace.track].filter(Boolean).join(" · "))
      );
      wrap.appendChild(next);
    }

    var list = el("ul", "schedule-list");
    rounds.forEach(function (r2) {
      var li = el("li", "schedule-list__item schedule-list__item--" + r2.status);
      li.appendChild(el("span", "schedule-list__dot"));
      li.appendChild(el("span", "schedule-list__date", r2.date_range));
      li.appendChild(el("span", "schedule-list__label", [r2.round, r2.name, r2.track].filter(Boolean).join(" · ")));
      list.appendChild(li);
    });
    wrap.appendChild(list);

    return wrap;
  }

  var REAL_STANDINGS_NOTE_KEYS = {
    super_taikyu: "standingsNoteSuperTaikyu",
    gt4_america: "standingsNoteGt4America",
    gt_world_challenge_asia: "standingsNoteGtWorldChallengeAsia",
    gt_world_challenge_america: "standingsNoteGtWorldChallengeAmerica",
    inter_proto_series: "standingsNoteInterProtoSeries",
    sro_japan_cup: "standingsNoteSroJapanCup",
    british_gt4: "standingsNoteBritishGt4",
    gt4_european_series: "standingsNoteGt4EuropeanSeries",
    french_gt4_cup: "standingsNoteFrenchGt4Cup",
    gt_world_challenge_australia: "standingsNoteGtWorldChallengeAustralia",
    gt4_australia: "standingsNoteGt4Australia",
  };

  function standingsNoteFor(s) {
    var i18n = t();
    var noteKey = REAL_STANDINGS_NOTE_KEYS[s.key];
    if (noteKey) return s.standings_error ? i18n.standingsNoteError : i18n[noteKey];
    return i18n.standingsNoteDefault;
  }

  function buildRankingBlock(s) {
    var wrap = el("div", "series-card__toggle-content");
    if (s.standings_chart && s.standings_chart.length > 0) {
      wrap.appendChild(buildStandingsChart(s.standings_chart));
    }
    wrap.appendChild(el("p", "panel__note series-card__chart-note", standingsNoteFor(s)));
    return wrap;
  }

  function buildToggleSection(label, contentEl) {
    var section = el("div", "series-card__toggle");
    var btn = el("button", "series-card__toggle-btn", label);
    contentEl.classList.add("series-card__toggle-body", "is-collapsed");
    btn.addEventListener("click", function () {
      var collapsed = contentEl.classList.toggle("is-collapsed");
      btn.classList.toggle("is-active", !collapsed);
    });
    section.appendChild(btn);
    section.appendChild(contentEl);
    return section;
  }

  function buildSeriesCard(regionKey, s) {
    var i18n = t();
    var entry = i18n.series[s.key];
    var label = (entry && entry.label) || s.label || s.key;
    var desc = entry && entry.desc;
    var card = el("div", "series-card series-card--" + regionKey);
    var header = el("div", "series-card__header");
    header.appendChild(el("span", null, label));
    card.appendChild(header);
    if (desc) card.appendChild(el("p", "series-card__desc", desc));
    card.appendChild(buildToggleSection(i18n.groupSchedule, buildScheduleBlock(s)));
    card.appendChild(buildToggleSection(i18n.groupRanking, buildRankingBlock(s)));
    card.appendChild(buildSeriesGroup(i18n.groupTopics, s.topics));
    card.appendChild(buildSeriesGroup(i18n.groupResults, s.results));
    card.appendChild(buildSeriesGroup(i18n.groupStandings, s.standings));

    var link = el("a", "series-card__link", i18n.linkStandings);
    link.href = s.standings_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    card.appendChild(link);

    return card;
  }

  function buildMotorsportsPanel(icon, section) {
    var i18n = t();
    var meta = i18n.sections.motorsports;
    var panel = el("section", "panel panel--full");
    var regions = section.regions || {};
    var totalCount = Object.values(regions).reduce(function (sum, r) {
      return (
        sum +
        r.series.reduce(function (s2, series) {
          return s2 + series.topics.length + series.results.length + series.standings.length;
        }, 0)
      );
    }, 0);
    panel.appendChild(buildPanelHeader(icon, meta.title, totalCount));
    if (meta.note) panel.appendChild(el("p", "panel__note", meta.note));

    var container = el("div", "motorsports");
    Object.keys(regions).forEach(function (key) {
      var r = regions[key];
      var block = el("div", "motorsports-region");
      var heading = el("div", "motorsports-region__title");
      if (r.flag) heading.appendChild(el("span", "motorsports-region__flag", r.flag));
      heading.appendChild(el("span", null, i18n.regions[key] || r.label || key));
      heading.appendChild(el("span", "motorsports-region__count", r.series.length + " " + i18n.unitSeries));
      block.appendChild(heading);

      var grid = el("div", "motorsports-region__grid");
      r.series.forEach(function (s) {
        grid.appendChild(buildSeriesCard(key, s));
      });
      block.appendChild(grid);

      container.appendChild(block);
    });
    panel.appendChild(container);
    return panel;
  }

  function collectSentimentItems(data) {
    var all = [];
    ["youtube_popular", "youtube_new", "social_buzz", "complaints", "gt4_topics"].forEach(function (key) {
      var section = data.sections[key];
      if (section && section.items) all = all.concat(section.items);
    });
    var ms = data.sections.motorsports;
    if (ms && ms.regions) {
      Object.values(ms.regions).forEach(function (r) {
        r.series.forEach(function (series) {
          all = all.concat(series.topics, series.results, series.standings);
        });
      });
    }
    return all;
  }

  function buildStats(data) {
    var i18n = t();
    statsEl.innerHTML = "";

    var sentimentItems = collectSentimentItems(data);
    var totalCount = sentimentItems.length;

    var youtubeCount = ["youtube_popular", "youtube_new"].reduce(function (sum, key) {
      return sum + ((data.sections[key] && data.sections[key].items) || []).length;
    }, 0);

    var motorsportsCount = 0;
    var seriesCount = 0;
    if (data.sections.motorsports && data.sections.motorsports.regions) {
      Object.values(data.sections.motorsports.regions).forEach(function (r) {
        seriesCount += r.series.length;
        r.series.forEach(function (series) {
          motorsportsCount += series.topics.length + series.results.length + series.standings.length;
        });
      });
    }

    // Tile 1: total
    var t1 = el("div", "stat-tile");
    t1.appendChild(el("div", "stat-tile__label", i18n.statTotal));
    var v1 = el("div", "stat-tile__value", String(totalCount));
    v1.appendChild(el("small", null, i18n.unitItems));
    t1.appendChild(v1);
    statsEl.appendChild(t1);

    // Tile 2: youtube
    var t3 = el("div", "stat-tile");
    t3.appendChild(el("div", "stat-tile__label", i18n.statYoutube));
    var v3 = el("div", "stat-tile__value", String(youtubeCount));
    v3.appendChild(el("small", null, i18n.unitVideos));
    t3.appendChild(v3);
    statsEl.appendChild(t3);

    // Tile 3: motorsports
    var t4 = el("div", "stat-tile");
    t4.appendChild(el("div", "stat-tile__label", i18n.statMotorsports.replace("{n}", String(seriesCount))));
    var v4 = el("div", "stat-tile__value", String(motorsportsCount));
    v4.appendChild(el("small", null, i18n.unitItems));
    t4.appendChild(v4);
    statsEl.appendChild(t4);
  }

  function buildCarCard(car) {
    var i18n = t();
    var card = el("div", "car-card" + (car.is_supra ? " car-card--spotlight" : ""));
    var model = pick(car.model);

    var figure = el("div", "car-card__photo");
    var img = el("img");
    img.src = car.photo.src;
    img.alt = car.manufacturer + " " + model;
    img.loading = "lazy";
    figure.appendChild(img);
    if (car.is_supra) figure.appendChild(el("span", "supra-tag car-card__badge", "SUPRA GT4"));
    card.appendChild(figure);

    var body = el("div", "car-card__body");
    body.appendChild(el("span", "car-card__manufacturer", car.manufacturer));
    body.appendChild(el("h3", "car-card__model", model));
    var description = pick(car.description);
    if (description) body.appendChild(el("p", "car-card__desc", description));
    body.appendChild(el("div", "car-card__price", pick(car.price)));

    var specList = el("dl", "car-card__specs");
    (car.specs || []).forEach(function (spec) {
      specList.appendChild(el("dt", null, i18n.carSpecs[spec.key] || spec.key));
      specList.appendChild(el("dd", null, pick(spec.value)));
    });
    body.appendChild(specList);

    var link = el("a", "series-card__link", i18n.linkOfficial);
    link.href = car.official_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    body.appendChild(link);

    var credit = el("p", "car-card__credit");
    credit.appendChild(document.createTextNode(i18n.photoCredit));
    var creditLink = el("a", null, car.photo.credit + " (" + car.photo.license + ")");
    creditLink.href = car.photo.source_url;
    creditLink.target = "_blank";
    creditLink.rel = "noopener noreferrer";
    credit.appendChild(creditLink);
    credit.appendChild(document.createTextNode(i18n.viaCommons));
    body.appendChild(credit);

    card.appendChild(body);
    return card;
  }

  function buildCarsPanel(carsData) {
    var i18n = t();
    var panel = el("section", "panel panel--full");
    var cars = carsData.cars || [];
    panel.appendChild(buildPanelHeader("car", i18n.sections.gt4_cars.title, cars.length));

    var analysis = carsData.trend_analysis;
    if (analysis) {
      var analysisBox = el("div", "car-analysis");
      analysisBox.appendChild(el("h3", "car-analysis__title", i18n.sections.gt4_cars.analysisTitle));
      pick(analysis)
        .split("\n")
        .filter(Boolean)
        .forEach(function (para) {
          analysisBox.appendChild(el("p", "car-analysis__text", para));
        });
      if (analysis.updated) {
        analysisBox.appendChild(el("p", "car-analysis__updated", i18n.analysisUpdatedPrefix + analysis.updated));
      }
      panel.appendChild(analysisBox);
    }

    var note = pick(carsData.note);
    if (note) panel.appendChild(el("p", "panel__note", note));

    var grid = el("div", "car-grid");
    cars.forEach(function (car) {
      grid.appendChild(buildCarCard(car));
    });
    panel.appendChild(grid);
    return panel;
  }

  function buildStTeamCard(team) {
    var i18n = t();
    var card = el("div", "car-card" + (team.rank === 1 ? " car-card--spotlight" : ""));

    var figure = el("div", "car-card__photo");
    if (team.photo) {
      var img = el("img");
      img.src = team.photo.src;
      img.alt = team.team_name;
      img.loading = "lazy";
      figure.appendChild(img);
    } else {
      figure.classList.add("car-card__photo--placeholder");
      var placeholderIcon = el("div", "car-card__photo-icon");
      placeholderIcon.innerHTML = ICONS.car;
      figure.appendChild(placeholderIcon);
    }
    figure.appendChild(el("span", "supra-tag car-card__badge", i18n.carNoLabel + team.car_no));
    card.appendChild(figure);

    var body = el("div", "car-card__body");
    body.appendChild(el("span", "car-card__manufacturer", "ST-Z"));
    body.appendChild(el("h3", "car-card__model", team.team_name));
    var description = pick(team.description);
    if (description) body.appendChild(el("p", "car-card__desc", description));

    var results = el("div", "car-card__price");
    if (typeof team.rank === "number" && typeof team.points === "number") {
      results.textContent =
        i18n.teamResultsRank.replace("{rank}", String(team.rank)).replace("{points}", String(team.points));
    } else {
      results.textContent = i18n.teamResultsUnknown;
    }
    body.appendChild(el("div", "car-card__specs-title", i18n.teamResults));
    body.appendChild(results);

    body.appendChild(el("div", "car-card__specs-title", i18n.teamDrivers));
    var drivers = team.drivers || [];
    if (drivers.length === 0) {
      body.appendChild(el("p", "panel__empty", i18n.teamDriversUnannounced));
    } else {
      var driverList = el("ul", "team-driver-list");
      drivers.forEach(function (driver) {
        var li = el("li", "team-driver-list__item");
        li.appendChild(el("span", "team-driver-list__name", driver.name));
        var gradeLabel = driver.grade === "gentleman" ? i18n.driverGradeGentleman : i18n.driverGradeExpertPlatinum;
        li.appendChild(el("span", "team-driver-list__grade team-driver-list__grade--" + driver.grade, gradeLabel));
        driverList.appendChild(li);
      });
      body.appendChild(driverList);
    }

    var link = el("a", "series-card__link", i18n.linkOfficial);
    link.href = team.official_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    body.appendChild(link);

    if (team.photo) {
      var credit = el("p", "car-card__credit");
      credit.appendChild(document.createTextNode(i18n.photoCredit));
      var creditLink = el("a", null, team.photo.credit + " (" + team.photo.license + ")");
      creditLink.href = team.photo.source_url;
      creditLink.target = "_blank";
      creditLink.rel = "noopener noreferrer";
      credit.appendChild(creditLink);
      credit.appendChild(document.createTextNode(i18n.viaCommons));
      body.appendChild(credit);
    }

    card.appendChild(body);
    return card;
  }

  function buildStTeamsPanel(section) {
    var i18n = t();
    var meta = i18n.sections.st_supra_teams;
    var panel = el("section", "panel panel--full");
    var teams = section.teams || [];
    panel.appendChild(buildPanelHeader("flag", meta.title, teams.length));
    if (meta.note) panel.appendChild(el("p", "panel__note", meta.note));

    var grid = el("div", "car-grid");
    teams.forEach(function (team) {
      grid.appendChild(buildStTeamCard(team));
    });
    panel.appendChild(grid);
    return panel;
  }

  function applyStaticText() {
    var i18n = t();
    document.documentElement.lang = LANG;
    if (chipLabelEl) chipLabelEl.textContent = i18n.chipLabel;
    if (updateIntervalChipEl) updateIntervalChipEl.textContent = i18n.updateInterval;
    if (footerTextEl) footerTextEl.textContent = i18n.footer;
    if (langToggleEl) {
      Array.prototype.forEach.call(langToggleEl.querySelectorAll(".lang-toggle__btn"), function (btn) {
        btn.classList.toggle("is-active", btn.getAttribute("data-lang") === LANG);
      });
    }
  }

  function render(data, carsData) {
    lastData = data;
    lastCarsData = carsData;
    applyStaticText();
    buildStats(data);

    board.innerHTML = "";
    if (carsData) board.appendChild(buildCarsPanel(carsData));
    if (data.sections && data.sections.st_supra_teams) {
      board.appendChild(buildStTeamsPanel(data.sections.st_supra_teams));
    }
    LAYOUT.forEach(function (entry) {
      if (entry.key === "youtube") {
        board.appendChild(buildYoutubePanel(entry.icon, data));
        return;
      }
      var section = data.sections && data.sections[entry.key];
      if (!section) return;
      var panel;
      if (entry.key === "motorsports") {
        panel = buildMotorsportsPanel(entry.icon, section);
      } else if (entry.key === "complaints" || entry.key === "social_buzz") {
        panel = buildTabbedPanel(entry.icon, entry.key, section);
      } else {
        panel = buildGenericPanel(entry.icon, entry.key, section, entry.size);
      }
      board.appendChild(panel);
    });

    var i18n = t();
    lastUpdatedEl.textContent = i18n.lastUpdatedPrefix + (data.generated_at_jst || i18n.lastUpdatedUnknown);

    var generatedAt = data.generated_at_utc ? new Date(data.generated_at_utc) : null;
    if (generatedAt) {
      var hoursSince = (Date.now() - generatedAt.getTime()) / 36e5;
      statusDot.classList.toggle("is-stale", hoursSince > 2);
    }
  }

  function renderError(message) {
    applyStaticText();
    statsEl.innerHTML = "";
    board.innerHTML = "";
    board.appendChild(el("p", "board__error", message));
    lastUpdatedEl.textContent = t().statusFetchFailed;
    statusDot.classList.add("is-error");
  }

  function setLang(lang) {
    if (lang !== "ja" && lang !== "en") return;
    if (lang === LANG) return;
    LANG = lang;
    try {
      window.localStorage.setItem(LANG_STORAGE_KEY, lang);
    } catch (e) {
      /* localStorage unavailable */
    }
    if (lastData) {
      render(lastData, lastCarsData);
    } else {
      applyStaticText();
      if (loadingEl) loadingEl.textContent = t().loading;
    }
  }

  if (langToggleEl) {
    langToggleEl.addEventListener("click", function (evt) {
      var btn = evt.target.closest(".lang-toggle__btn");
      if (!btn) return;
      setLang(btn.getAttribute("data-lang"));
    });
  }

  applyStaticText();
  if (loadingEl) loadingEl.textContent = t().loading;

  function fetchJson(path) {
    return fetch(path, { cache: "no-store" }).then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    });
  }

  fetchJson("data/latest.json")
    .then(function (data) {
      fetchJson("data/gt4_cars.json")
        .then(function (carsData) {
          render(data, carsData);
        })
        .catch(function () {
          render(data, null);
        });
    })
    .catch(function (err) {
      renderError(t().fetchErrorPrefix + err.message + t().fetchErrorSuffix);
    });
})();

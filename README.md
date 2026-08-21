# Supra GT4 Watch

Toyota GR Supra GT4に関する情報を1か所に集約するモニタリングダッシュボード。GitHub Actionsで
1日3回(JST 07:00 / 12:00 / 17:00、GR Corolla Watchと同一の更新周期)自動的にデータを収集し、
GitHub Pagesで公開する。

**公開ページ:** Settings > Pages で有効化後、`https://<owner>.github.io/Supra-GT4/`

## 掲載している情報

| セクション | 内容 | 取得方法 |
| --- | --- | --- |
| GR Supra GT4 参戦レース(地域別・全14シリーズ) | 日本・アジア(スーパー耐久 ST-Zクラス/SRO Japan Cup/SRO GT Cup中国)、米国(GT4 America/IMSA Michelin Pilot Challenge)、欧州(GT4 European Series/British GT/French GT4 Cup/GT4 Italian Series/ADAC GT4 Germany/ニュルブルクリンク NLS・24h/GT4 Winter Series)、オセアニア(Monochrome GT4 Australia)、中東(24H Series Middle East)の5地域・14シリーズに整理。各シリーズの今年度スケジュール・ランキング(Supra GT4をハイライト)・最新トピックスを表示 | Google News RSS(トピックス/結果/ランキング話題) + 各シリーズ公式サイト(スーパー耐久は日程、GT4 Americaはチームランキングを実データ取得。他シリーズは公式カレンダー/ランキングページへの直接リンク) |
| GT4参戦車両一覧 | 現在SRO GT4 Manufacturer Rankingに参加している9メーカー(Toyota・BMW・Mercedes-AMG・Porsche・Ford・Audi・McLaren・Aston Martin・Ginetta)の最新モデルを写真付きでリスト化。メーカー・車名・参考価格・エンジン/出力/トルク/車重/トランスミッション等のスペックと、各社公式サイトへのリンクを掲載。Supra GT4のみハイライト表示 | 各社公式発表・報道の参考価格(手動収集、静的データ)+ 写真はWikimedia Commonsのクリエイティブ・コモンズ・ライセンス画像(撮影者・ライセンスを明記) |
| GT4カテゴリー最新トピックス | GT4ホモロゲーション/レギュレーション、競合GT4(BMW M4 GT4・Mercedes-AMG GT4・Porsche Cayman GT4・Ford Mustang GT4・Aston Martin Vantage GT4・Audi R8 LMS GT4・McLaren Artura GT4等)の開発・アップデート、技術情報、Supra GT4や競合車の不具合情報をカテゴリー別バッジ付きで新着順に表示 | Google News RSS(日英) |
| YouTube 人気動画/新着動画 | Supra GT4・競合GT4の動画を20本ずつ整理(サムネイル付き、日英クエリを統合)。人気動画は再生数順、新着動画は投稿日時順 | YouTube検索結果ページのベストエフォート・スクレイピング |
| SNSでの話題 | X/Facebookの投稿の代替として、Supra GT4・競合GT4に関するニュース・ブログでの話題言及。「最新順」「話題順」をタブで切り替え表示 | Google News RSS |
| Supra GT4 お客様の声・クレーム関連情報 | リコール・不具合報道など公開情報(Supra GT4限定、競合車は含まない)。「最新順」「話題順」をタブで切り替え表示 | Google News RSS |

「人気動画」以外の全セクションは新しい順/話題順に並び替えている。トヨタ公式発表以外の
全セクションには、見出し文からの簡易センチメント判定(ポジティブ/ネガティブ)を付与している
(英語: VADER、日本語: 自動車/モータースポーツレビュー向け手作り極性辞書)。判定根拠は
バッジへのマウスオーバー(タッチ操作の場合はタップ)で確認できる。あくまで見出し文のみに
基づく自動推定であり、参考値として利用すること。

## 参戦レース情報の全14シリーズ一覧

| 地域 | シリーズ | 実データ取得 |
| --- | --- | --- |
| 日本・アジア | スーパー耐久 ST-Zクラス | 年間スケジュールを実データ取得 |
| 日本・アジア | SRO Japan Cup(GT4クラス) | 公式カレンダー/ランキングへのリンクのみ |
| 日本・アジア | SRO GT Cup(中国) | 公式サイト未確定のため検索リンク |
| 米国 | Pirelli/Fanatec GT4 America(Silver Teams) | チームランキングを実データ取得(Supra GT4ハイライト) |
| 米国 | IMSA Michelin Pilot Challenge(GSクラス) | 公式カレンダー/ランキングへのリンクのみ |
| 欧州 | GT4 European Series | 公式カレンダー/ランキングへのリンクのみ |
| 欧州 | British GT Championship(GT4クラス) | 公式カレンダー/ランキングへのリンクのみ |
| 欧州 | French GT4 Cup | 公式サイト未確定のため検索リンク |
| 欧州 | GT4 Italian Series | 公式カレンダー/ランキングへのリンクのみ |
| 欧州 | ADAC GT4 Germany | 公式カレンダー/ランキングへのリンクのみ |
| 欧州 | ニュルブルクリンク NLS・24h(SP10クラス) | 公式カレンダーへのリンク、ランキングは検索リンク |
| 欧州 | GT4 Winter Series(イベリア半島) | 主催者(GEDLICH Racing)公式ページへのリンク、ランキングは検索リンク |
| オセアニア | Monochrome GT4 Australia Series | 公式カレンダー/ランキングへのリンクのみ |
| 中東 | 24H Series Middle East(GT4クラス) | 公式カレンダー/ランキングへのリンクのみ |

- **スーパー耐久(日本・アジア)**: 公式レース一覧ページ(supertaikyu.com)から年間スケジュールを
  実データで取得している。全クラス共通日程のためST-Zクラス(GR Supra GT4)にもそのまま適用される。
  順位表はクラス別の機械的解釈が難しいため、公式ランキングページへの直接リンクのみ。
- **GT4 America(米国)**: gt4-america.comはTC America(tcamerica.us)と同じSRO Motorsports
  America系列の共通CMSで運用されており、"Silver Teams"クラスの順位表を実データで取得し、
  各レースの完全結果ページから補完した使用車種でGR Supra GT4参戦チームをハイライト表示している。
- **上記2つ以外の12シリーズ**: 順位表のクラス別フィルター構造やチーム別使用車種の確定方法を
  安定的に確認できていないため、誤表示リスクを避けグラフ化は行わず、公式カレンダー/ランキング
  ページへの直接リンクのみを表示している(URLは実装時に実在を確認済み。ただしFrench GT4 Cup・
  SRO GT Cup中国・ニュルブルクリンクNLS標準順位表・GT4 Winter Seriesの4シリーズは安定した
  公式URLを特定できなかったため、Google検索へのリンクとしている)。トピックス/結果/ランキング
  関連のニュースはGoogle News RSSでSupra GT4関連の話題を検索しているため、Supra GT4の
  参戦実績が薄い/未確認のシリーズでは「該当情報なし」と表示されることがある。

## 既知の制約

- **公式API未使用**: YouTube Data API・X API・Facebook Graph API のキーは未設定。すべて
  無料の公開エンドポイント(Google News RSS、YouTube検索ページ)をベストエフォートで
  利用しているため、件数の正確性・網羅性は公式APIに劣る。
- **X/Facebookの投稿本体は含まれない**: ニュース/ブログでの言及を代替指標として表示している。
- **クレーム情報は社内システム未連携**: 公開されている報道・SNS言及のみを集約した簡易モニタリング。
- **YouTube検索スクレイピングの脆弱性**: YouTube側のページ構造変更により取得に失敗する
  可能性がある。失敗時はダッシュボード上に取得エラーとして表示される。
- **GT4 Americaランキングは"Silver Teams"クラスのみ**: Toyota GR Supra GT4は複数クラス
  (Pro-Am/Am等)にも参戦し得るが、機械的に安定して取得できるのはSilver Teamsクラスのみのため
  そのクラスのみをグラフ表示している。
- **センチメント判定は見出し文のみの自動推定**: 判定根拠語が1つ以下の場合は中立とする
  2語ゲート(英語のみ)により、単語1つで結論が引っ張られる誤判定を抑えている。判定機能自体は
  内部的に維持しているが、画面上の集計表示(「評判」タイル)は削除している。
- **GT4参戦車両一覧は静的データ**: `site/data/gt4_cars.json` は1日3回の自動更新の対象外で、
  手動収集した参考価格・スペックを元にした静的ファイル。価格・スペックは為替やオプション、
  BoP(性能調整)により変動するため参考値として扱うこと。更新する場合は同ファイルを直接編集する。

## 構成

```
scripts/
  fetch_data.py         # 全ソースを集約し site/data/latest.json を生成
  sources/
    common.py            # RSS取得・数値/日時パース等の共通処理
    sentiment.py          # 見出し文からのポジティブ/ネガティブ推定(VADER + 日本語辞書)
    motorsports.py         # 地域別(日本・アジア/米国/欧州/オセアニア/中東)・全14シリーズのレース情報集約
    standings.py            # GT4 America公式サイトの実データランキング取得
    schedule.py              # スーパー耐久の年間レース日程取得
    gt4_topics.py             # GT4カテゴリー全体のトピックス(ホモロゲーション/技術/不具合等)
    youtube.py                 # YouTube人気/新着動画
    social_buzz.py              # SNS話題の代替指標(最新順/話題順)
    complaints.py                # Supra GT4のクレーム・不具合情報(最新順/話題順)
site/
  index.html / style.css / app.js   # ダッシュボード本体(静的サイト)
  data/latest.json                  # 自動生成される最新データ(コミット対象外)
  data/gt4_cars.json                # GT4参戦車両一覧(手動更新・コミット対象)
.github/workflows/update-dashboard.yml  # 1日3回の自動更新 + GitHub Pagesデプロイ
```

## ローカルでの動作確認

```bash
cd scripts
pip install -r requirements.txt
python fetch_data.py          # site/data/latest.json を生成
cd ../site
python3 -m http.server 8000   # http://localhost:8000 で確認
```

## GitHub Pagesの有効化(初回のみ)

リポジトリの Settings > Pages > Build and deployment > Source を
**GitHub Actions** に設定する。設定後、`update-dashboard` ワークフローの実行(スケジュール
または手動の workflow_dispatch)によって自動的に公開される。

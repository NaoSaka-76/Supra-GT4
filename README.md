# Supra GT4 Watch

Toyota GR Supra GT4に関する情報を1か所に集約するモニタリングダッシュボード。GitHub Actionsで
1日3回(JST 07:00 / 12:00 / 17:00、GR Corolla Watchと同一の更新周期)自動的にデータを収集し、
GitHub Pagesで公開する。

**公開ページ:** Settings > Pages で有効化後、`https://<owner>.github.io/Supra-GT4/`

## 掲載している情報

| セクション | 内容 | 取得方法 |
| --- | --- | --- |
| GR Supra GT4 参戦レース(地域別) | 日本・アジア(スーパー耐久 ST-Zクラス)、米国(Pirelli/Fanatec GT4 America)、欧州(GT4 European Series)、オセアニア(Monochrome GT4 Australia Series)の4地域に整理。各地域の今年度スケジュール・ランキング(Supra GT4をハイライト)・最新トピックスを表示 | Google News RSS(トピックス/結果/ランキング話題) + 各シリーズ公式サイト(スーパー耐久は日程を実データ取得、GT4 Americaはチームランキングを実データ取得、他2地域は公式カレンダー/ランキングページへの直接リンク) |
| GT4カテゴリー最新トピックス | GT4ホモロゲーション/レギュレーション、競合GT4(BMW M4 GT4・Mercedes-AMG GT4・Porsche Cayman GT4・Ford Mustang GT4・Aston Martin Vantage GT4・Audi R8 LMS GT4・McLaren Artura GT4等)の開発・アップデート、技術情報、Supra GT4や競合車の不具合情報をカテゴリー別バッジ付きで新着順に表示 | Google News RSS(日英) |
| YouTube 人気動画/新着動画 | Supra GT4・競合GT4の動画を20本ずつ整理(サムネイル付き、日英クエリを統合)。人気動画は再生数順、新着動画は投稿日時順 | YouTube検索結果ページのベストエフォート・スクレイピング |
| SNSでの話題 | X/Facebookの投稿の代替として、Supra GT4・競合GT4に関するニュース・ブログでの話題言及。「最新順」「話題順」をタブで切り替え表示 | Google News RSS |
| Supra GT4 お客様の声・クレーム関連情報 | リコール・不具合報道など公開情報(Supra GT4限定、競合車は含まない)。「最新順」「話題順」をタブで切り替え表示 | Google News RSS |

「人気動画」以外の全セクションは新しい順/話題順に並び替えている。トヨタ公式発表以外の
全セクションには、見出し文からの簡易センチメント判定(ポジティブ/ネガティブ)を付与している
(英語: VADER、日本語: 自動車/モータースポーツレビュー向け手作り極性辞書)。判定根拠は
バッジへのマウスオーバー(タッチ操作の場合はタップ)で確認できる。あくまで見出し文のみに
基づく自動推定であり、参考値として利用すること。

## 参戦レース情報の実データ取得について

- **スーパー耐久(日本・アジア)**: 公式レース一覧ページ(supertaikyu.com)から年間スケジュールを
  実データで取得している。全クラス共通日程のためST-Zクラス(GR Supra GT4)にもそのまま適用される。
  順位表はクラス別の機械的解釈が難しいため、公式ランキングページへの直接リンクのみ。
- **GT4 America(米国)**: gt4-america.comはTC America(tcamerica.us)と同じSRO Motorsports
  America系列の共通CMSで運用されており、"Silver Teams"クラスの順位表を実データで取得し、
  各レースの完全結果ページから補完した使用車種でGR Supra GT4参戦チームをハイライト表示している。
- **GT4 European Series(欧州)/ Monochrome GT4 Australia(オセアニア)**: 順位表のクラス別
  フィルター構造やチーム別使用車種の確定方法を安定的に確認できていないため、誤表示リスクを
  避けグラフ化は行わず、公式カレンダー/ランキングページへの直接リンクのみを表示している
  (URLは実装時に実在を確認済み)。

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
  2語ゲート(英語のみ)により、単語1つで結論が引っ張られる誤判定を抑えている。

## 構成

```
scripts/
  fetch_data.py         # 全ソースを集約し site/data/latest.json を生成
  sources/
    common.py            # RSS取得・数値/日時パース等の共通処理
    sentiment.py          # 見出し文からのポジティブ/ネガティブ推定(VADER + 日本語辞書)
    motorsports.py         # 地域別(日本・アジア/米国/欧州/オセアニア)のレース情報集約
    standings.py            # GT4 America公式サイトの実データランキング取得
    schedule.py              # スーパー耐久の年間レース日程取得 + 他地域の公式カレンダーリンク
    gt4_topics.py             # GT4カテゴリー全体のトピックス(ホモロゲーション/技術/不具合等)
    youtube.py                 # YouTube人気/新着動画
    social_buzz.py              # SNS話題の代替指標(最新順/話題順)
    complaints.py                # Supra GT4のクレーム・不具合情報(最新順/話題順)
site/
  index.html / style.css / app.js   # ダッシュボード本体(静的サイト)
  data/latest.json                  # 自動生成される最新データ(コミット対象外)
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

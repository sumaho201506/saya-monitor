# サヤ取りチャートモニター（GitHub Pages ＋ 1時間ごとの自動価格更新）

## 仕組み
- `index.html` … チャートのページ（v12）。開くと `prices.json` を自動で読み、1時間ごとに再取得します。
- `fetch_prices.py` … yfinance で `tickers.txt` の銘柄の最新価格（約15分遅れ）を取り、`prices.json` に書き出します。
- `.github/workflows/update.yml` … 上のスクリプトを GitHub が自動実行します（平日 日本時間 9:05〜16:05 の毎時）。あなたのPCは不要です。

## 設定手順（約15分・すべて無料）
1. https://github.com でアカウントを作ります（持っていれば不要）。
2. 右上「＋」→「New repository」。名前は `saya-monitor`、**Public** を選び「Create repository」。
   （無料のGitHub Pagesは、Publicのリポジトリが対象です。ページ自体は誰でも見られますが、あなたの取引データはブラウザ内にだけ保存され、ここには載りません。）
3. 作成後の画面の「uploading an existing file」から、このフォルダの中身（`index.html` `fetch_prices.py` `tickers.txt` `requirements.txt` `prices.json` `README.md` と **`.github` フォルダごと**）をドラッグして「Commit changes」。
   - `.github` フォルダが上がらない場合は、「Add file → Create new file」で名前に `.github/workflows/update.yml` と入力し、`update.yml` の中身を貼り付けて保存します。
4. 「Settings → Actions → General」の一番下「Workflow permissions」で **Read and write permissions** を選び「Save」。
5. 「Settings → Pages」で、Source を「Deploy from a branch」、Branch を `main` / `(root)` にして「Save」。1〜2分後、`https://（あなたのユーザー名）.github.io/saya-monitor/` でページが開きます。
6. 「Actions」タブ → `update-prices` → 「Run workflow」で、まず手動で1回実行します。緑のチェックが付けば成功で、`prices.json` に価格が入ります。
7. ページを開き、各Setで 1343・1345 などのデータを Import（ライン名は銘柄コードを含めてください。例：`1345`）。返済行の「最新価格」にチェックを入れると、`prices.json` の価格が反映されます。

## 銘柄を増やす
`tickers.txt` に1行1銘柄で足します（東証は4桁コード。自動で `.T` が付きます）。`prices.json` の銘柄コードと、ページのライン名の中の4桁が一致すれば反映されます。

## 更新の間隔を変える
`.github/workflows/update.yml` の `cron` を編集します。`5 0-7 * * 1-5` は「平日のUTC0〜7時の毎時5分」＝日本時間9:05〜16:05です。終日にするなら `5 * * * *`。

## 注意
- yfinance は Yahoo! ファイナンスのデータを取る非公式の方法です。利用規約は各自でご確認ください。Yahoo側の変更で、突然取得できなくなることがあります。その場合 `prices.json` は前回の値のままで、ページの時刻表示が古いままになります。
- 価格は約15分遅れです（実際の遅延は、動かして確認してください）。
- GitHubの定期実行は、数分〜数十分遅れることがあります。また、リポジトリに60日間動きがないと、定期実行が自動で止まる場合があります（Actionsタブから再開できます）。
- ページを開いている間だけ、1時間ごとの自動取得が動きます。閉じている間も `prices.json` は更新され、次に開いたときに最新値が入ります。
- 保存データ（取込データ・シミュレーション・メモ）は、そのブラウザ内にあります。claude.ai上のページとは別の場所なので、移行したい場合は旧ページで「バックアップ保存」し、新ページで「バックアップ読込」を使ってください。

# Change Log

## v1.2

- デプロイ枚数オプションの n, n_example をnullableに変更。nullのとき、全画像を出力。
- コマンドラインオプション変更: `--makesample <N>` -> `--generate-samplefile`
- コマンドラインオプション追加: `--deploy-result`
- 設定値追加: backup

## v1.1

- 自作カラーマップをサポート。
- 設定値 vmax の初期値を変更。
- 設定値 vmin, vmax の空欄設定(自動判定)をサポート。

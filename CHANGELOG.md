# Change Log

## 1.6

- CSVエクスポート機能追加 `--export`

## 1.5

- GUI追加

## 1.4

- 設定ファイルのデフォルトセクション名変更: `DEFAULT` -> `annotation`
- lib.config.saveに `mode` オプション追加。

## 1.3

- 設定ファイル切替機能追加 `--config-file`
- 設定ファイルセクション切替機能追加 `--config-section`
- 設定ファイル生成機能追加 `--create-config-file`
- コマンドラインオプション変更: `--generate-samplefile` -> `--create-sample-datafile`

## 1.2

- 設定値 n, n_example をnullableに変更。nullのとき、全画像を出力。
- コマンドラインオプション変更: `--makesample <N>` -> `--generate-samplefile`
- 結果出力機能追加 `--deploy-result`
- 設定値追加: figsize, backup
- col_filename に 'index' を指定し 'index' カラムがなかった場合、DataFrame.indexを使うよう変更。

## 1.1

- 自作カラーマップをサポート。
- 設定値 vmax の初期値を変更。
- 設定値 vmin, vmax をnullableに変更。nullのとき、自動判定。

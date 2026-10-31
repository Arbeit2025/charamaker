# charamaker（キャラクターメーカー）

ランダムなキャラクター設定を、ドット絵風の顔画像つきで生成する小さな Web ツールです。単一ファイル Flask アプリ（`app.py`）で、データベースは使いません。

## できること

- 「新しいキャラクターを生成」ボタンで、キャラクター設定をランダム生成
  - 名前（日本語の姓名プール）、年齢（18〜60歳）、性別、職業（30種）
  - 性格（2〜3個）、趣味、特技、口癖、好きなもの
  - テンプレートで合成した短い紹介文
- Pillow で描くドット絵風フェイス（髪型・髪色・目の形・口・アクセサリがランダム）
- **seed 方式で再現可能**：設定も画像も seed から決定的に生成されます。気に入ったキャラクターは `/?seed=<番号>` でいつでも再表示できます

## 使い方

1. トップページを開くと、ランダムなキャラクターが表示されます
2. 「🎲 新しいキャラクターを生成」を押すと別のキャラクターになります
3. 特定のキャラクターを再現したいときは `/?seed=12345` のように seed を指定します

## ローカル起動

```bash
pip install -r requirements.txt
python app.py
# http://localhost:5000
```

## テスト

```bash
python -m unittest discover -s tests
```

## デプロイ（Render）

`render.yaml` を使って Web Service（Free）としてデプロイできます。起動コマンドは `gunicorn app:app`、ヘルスチェックは `/healthz` です。

## 構成

- `app.py` … 本体（単一ファイル）。データプール／キャラクター生成／顔描画／ルーティング
- `tests/test_app.py` … unittest
- `requirements.txt` … Flask / gunicorn / Pillow

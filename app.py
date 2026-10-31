# ============================================================
# charamaker（キャラクターメーカー）
# ランダムキャラクター設定生成ツール（画像付き）
#
# 目次
#   1. データプール（名前・職業・性格など）
#   2. キャラクター生成（seed で再現可能）
#   3. ドット絵フェイス描画（Pillow）
#   4. ルーティング
# ============================================================

import io
import random

from flask import Flask, Response, jsonify, render_template_string, request
from PIL import Image, ImageDraw

app = Flask(__name__)

# ============================================================
# 1. データプール
# ============================================================

FAMILY_NAMES = [
    "佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村",
    "小林", "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上",
    "木村", "林", "斎藤", "清水",
]

GIVEN_NAMES_FEMALE = [
    "さくら", "葵", "美咲", "結衣", "陽菜", "莉子", "花", "澪",
    "楓", "遥", "真央", "凛", "由紀", "香織", "彩乃", "芽衣",
    "千尋", "薫", "桃子", "栞",
]

GIVEN_NAMES_MALE = [
    "蓮", "悠真", "翔太", "健一", "拓海", "颯太", "大輔", "直樹",
    "亮", "誠", "悠", "蒼", "陸", "駿", "和也", "智也",
    "光", "翼", "慶太", "航",
]

GENDERS = ["女性", "男性"]

JOBS = [
    "教師", "看護師", "エンジニア", "デザイナー", "料理人", "農家",
    "漁師", "作家", "イラストレーター", "音楽家", "カフェ店員",
    "図書館司書", "保育士", "警察官", "消防士", "薬剤師", "美容師",
    "建築士", "翻訳家", "動画配信者", "占い師", "探偵", "声優",
    "プロゲーマー", "駅員", "花屋", "パン職人", "動物園飼育員",
    "気象予報士", "弁護士",
]

PERSONALITIES = [
    "明るい", "穏やか", "真面目", "好奇心旺盛", "マイペース",
    "面倒見がいい", "負けず嫌い", "ロマンチスト", "慎重", "行動的",
    "おっちょこちょい", "冷静", "情熱的", "のんびり屋", "几帳面",
    "ユーモアがある", "照れ屋", "努力家",
]

HOBBIES = [
    "読書", "映画鑑賞", "料理", "キャンプ", "写真", "ゲーム",
    "園芸", "釣り", "カラオケ", "旅行", "ランニング", "ボードゲーム",
    "プラモデル", "手芸", "温泉めぐり", "星空観察", "筋トレ", "カフェ巡り",
]

SKILLS = [
    "暗算が速い", "どこでも寝られる", "絶対音感がある", "早起き",
    "人の名前をすぐ覚える", "折り紙", "ジャグリング", "一輪車",
    "地図を読むこと", "利き茶", "書道", "速読", "似顔絵",
    "編み物", "水泳", "パズル",
]

CATCHPHRASES = [
    "なんとかなるさ", "まあ、いっか", "それな", "とりあえずやってみよう",
    "ふむふむ", "だよね〜", "よし、決めた", "まじで？",
    "おつかれさまです", "いい感じ",
]

FAVORITES = [
    "プリン", "猫", "雨の日の匂い", "古い映画", "抹茶アイス",
    "電車の旅", "文房具", "星空", "辛いもの", "昼寝",
    "海", "レトロゲーム", "紅茶", "スイカ", "図書館の静けさ",
]

BIO_TEMPLATES = [
    "{name}（{age}歳）。{job}として働いている。{personalities}な性格で、"
    "趣味は{hobby}。特技は{skill}で、口癖は「{catchphrase}」。"
    "{favorite}が大好き。",
    "{job}の{name}、{age}歳。{personalities}な人柄で周りから頼られることも多い。"
    "休みの日は{hobby}を楽しみ、特技の{skill}を披露することもある。"
    "口癖は「{catchphrase}」。{favorite}には目がない。",
    "{name}（{age}歳）は{personalities}な{job}。"
    "{hobby}が趣味で、{skill}が得意。ふとしたときに「{catchphrase}」と言い、"
    "{favorite}の話になると目を輝かせる。",
]

# ============================================================
# 2. キャラクター生成
# ============================================================


def _parse_seed(raw):
    """seed 文字列を int に変換する。不正な値は None を返す（500 にしない）。"""
    if raw is None:
        return None
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        return None


def generate_character(seed):
    """seed からキャラクター設定を決定的に生成する。"""
    rng = random.Random(seed)
    gender = rng.choice(GENDERS)
    family = rng.choice(FAMILY_NAMES)
    given = rng.choice(GIVEN_NAMES_FEMALE if gender == "女性" else GIVEN_NAMES_MALE)
    name = f"{family} {given}"
    age = rng.randint(18, 60)
    job = rng.choice(JOBS)
    personalities = rng.sample(PERSONALITIES, rng.choice([2, 3]))
    hobby = rng.choice(HOBBIES)
    skill = rng.choice(SKILLS)
    catchphrase = rng.choice(CATCHPHRASES)
    favorite = rng.choice(FAVORITES)
    bio = rng.choice(BIO_TEMPLATES).format(
        name=name,
        age=age,
        job=job,
        personalities="で".join(personalities),
        hobby=hobby,
        skill=skill,
        catchphrase=catchphrase,
        favorite=favorite,
    )
    return {
        "seed": seed,
        "name": name,
        "age": age,
        "gender": gender,
        "job": job,
        "personalities": personalities,
        "hobby": hobby,
        "skill": skill,
        "catchphrase": catchphrase,
        "favorite": favorite,
        "bio": bio,
    }


# ============================================================
# 3. ドット絵フェイス描画
# ============================================================

GRID = 32          # 論理グリッド（32x32 ドット）
SCALE = 12         # 1ドット = 12px → 出力 384x384

SKIN_TONES = ["#ffe0bd", "#ffd3a1", "#f1c27d", "#e0ac69", "#c68642"]
HAIR_COLORS = [
    "#2b2b2b", "#5a3a22", "#8a5a2b", "#c98a3d", "#e8c87a",
    "#b0483e", "#4a6fa5", "#5f8f5a", "#8e6bbf", "#d97ba6",
    "#7a7a7a", "#e8e8e8",
]
BG_COLORS = [
    "#fdeef2", "#eaf4fd", "#eefde9", "#fdf6e3", "#f1eafd",
    "#e9fdf8", "#fdeee9", "#eef1e4",
]
HAIR_STYLES = ["ロング", "ショート", "ボブ", "ツインテール", "ポニーテール", "お団子", "短髪"]
EYE_SHAPES = ["まる", "たれ", "つり", "ほそ"]
MOUTHS = ["にっこり", "ふつう", "あいた"]
ACCESSORIES = ["なし", "メガネ", "リボン", "帽子", "イヤリング", "ヘアピン"]


def face_params(seed):
    """seed から顔パーツのパラメータを決定的に決める。"""
    rng = random.Random(f"charamaker-face-{seed}")
    return {
        "skin": rng.choice(SKIN_TONES),
        "hair_color": rng.choice(HAIR_COLORS),
        "hair_style": rng.choice(HAIR_STYLES),
        "eyes": rng.choice(EYE_SHAPES),
        "mouth": rng.choice(MOUTHS),
        "accessory": rng.choice(ACCESSORIES),
        "bg": rng.choice(BG_COLORS),
    }


def _rect(draw, x, y, w, h, color):
    """グリッド座標で矩形を描く（座標はドット単位）。"""
    draw.rectangle(
        [x * SCALE, y * SCALE, (x + w) * SCALE - 1, (y + h) * SCALE - 1],
        fill=color,
    )


def draw_face(seed):
    """seed からドット絵風フェイスを描き、PIL Image を返す。"""
    p = face_params(seed)
    img = Image.new("RGB", (GRID * SCALE, GRID * SCALE), p["bg"])
    d = ImageDraw.Draw(img)
    skin = p["skin"]
    hair = p["hair_color"]
    dark = "#2b2b2b"
    pink = "#f2a0a8"

    # --- 髪の後ろ側（ロング・ツインテール） ---
    if p["hair_style"] == "ロング":
        _rect(d, 6, 6, 20, 22, hair)
    elif p["hair_style"] == "ツインテール":
        _rect(d, 3, 10, 5, 16, hair)
        _rect(d, 24, 10, 5, 16, hair)

    # --- 顔 ---
    _rect(d, 9, 9, 14, 16, skin)
    _rect(d, 10, 25, 12, 2, skin)  # あご側を少し細く

    # --- 髪の前側 ---
    if p["hair_style"] in ("ロング", "ボブ", "ツインテール", "ポニーテール"):
        _rect(d, 8, 6, 16, 5, hair)
        _rect(d, 8, 11, 3, 6, hair)
        _rect(d, 21, 11, 3, 6, hair)
        if p["hair_style"] == "ボブ":
            _rect(d, 8, 17, 3, 6, hair)
            _rect(d, 21, 17, 3, 6, hair)
        if p["hair_style"] == "ポニーテール":
            _rect(d, 22, 4, 5, 10, hair)
    elif p["hair_style"] == "お団子":
        _rect(d, 8, 6, 16, 4, hair)
        _rect(d, 13, 2, 6, 4, hair)
    else:  # ショート・短髪
        _rect(d, 8, 6, 16, 4, hair)
        _rect(d, 8, 10, 2, 3, hair)
        _rect(d, 22, 10, 2, 3, hair)

    # --- ほっぺ ---
    _rect(d, 10, 20, 3, 2, pink)
    _rect(d, 19, 20, 3, 2, pink)

    # --- 目 ---
    for cx in (12, 18):
        if p["eyes"] == "まる":
            _rect(d, cx, 15, 2, 4, dark)
        elif p["eyes"] == "たれ":
            _rect(d, cx, 16, 2, 3, dark)
            _rect(d, cx - 1 if cx == 12 else cx + 1, 15, 1, 1, dark)
        elif p["eyes"] == "つり":
            _rect(d, cx, 15, 2, 3, dark)
            _rect(d, cx + 1 if cx == 12 else cx - 1, 14, 1, 1, dark)
        else:  # ほそ（糸目）
            _rect(d, cx - 1, 17, 4, 1, dark)

    # --- 口 ---
    if p["mouth"] == "にっこり":
        _rect(d, 15, 21, 1, 1, dark)
        _rect(d, 16, 22, 2, 1, dark)
        _rect(d, 18, 21, 1, 1, dark)
    elif p["mouth"] == "あいた":
        _rect(d, 15, 21, 3, 2, "#8a4a3a")
    else:
        _rect(d, 15, 22, 3, 1, dark)

    # --- アクセサリ ---
    acc = p["accessory"]
    if acc == "メガネ":
        for cx in (11, 17):
            d.rectangle(
                [cx * SCALE, 14 * SCALE, (cx + 4) * SCALE - 1, 19 * SCALE - 1],
                outline=dark, width=SCALE // 2,
            )
        _rect(d, 15, 16, 2, 1, dark)
    elif acc == "リボン":
        _rect(d, 21, 4, 3, 3, "#e05a7a")
        _rect(d, 25, 4, 3, 3, "#e05a7a")
        _rect(d, 24, 5, 1, 1, "#b03a58")
    elif acc == "帽子":
        _rect(d, 6, 5, 20, 2, "#4a6fa5")
        _rect(d, 11, 1, 10, 4, "#4a6fa5")
    elif acc == "イヤリング":
        _rect(d, 8, 22, 1, 2, "#e8c33a")
        _rect(d, 23, 22, 1, 2, "#e8c33a")
    elif acc == "ヘアピン":
        _rect(d, 19, 9, 4, 1, "#e8c33a")
        _rect(d, 19, 11, 4, 1, "#e05a7a")

    return img


# ============================================================
# 4. ルーティング
# ============================================================

INDEX_HTML = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>charamaker（キャラクターメーカー）</title>
<style>
  body { font-family: sans-serif; margin: 2em auto; max-width: 640px; padding: 0 1em;
         background: #faf7f2; color: #333; }
  h1 { font-size: 1.4em; }
  .card { background: #fff; border: 1px solid #e2ddd2; border-radius: 12px;
          padding: 1.2em; display: flex; gap: 1.2em; flex-wrap: wrap; }
  .card img { image-rendering: pixelated; border-radius: 8px; }
  table { border-collapse: collapse; }
  th { text-align: left; padding: 0.25em 0.8em 0.25em 0; color: #777; font-weight: normal; }
  td { padding: 0.25em 0; }
  .bio { background: #fff; border: 1px solid #e2ddd2; border-radius: 12px;
         padding: 1em 1.2em; margin-top: 1em; line-height: 1.8; }
  .btn { display: inline-block; background: #e05a7a; color: #fff; padding: 0.7em 1.4em;
         border-radius: 999px; text-decoration: none; margin: 1em 0; }
  .seed { color: #999; font-size: 0.85em; }
</style>
</head>
<body>
<h1>🎲 charamaker（キャラクターメーカー）</h1>
<p>ボタンを押すと、ランダムなキャラクター設定とドット絵フェイスを生成します。</p>
<a class="btn" href="/">🎲 新しいキャラクターを生成</a>
<div class="card">
  <img src="/img?seed={{ c.seed }}" width="192" height="192" alt="キャラクターの顔">
  <table>
    <tr><th>名前</th><td>{{ c.name }}</td></tr>
    <tr><th>年齢</th><td>{{ c.age }}歳</td></tr>
    <tr><th>性別</th><td>{{ c.gender }}</td></tr>
    <tr><th>職業</th><td>{{ c.job }}</td></tr>
    <tr><th>性格</th><td>{{ c.personalities | join("、") }}</td></tr>
    <tr><th>趣味</th><td>{{ c.hobby }}</td></tr>
    <tr><th>特技</th><td>{{ c.skill }}</td></tr>
    <tr><th>口癖</th><td>「{{ c.catchphrase }}」</td></tr>
    <tr><th>好きなもの</th><td>{{ c.favorite }}</td></tr>
  </table>
</div>
<div class="bio">{{ c.bio }}</div>
<p class="seed">seed: {{ c.seed }}（同じ seed の URL ／?seed={{ c.seed }} で再現できます）</p>
</body>
</html>
"""


@app.route("/")
def index():
    seed = _parse_seed(request.args.get("seed"))
    if seed is None:
        seed = random.randrange(0, 2**31)
    character = generate_character(seed)
    return render_template_string(INDEX_HTML, c=character)


@app.route("/img")
def img():
    seed = _parse_seed(request.args.get("seed"))
    if seed is None:
        seed = 0
    image = draw_face(seed)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return Response(buf.getvalue(), mimetype="image/png")


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

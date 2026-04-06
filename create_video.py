#!/usr/bin/env python3
"""禅園 4月懐石コース - テキストオーバーレイ付きMP4動画生成"""

from moviepy import (
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
    vfx,
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

BASE_DIR = "/home/user/0409Zenen-Nishiumeda"

# フォント
FONT_PATH = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"

# 出力サイズ（Instagram推奨 4:5）
OUT_W, OUT_H = 1080, 1350
DURATION_PER_SLIDE = 4
FADE_DURATION = 0.8
ZOOM_FACTOR = 0.05
FPS = 30

# 各スライドの構成: (画像, テキスト行リスト, テキスト位置)
SLIDES = [
    {
        "image": "3Z7A4074修.jpg",
        "texts": ["四月の懐石", "コースのご案内"],
        "position": "center",
        "font_size": 64,
        "sub_texts": ["西梅田 禅園"],
        "sub_font_size": 36,
    },
    {
        "image": "3Z7A3991.jpg",
        "texts": ["━ 春の前菜 ━", "", "桜餅・三色団子・翡翠豆", "春の彩りを盛り込んで"],
        "position": "bottom",
        "font_size": 36,
    },
    {
        "image": "3Z7A4038.jpg",
        "texts": ["季節の懐石コース", "", "旬の食材をふんだんに", "前菜からお造り 焼物 煮物 揚物まで"],
        "position": "bottom",
        "font_size": 36,
    },
    {
        "image": "3Z7A4108.jpg",
        "texts": ["しゃぶしゃぶ懐石コース", "", "厳選されたお肉を", "旬のお造りとともに"],
        "position": "bottom",
        "font_size": 36,
    },
    {
        "image": "3Z7A4140.jpg",
        "texts": ["すき焼き懐石コース", "", "特選和牛の霜降りを", "きのこや旬の食材とともに"],
        "position": "bottom",
        "font_size": 36,
    },
    {
        "image": "3Z7A4025.jpg",
        "texts": ["━ 甘味 ━", "", "抹茶わらび餅", "きな粉と黒豆を添えて"],
        "position": "bottom",
        "font_size": 36,
    },
]

# 最後のエンドカード（店舗情報）
ENDCARD_DURATION = 5


def resize_and_crop_center(img_path):
    """画像を4:5にリサイズ＆中央クロップ"""
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    target_ratio = OUT_W / OUT_H

    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    img = img.resize((OUT_W, OUT_H), Image.LANCZOS)
    return img


def draw_text_overlay(img, texts, position="bottom", font_size=36,
                      sub_texts=None, sub_font_size=28):
    """画像にテキストオーバーレイを描画"""
    overlay = img.copy()
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype(FONT_PATH, font_size)

    # テキスト全体の高さを計算
    line_height = font_size + 12
    total_text_height = len(texts) * line_height

    if sub_texts:
        sub_font = ImageFont.truetype(FONT_PATH, sub_font_size)
        sub_line_height = sub_font_size + 10
        total_text_height += len(sub_texts) * sub_line_height + 20

    # 背景帯の位置
    padding = 40
    if position == "center":
        y_start = (OUT_H - total_text_height) // 2 - padding
        bg_height = total_text_height + padding * 2
    else:  # bottom
        y_start = OUT_H - total_text_height - padding * 2 - 30
        bg_height = total_text_height + padding * 2

    # 半透明の背景帯を描画
    bg_overlay = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg_overlay)
    bg_draw.rectangle(
        [(0, y_start), (OUT_W, y_start + bg_height)],
        fill=(0, 0, 0, 140),
    )
    overlay = Image.alpha_composite(overlay.convert("RGBA"), bg_overlay)
    draw = ImageDraw.Draw(overlay)

    # メインテキスト描画
    y = y_start + padding
    for text in texts:
        if text == "":
            y += 8
            continue
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (OUT_W - text_w) // 2
        # 影
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 200))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        y += line_height

    # サブテキスト描画
    if sub_texts:
        y += 20
        sub_font = ImageFont.truetype(FONT_PATH, sub_font_size)
        for text in sub_texts:
            bbox = draw.textbbox((0, 0), text, font=sub_font)
            text_w = bbox[2] - bbox[0]
            x = (OUT_W - text_w) // 2
            draw.text((x + 1, y + 1), text, font=sub_font, fill=(0, 0, 0, 180))
            draw.text((x, y), text, font=sub_font, fill=(220, 200, 160, 255))
            y += sub_line_height

    return overlay.convert("RGB")


def create_endcard():
    """店舗情報のエンドカードを作成"""
    img = Image.new("RGB", (OUT_W, OUT_H), (30, 10, 10))
    draw = ImageDraw.Draw(img)

    # 装飾ライン
    line_color = (180, 150, 100)
    draw.line([(OUT_W // 4, 280), (OUT_W * 3 // 4, 280)], fill=line_color, width=2)
    draw.line([(OUT_W // 4, 1070), (OUT_W * 3 // 4, 1070)], fill=line_color, width=2)

    # 店名
    title_font = ImageFont.truetype(FONT_PATH, 56)
    sub_font = ImageFont.truetype(FONT_PATH, 30)
    info_font = ImageFont.truetype(FONT_PATH, 26)
    small_font = ImageFont.truetype(FONT_PATH, 22)

    lines = [
        (title_font, "西梅田 禅園", (255, 255, 255), 320),
        (sub_font, "Z E N E N", (180, 150, 100), 400),
        (info_font, "", None, 460),
        (info_font, "〒530-0001", (200, 200, 200), 500),
        (info_font, "大阪府大阪市北区梅田2-5-25", (200, 200, 200), 545),
        (info_font, "ハービスPLAZA（ハービスOSAKA）B2F", (200, 200, 200), 590),
        (info_font, "", None, 650),
        (sub_font, "━ 営業時間 ━", (180, 150, 100), 680),
        (info_font, "ランチ　  11:00〜14:45（L.O. 14:00）", (200, 200, 200), 740),
        (info_font, "ディナー  17:30〜22:00（L.O. 21:00）", (200, 200, 200), 785),
        (small_font, "定休日：不定休（ハービスPLAZA定休日に準ずる）", (160, 160, 160), 840),
        (info_font, "", None, 900),
        (sub_font, "━ ご予約・お問い合わせ ━", (180, 150, 100), 920),
        (title_font, "06-6457-1002", (255, 255, 255), 980),
    ]

    for font, text, color, y in lines:
        if text == "":
            continue
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (OUT_W - text_w) // 2
        draw.text((x, y), text, font=font, fill=color)

    return img


def make_zoom_clip_with_text(slide_info, duration):
    """ズーム＋テキストオーバーレイ付きクリップ"""
    img_path = os.path.join(BASE_DIR, slide_info["image"])
    img = resize_and_crop_center(img_path)

    # テキストオーバーレイ
    img = draw_text_overlay(
        img,
        slide_info["texts"],
        slide_info.get("position", "bottom"),
        slide_info.get("font_size", 36),
        slide_info.get("sub_texts"),
        slide_info.get("sub_font_size", 28),
    )

    # ズーム用に少し大きめ
    zoom_w = int(OUT_W * (1 + ZOOM_FACTOR * 2))
    zoom_h = int(OUT_H * (1 + ZOOM_FACTOR * 2))
    img_large = img.resize((zoom_w, zoom_h), Image.LANCZOS)

    temp_path = os.path.join(BASE_DIR, "_temp_frame.jpg")
    img_large.save(temp_path, quality=95)

    clip = (
        ImageClip(temp_path)
        .with_duration(duration)
        .resized(lambda t: 1 - ZOOM_FACTOR + ZOOM_FACTOR * (t / duration))
    )

    clip = clip.cropped(
        x_center=zoom_w // 2,
        y_center=zoom_h // 2,
        width=OUT_W,
        height=OUT_H,
    )

    return clip


print("テキスト付き動画の生成を開始します...")

clips = []
for i, slide in enumerate(SLIDES):
    fname = slide["image"]
    print(f"  [{i+1}/{len(SLIDES)}] {fname}")
    clip = make_zoom_clip_with_text(slide, DURATION_PER_SLIDE)

    if i > 0:
        clip = clip.with_effects([vfx.CrossFadeIn(FADE_DURATION)])
    if i < len(SLIDES) - 1:
        clip = clip.with_effects([vfx.CrossFadeOut(FADE_DURATION)])
    else:
        clip = clip.with_effects([vfx.CrossFadeOut(FADE_DURATION)])

    clips.append(clip)

# エンドカード作成
print("  [END] 店舗情報カード")
endcard_img = create_endcard()
endcard_path = os.path.join(BASE_DIR, "_temp_endcard.jpg")
endcard_img.save(endcard_path, quality=95)

endcard_clip = (
    ImageClip(endcard_path)
    .with_duration(ENDCARD_DURATION)
    .with_effects([vfx.CrossFadeIn(FADE_DURATION), vfx.FadeOut(1.0)])
)
clips.append(endcard_clip)

# 結合
final = concatenate_videoclips(clips, method="compose", padding=-FADE_DURATION)

output_path = os.path.join(BASE_DIR, "april_kaiseki_slideshow.mp4")
final.write_videofile(
    output_path,
    fps=FPS,
    codec="libx264",
    audio=False,
    preset="medium",
    bitrate="5000k",
)

# 一時ファイル削除
for f in ["_temp_frame.jpg", "_temp_endcard.jpg"]:
    p = os.path.join(BASE_DIR, f)
    if os.path.exists(p):
        os.remove(p)

print(f"\n✅ 動画を生成しました: {output_path}")
size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"   ファイルサイズ: {size_mb:.1f} MB")
dur = final.duration
print(f"   動画の長さ: 約{dur:.1f}秒")

#!/usr/bin/env python3
"""禅園 4月懐石コース - 4コース紹介＋BGM付きMP4動画生成"""

from moviepy import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    vfx,
    afx,
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

BASE_DIR = "/home/user/0409Zenen-Nishiumeda"
BGM_PATH = os.path.join(BASE_DIR, "Wet_Streets_at_Two.mp3")
FONT_PATH = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"

OUT_W, OUT_H = 1080, 1350
FADE_DURATION = 0.8
ZOOM_FACTOR = 0.05
FPS = 30

# ── スライド構成 ──
SLIDES = [
    # 1. タイトル
    {
        "image": "3Z7A4074修.jpg",
        "duration": 4,
        "texts": ["四月の懐石", "コースのご案内"],
        "position": "center",
        "font_size": 64,
        "sub_texts": ["西梅田 禅園"],
        "sub_font_size": 36,
    },
    # 2. 前菜（全コース共通）
    {
        "image": "3Z7A3991.jpg",
        "duration": 4,
        "texts": ["━  前 菜  ━", "", "うすい豆  筍木乃芽和え", "さより小袖寿司  桜葉", "三色団子  桜海老  バイ貝旨煮"],
        "position": "bottom",
        "font_size": 32,
        "tag": "全コース共通",
    },
    # 3. 紫紺コース
    {
        "image": "3Z7A4038.jpg",
        "duration": 5,
        "texts": [
            "紫紺（しこん）コース",
            "7,800円",
            "",
            "造里｜初鰹・桜鯛・平貝",
            "焼物｜鰆二色焼き 木の芽味噌",
            "温物｜若竹煮 鯛の子",
        ],
        "position": "bottom",
        "font_size": 32,
        "title_lines": 2,
    },
    # 4. 花緑青コース
    {
        "image": "3Z7A4074修.jpg",
        "duration": 5,
        "texts": [
            "花緑青（はなろくしょう）コース",
            "9,800円",
            "",
            "造里｜本鮪 縞鯵 キャビア 赤貝",
            "焼物｜黒毛和牛ロース炙り 甘夏ソース",
            "温物｜めばるの南蛮煮",
        ],
        "position": "bottom",
        "font_size": 32,
        "title_lines": 2,
    },
    # 5. 宗伝唐茶コース
    {
        "image": "3Z7A4108.jpg",
        "duration": 5,
        "texts": [
            "宗伝唐茶（そうでんからちゃ）コース",
            "12,800円",
            "",
            "椀物｜新玉葱すり流し 鴨ロース",
            "造里｜鰆焼霜・剣先烏賊・本鮪・赤貝",
            "焼物｜黒毛和牛ロース炙り",
            "温物｜ホタルイカしゃぶしゃぶ小鍋",
        ],
        "position": "bottom",
        "font_size": 30,
        "title_lines": 2,
    },
    # 6. 空五倍子色コース
    {
        "image": "3Z7A4140.jpg",
        "duration": 5,
        "texts": [
            "空五倍子色（うつぶしいろ）コース",
            "15,800円",
            "",
            "造里｜縞鯵薄造里 鮑 本鮪にぎり 雲丹肉巻き",
            "焼物｜甘鯛塩焼き",
            "温物｜黒毛和牛サーロインすき焼き小鍋",
        ],
        "position": "bottom",
        "font_size": 30,
        "title_lines": 2,
    },
    # 7. 甘味（全コース共通）
    {
        "image": "3Z7A4025.jpg",
        "duration": 4,
        "texts": ["━  甘 味  ━", "", "抹茶プリン"],
        "position": "bottom",
        "font_size": 36,
        "tag": "全コース共通",
    },
    # 8. 鯛飯（テキストのみ、背景は前菜画像を暗くして）
    {
        "image": "3Z7A4038.jpg",
        "duration": 4,
        "darken": True,
        "texts": [
            "全コース共通",
            "",
            "名物",
            "明石の天然真鯛を使った鯛飯",
            "",
            "香の物・味噌汁とともに",
        ],
        "position": "center",
        "font_size": 36,
    },
]

ENDCARD_DURATION = 5


def resize_and_crop_center(img_path):
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


def draw_text_overlay(img, slide):
    texts = slide["texts"]
    position = slide.get("position", "bottom")
    font_size = slide.get("font_size", 32)
    sub_texts = slide.get("sub_texts")
    sub_font_size = slide.get("sub_font_size", 28)
    tag = slide.get("tag")
    title_lines = slide.get("title_lines", 0)
    darken = slide.get("darken", False)

    overlay = img.copy()

    # 画像全体を暗くする
    if darken:
        dark = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 160))
        overlay = Image.alpha_composite(overlay.convert("RGBA"), dark).convert("RGB")

    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype(FONT_PATH, font_size)
    price_font = ImageFont.truetype(FONT_PATH, int(font_size * 0.9))
    tag_font = ImageFont.truetype(FONT_PATH, 22)

    line_height = font_size + 14
    total_text_height = 0
    for t in texts:
        if t == "":
            total_text_height += 10
        else:
            total_text_height += line_height

    if tag:
        total_text_height += 36
    if sub_texts:
        sub_line_height = sub_font_size + 10
        total_text_height += len(sub_texts) * sub_line_height + 20

    padding = 40
    if position == "center":
        y_start = (OUT_H - total_text_height) // 2 - padding
    else:
        y_start = OUT_H - total_text_height - padding * 2 - 30
    bg_height = total_text_height + padding * 2

    # 半透明背景
    bg_overlay = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg_overlay)
    bg_draw.rectangle(
        [(0, y_start), (OUT_W, y_start + bg_height)],
        fill=(0, 0, 0, 150),
    )
    overlay = Image.alpha_composite(overlay.convert("RGBA"), bg_overlay)
    draw = ImageDraw.Draw(overlay)

    y = y_start + padding

    # タグ（全コース共通 など）
    if tag:
        bbox = draw.textbbox((0, 0), tag, font=tag_font)
        tw = bbox[2] - bbox[0]
        x = (OUT_W - tw) // 2
        draw.text((x, y), tag, font=tag_font, fill=(220, 200, 160, 255))
        y += 36

    # メインテキスト
    for i, text in enumerate(texts):
        if text == "":
            y += 10
            continue

        # タイトル行（コース名・価格）は金色
        if title_lines and i < title_lines:
            use_font = font if i == 0 else price_font
            color = (220, 200, 160, 255)
        else:
            use_font = font
            color = (255, 255, 255, 255)

        bbox = draw.textbbox((0, 0), text, font=use_font)
        tw = bbox[2] - bbox[0]
        x = (OUT_W - tw) // 2
        draw.text((x + 2, y + 2), text, font=use_font, fill=(0, 0, 0, 200))
        draw.text((x, y), text, font=use_font, fill=color)
        y += line_height

    # サブテキスト
    if sub_texts:
        y += 20
        sub_font = ImageFont.truetype(FONT_PATH, sub_font_size)
        for text in sub_texts:
            bbox = draw.textbbox((0, 0), text, font=sub_font)
            tw = bbox[2] - bbox[0]
            x = (OUT_W - tw) // 2
            draw.text((x + 1, y + 1), text, font=sub_font, fill=(0, 0, 0, 180))
            draw.text((x, y), text, font=sub_font, fill=(220, 200, 160, 255))
            y += sub_font_size + 10

    return overlay.convert("RGB")


def create_endcard():
    img = Image.new("RGB", (OUT_W, OUT_H), (30, 10, 10))
    draw = ImageDraw.Draw(img)

    line_color = (180, 150, 100)
    draw.line([(OUT_W // 4, 280), (OUT_W * 3 // 4, 280)], fill=line_color, width=2)
    draw.line([(OUT_W // 4, 1070), (OUT_W * 3 // 4, 1070)], fill=line_color, width=2)

    title_font = ImageFont.truetype(FONT_PATH, 56)
    sub_font = ImageFont.truetype(FONT_PATH, 30)
    info_font = ImageFont.truetype(FONT_PATH, 26)
    small_font = ImageFont.truetype(FONT_PATH, 22)

    lines = [
        (title_font, "西梅田 禅園", (255, 255, 255), 320),
        (sub_font, "Z E N E N", (180, 150, 100), 400),
        (info_font, "〒530-0001", (200, 200, 200), 500),
        (info_font, "大阪府大阪市北区梅田2-5-25", (200, 200, 200), 545),
        (info_font, "ハービスPLAZA（ハービスOSAKA）B2F", (200, 200, 200), 590),
        (sub_font, "━ 営業時間 ━", (180, 150, 100), 680),
        (info_font, "ランチ　  11:00〜14:45（L.O. 14:00）", (200, 200, 200), 740),
        (info_font, "ディナー  17:30〜22:00（L.O. 21:00）", (200, 200, 200), 785),
        (small_font, "定休日：不定休（ハービスPLAZA定休日に準ずる）", (160, 160, 160), 840),
        (sub_font, "━ ご予約・お問い合わせ ━", (180, 150, 100), 920),
        (title_font, "06-6457-1002", (255, 255, 255), 980),
    ]

    for font, text, color, y_pos in lines:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (OUT_W - tw) // 2
        draw.text((x, y_pos), text, font=font, fill=color)

    return img


def make_zoom_clip(slide, duration):
    img_path = os.path.join(BASE_DIR, slide["image"])
    img = resize_and_crop_center(img_path)
    img = draw_text_overlay(img, slide)

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
        x_center=zoom_w // 2, y_center=zoom_h // 2,
        width=OUT_W, height=OUT_H,
    )
    return clip


print("4コース紹介動画の生成を開始します...")

clips = []
for i, slide in enumerate(SLIDES):
    print(f"  [{i+1}/{len(SLIDES)}] {slide['image']} - {slide['texts'][0]}")
    duration = slide["duration"]
    clip = make_zoom_clip(slide, duration)

    if i > 0:
        clip = clip.with_effects([vfx.CrossFadeIn(FADE_DURATION)])
    if i < len(SLIDES) - 1:
        clip = clip.with_effects([vfx.CrossFadeOut(FADE_DURATION)])
    else:
        clip = clip.with_effects([vfx.CrossFadeOut(FADE_DURATION)])

    clips.append(clip)

# エンドカード
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

# BGM
print("  [BGM] Wet_Streets_at_Two.mp3")
bgm = AudioFileClip(BGM_PATH)
video_duration = final.duration
if bgm.duration > video_duration:
    bgm = bgm.subclipped(0, video_duration)
else:
    # BGMが短い場合はループ
    loops = int(video_duration / bgm.duration) + 1
    from moviepy import concatenate_audioclips
    bgm = concatenate_audioclips([bgm] * loops).subclipped(0, video_duration)
bgm = bgm.with_effects([afx.AudioFadeOut(2.5)])
final = final.with_audio(bgm)

output_path = os.path.join(BASE_DIR, "april_kaiseki_slideshow.mp4")
final.write_videofile(
    output_path,
    fps=FPS, codec="libx264",
    audio_codec="aac", audio_bitrate="192k",
    preset="medium", bitrate="5000k",
)

# 一時ファイル削除
for f in ["_temp_frame.jpg", "_temp_endcard.jpg"]:
    p = os.path.join(BASE_DIR, f)
    if os.path.exists(p):
        os.remove(p)

print(f"\n✅ 動画を生成しました: {output_path}")
size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"   ファイルサイズ: {size_mb:.1f} MB")
print(f"   動画の長さ: 約{final.duration:.1f}秒")
print(f"   BGM: Wet_Streets_at_Two.mp3（フェードアウト付き）")

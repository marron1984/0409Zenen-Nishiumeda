#!/usr/bin/env python3
"""禅園 4月懐石コース - スライドショーMP4動画生成"""

from moviepy import (
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
    vfx,
)
from PIL import Image
import os

BASE_DIR = "/home/user/0409Zenen-Nishiumeda"

# カルーセル順に画像を配置
image_files = [
    "3Z7A4074修.jpg",   # 1. メインビジュアル（コース集合②）
    "3Z7A3991.jpg",     # 2. 前菜（共通）
    "3Z7A4038.jpg",     # 3. コース集合①
    "3Z7A4108.jpg",     # 4. お造り・しゃぶしゃぶ
    "3Z7A4140.jpg",     # 5. 和牛すき焼き
    "3Z7A4025.jpg",     # 6. 甘味（共通）
]

# 出力サイズ（Instagram推奨 4:5）
OUT_W, OUT_H = 1080, 1350
DURATION_PER_SLIDE = 4  # 各スライド秒数
FADE_DURATION = 0.8     # フェード秒数
ZOOM_FACTOR = 0.05      # ズーム量（5%）
FPS = 30

def resize_and_crop_center(img_path):
    """画像を4:5にリサイズ＆中央クロップ"""
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    target_ratio = OUT_W / OUT_H  # 0.8

    if w / h > target_ratio:
        # 横長 → 高さに合わせて幅をクロップ
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        # 縦長 → 幅に合わせて高さをクロップ
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    img = img.resize((OUT_W, OUT_H), Image.LANCZOS)
    return img


def make_zoom_clip(img_path, duration):
    """ゆっくりズームインするクリップを作成"""
    img = resize_and_crop_center(img_path)
    # 少し大きめの画像を用意してズーム効果を出す
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

    # 中央にクロップ
    clip = clip.cropped(
        x_center=zoom_w // 2,
        y_center=zoom_h // 2,
        width=OUT_W,
        height=OUT_H,
    )

    return clip


print("動画生成を開始します...")

clips = []
for i, fname in enumerate(image_files):
    path = os.path.join(BASE_DIR, fname)
    print(f"  [{i+1}/{len(image_files)}] {fname}")
    clip = make_zoom_clip(path, DURATION_PER_SLIDE)

    # フェードイン/アウト
    if i > 0:
        clip = clip.with_effects([vfx.CrossFadeIn(FADE_DURATION)])
    if i < len(image_files) - 1:
        clip = clip.with_effects([vfx.CrossFadeOut(FADE_DURATION)])
    else:
        # 最後のクリップはフェードアウトのみ
        clip = clip.with_effects([vfx.FadeOut(FADE_DURATION)])

    clips.append(clip)

# クリップを結合（クロスフェード付き）
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
temp = os.path.join(BASE_DIR, "_temp_frame.jpg")
if os.path.exists(temp):
    os.remove(temp)

print(f"\n✅ 動画を生成しました: {output_path}")

# ファイルサイズ確認
size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"   ファイルサイズ: {size_mb:.1f} MB")
duration_total = DURATION_PER_SLIDE * len(image_files) - FADE_DURATION * (len(image_files) - 1)
print(f"   動画の長さ: 約{duration_total:.1f}秒")

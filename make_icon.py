# -*- coding: utf-8 -*-
"""从 idle GIF 生成美叽应用图标 meji.ico（多尺寸，透明底）。"""
import os
from PIL import Image, ImageSequence

os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
src = os.path.join("assets", "150", "meji_idle_t.gif")
im = Image.open(src)

# 选一个身体完整、睁眼的帧（取中间偏前一帧）
n = getattr(im, "n_frames", 1)
frame = None
for fi in range(n):
    im.seek(fi)
    f = im.convert("RGBA")
    bbox = f.getbbox()
    if bbox:
        w = bbox[2] - bbox[0]; h = bbox[3] - bbox[1]
        # 选身体尺寸较大的一帧（完整站姿）
        if frame is None or w * h > frame[1]:
            frame = (f.crop(bbox), w * h, fi)
crop, _, chosen = frame
print("选帧", chosen, "裁切", crop.size)

# 正方形画布，四周留 8% 边距
cw, ch = crop.size
side = int(max(cw, ch) * 1.16)
canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
canvas.alpha_composite(crop, ((side - cw) // 2, (side - ch) // 2))

base = canvas.resize((256, 256), Image.LANCZOS)
ico = "meji.ico"
base.save(ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
# 同时存一张 256 png 供检查
base.save("_analysis/meji_icon256.png")
print("saved", ico, os.path.getsize(ico), "bytes")

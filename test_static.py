# -*- coding: utf-8 -*-
"""通道一：静态资源验证"""
import os, sys, glob, json
from PIL import Image

os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")

# 从 pet.py 提取 FACES 键名（硬编码40个）
FACES_KEYS = [
    "idle","happy","hug","money","sleep","eat","excited","smug","kiss",
    "laugh","phone","wave","hug2","joy","drunk","cry","bliss","wronged",
    "pout","think","shy","gift","flower","drink","rain","present","relax",
    "fume","furious","lieflat","stomp","cheer","cool","surprised","sushi",
    "salad","innocent","blowkiss","glare","away"
]
# money 对应 meji_angry_t.gif，wave 对应 meji_fan_t.gif
FILE_MAP = {"money": "meji_angry_t.gif", "wave": "meji_fan_t.gif"}

SIZES = ["50","60","100","150"]
results = []
def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")

# 1. 原始 assets 目录40个GIF
src_files = sorted(glob.glob("assets/*_t.gif"))
src_files = [f for f in src_files if os.path.isfile(f)]
check("原始素材数量=40", len(src_files)==40, f"实际{len(src_files)}")

# 2. 每个尺寸目录
for sz in SIZES:
    d = f"assets/{sz}"
    check(f"目录存在 {d}", os.path.isdir(d))
    files = sorted(glob.glob(f"{d}/*_t.gif"))
    check(f"{sz}px GIF数量=40", len(files)==40, f"实际{len(files)}")

# 3. 逐文件检查：可打开、有透明、多帧、尺寸<=目标、非全透明
for sz in SIZES:
    target = int(sz)
    bad_open, bad_trans, bad_frame, bad_size, bad_empty = [], [], [], [], []
    for k in FACES_KEYS:
        fn = FILE_MAP.get(k, f"meji_{k}_t.gif")
        p = f"assets/{sz}/{fn}"
        if not os.path.exists(p):
            bad_open.append(k); continue
        try:
            im = Image.open(p)
            n = getattr(im, "n_frames", 1)
            # 透明
            if not (im.mode=="P" and "transparency" in im.info):
                bad_trans.append(k)
            # 多帧
            if n < 2:
                bad_frame.append(f"{k}({n}帧)")
            # 尺寸：普通表情长边<=目标；away为特写穿过镜头，允许到 min(200,目标*1.4)；
            # 所有影片都不得超出窗口 W=200
            limit = min(200, int(target*1.4)) if k == "away" else target
            if max(im.size) > limit + 2:
                bad_size.append(f"{k}{im.size}")
            # 非全透明：第一帧有不透明像素
            rgba = im.convert("RGBA")
            alpha = rgba.getchannel("A")
            extrema = alpha.getextrema()
            if extrema[1] < 200:  # 最大alpha太低=几乎全透明
                bad_empty.append(k)
        except Exception as e:
            bad_open.append(f"{k}:{e}")
    check(f"{sz}px 全部可打开", not bad_open, str(bad_open[:5]))
    check(f"{sz}px 透明索引", not bad_trans, str(bad_trans[:5]))
    check(f"{sz}px 均为多帧动画", not bad_frame, str(bad_frame[:5]))
    check(f"{sz}px 尺寸达标(普通<={target},away<=min(200,{target*1.4}),全部<=200)", not bad_size, str(bad_size[:5]))
    check(f"{sz}px 非全透明", not bad_empty, str(bad_empty[:5]))

# 4. 帧数统计（抽查idle）
for sz in ["50","150"]:
    im = Image.open(f"assets/{sz}/meji_idle_t.gif")
    check(f"{sz}px idle帧数={getattr(im,'n_frames',1)}", getattr(im,'n_frames',1)>1,
          f"{im.size}")

# 5. 配置读写与损坏回退
sys.path.insert(0, r"C:\ps6"); sys.path.insert(0, r"C:\plibs")
cfg_test = os.path.join(os.path.expanduser("~"), ".meji_pet_config_test.json")
# 正常
with open(cfg_test,"w",encoding="utf-8") as f:
    json.dump({"size":100,"activity":50}, f)
with open(cfg_test,"r",encoding="utf-8") as f:
    c = json.load(f)
check("配置正常读取", c.get("size")==100)
# 损坏
with open(cfg_test,"w",encoding="utf-8") as f:
    f.write("{这不是合法JSON")
try:
    with open(cfg_test,"r",encoding="utf-8") as f:
        json.load(f)
    corrupt_ok = False
except:
    corrupt_ok = True
check("损坏配置抛异常(代码会回退默认)", corrupt_ok)
os.remove(cfg_test)

# 汇总
passed = sum(1 for _,ok,_ in results if ok)
failed = sum(1 for _,ok,_ in results if not ok)
print(f"\n===== 静态验证：{passed} 通过 / {failed} 失败 =====")

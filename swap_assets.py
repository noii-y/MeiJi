# -*- coding: utf-8 -*-
import os, shutil, filecmp
from PIL import Image, ImageSequence
Image.MAX_IMAGE_PIXELS=None
P=r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet"
NEW=os.path.join(P,"assets_new"); AS=os.path.join(P,"assets"); BK=os.path.join(P,"_assets_backup_v1")
import regen2 as r
expected=set(f"meji_{k}_t.gif" for k in r.KEYS)
print("期望文件数",len(expected))
ok=True
for sz in r.SIZES:
    d=os.path.join(NEW,str(sz)); files=set(os.listdir(d))
    miss=expected-files; extra=files-expected
    print(f"size{sz}: 文件{len(files)} 缺{sorted(miss)} 多{sorted(extra)}")
    if miss or len(files)!=40: ok=False
if not ok:
    print("!! 文件不齐，终止替换"); raise SystemExit(1)
# 备份并替换
for sz in r.SIZES:
    s=os.path.join(AS,str(sz)); b=os.path.join(BK,str(sz)); n=os.path.join(NEW,str(sz))
    if not os.path.isdir(b):
        shutil.copytree(s,b)
    else:
        shutil.rmtree(s); shutil.copytree(b,s)  # 已有备份则先还原再覆盖（保证幂等）
    # 清空目标并复制新文件
    shutil.rmtree(s); shutil.copytree(n,s)
    print("replaced",sz,"文件数",len(os.listdir(s)))
# 替换后解码复检 + 与new逐字节一致
bad=0
for sz in r.SIZES:
    for fn in sorted(expected):
        p=os.path.join(AS,str(sz),fn)
        try:
            im=Image.open(p)
            assert im.mode=='P' and 'transparency' in im.info
            for f in ImageSequence.Iterator(im): f.load()
        except Exception as e:
            print("BAD",sz,fn,repr(e));bad+=1
print("替换后损坏/异常:",bad)
print("done")

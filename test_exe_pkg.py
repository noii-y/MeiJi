# -*- coding: utf-8 -*-
"""验证 EXE 内是否打包了 assets 四个尺寸子目录"""
import sys, os
sys.path.insert(0, r"C:\plibs")
from PyInstaller.archive.readers import CArchiveReader

exe = r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet\dist\MejiPet.exe"
arc = CArchiveReader(exe)
names = arc.toc.keys() if hasattr(arc,'toc') else []
# 收集所有条目名
allnames = list(names)
asset_entries = [n for n in allnames if 'assets' in str(n).lower() or n.endswith('.gif')]
print("总条目数:", len(allnames))
print("assets相关条目数:", len(asset_entries))
# 统计每个尺寸目录的gif
for sz in ["50","60","100","150"]:
    cnt = sum(1 for n in asset_entries if f"assets/{sz}/" in str(n).replace("\\","/"))
    print(f"  assets/{sz}/ : {cnt} 个gif")
# 顶层assets
top = sum(1 for n in asset_entries if str(n).replace("\\","/").count("/")==1 and n.endswith('.gif'))
print("  assets/ 顶层gif:", top)

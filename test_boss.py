# -*- coding: utf-8 -*-
"""批次F：老板键隐藏/召回 + 素材正名后 money/wave 正常加载（offscreen）。"""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
sys.path.insert(0, r"C:\ps6"); sys.path.insert(0, r"C:\plibs")

import pet as P
from PySide6.QtWidgets import QApplication
app = QApplication([])
results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")

mgr = P.PetManager()
P.Pet.manager = mgr
p = mgr.spawn()
app.processEvents()
check("召唤后宠物可见", p.isVisible())

# 老板键隐藏
mgr.boss_toggle()
check("老板键隐藏：所有宠物不可见", all(not x.isVisible() for x in mgr.pets) and mgr._boss_hidden)
# 再按召回
mgr.boss_toggle()
check("老板键召回：宠物重新可见", all(x.isVisible() for x in mgr.pets) and not mgr._boss_hidden)

# 结构检查：热键与托盘菜单存在
src = open("pet.py", encoding="utf-8").read()
check("含全局热键注册代码", "RegisterHotKey" in src and "_hotkey_loop" in src)
check("托盘菜单含emoji与老板键项", "🙈" in src and "🚪" in src and "🌻" in src)

# 素材正名：money/wave 文件存在且能加载，且旧名已不存在
ad = os.path.join("assets", str(p.cfg.get("size", 60)))
check("money/wave 新文件名存在",
      os.path.exists(os.path.join(ad, "meji_money_t.gif")) and
      os.path.exists(os.path.join(ad, "meji_wave_t.gif")))
check("旧 angry/fan 运行时文件已移除",
      not os.path.exists(os.path.join(ad, "meji_angry_t.gif")) and
      not os.path.exists(os.path.join(ad, "meji_fan_t.gif")))
p.face("money"); p.face("wave")
check("money/wave 表情可切换", p.movies.get("money") is not None and p.movies.get("wave") is not None)

mgr.quit_all if False else None
for x in mgr.pets:
    x.close_pet()
passed = sum(results); total = len(results)
print(f"\n===== 老板键/正名测试：{passed}/{total} 通过 =====")
sys.exit(0 if passed == total else 1)

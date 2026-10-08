# -*- coding: utf-8 -*-
"""批次E：自适应 tick——走路高频、发呆低频；GIF 播放不受 tick 降频影响。"""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
sys.path.insert(0, r"C:\ps6"); sys.path.insert(0, r"C:\plibs")

import pet as P
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QMovie
app = QApplication([])
results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")

P.Pet.manager = None
p = P.Pet()

# 发呆：无走动目标 -> 低频
p.walk_target = None
p._update_tick_rate()
check("发呆时 tick=250ms", p.timer.interval() == 250, str(p.timer.interval()))

# 走动开始 -> 高频
p.start_walk()
check("走动时 tick=30ms", p.timer.interval() == 30, str(p.timer.interval()))

# 走动结束 -> 回低频
p.walk_target = None
p._update_tick_rate()
check("走动结束回 250ms", p.timer.interval() == 250)

# 走开（也是 walk）-> 高频
p.start_away()
check("走开时 tick=30ms", p.timer.interval() == 30)

# 降频后 QMovie 仍在自行播放（GIF 不动依赖 tick）
p.walk_target = None
p._update_tick_rate()
check("低频下 GIF 仍在播放", p.current_movie is not None and
      p.current_movie.state() == QMovie.Running,
      str(p.current_movie.state() if p.current_movie else None))

p.close_pet()
passed = sum(results); total = len(results)
print(f"\n===== 自适应tick测试：{passed}/{total} 通过 =====")
sys.exit(0 if passed == total else 1)

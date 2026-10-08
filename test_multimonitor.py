# -*- coding: utf-8 -*-
"""批次D：多显示器可用区域钳制（offscreen 下用主屏与极端坐标验证回退逻辑）。"""
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

screens = QApplication.screens()
check("至少检测到一个显示器", len(screens) >= 1, f"{len(screens)}个")

P.Pet.manager = None
p = P.Pet()
g = p._screen.availableGeometry()
check("初始位置在主屏可用区域内",
      g.left() <= p.px <= g.right()+1-P.W and g.top() <= p.py <= g.bottom()+1-P.W,
      f"px={p.px:.0f} py={p.py:.0f} g=({g.left()},{g.top()},{g.width()}x{g.height()})")

# 屏内点钳制后仍在区域内
x, y = p.clamp_to_screen(g.left() + 200, g.top() + 200)
check("屏内点钳制保持在区域内",
      g.left() <= x <= g.right()+1-P.W and g.top() <= y <= g.bottom()+1-P.W,
      f"{x:.0f},{y:.0f}")

# 极端坐标（无显示器命中）回退到主屏并钳到左上角
x2, y2 = p.clamp_to_screen(-10000, -10000)
check("极端左上回退主屏左上角", x2 == g.left() and y2 == g.top(), f"{x2:.0f},{y2:.0f}")

# 极端右下钳到主屏右下角
x3, y3 = p.clamp_to_screen(999999, 999999)
check("极端右下钳到主屏右下角", x3 == g.right()+1-P.W and y3 == g.bottom()+1-P.W,
      f"{x3:.0f},{y3:.0f}")

# 走开目标在当前屏幕右边缘之外
p.start_away()
check("走开目标在屏幕右缘之外", p.walk_target[0] > g.right(),
      f"tx={p.walk_target[0]:.0f} right={g.right()}")

# 走动目标不超出当前屏幕
p._away_mode = False
p.start_walk()
tx, ty = p.walk_target
check("走动目标在屏幕可用区域内",
      g.left() <= tx <= g.right()+1-P.W and g.top() <= ty <= g.bottom()+1-P.W,
      f"{tx:.0f},{ty:.0f}")

p.close_pet()
passed = sum(results); total = len(results)
print(f"\n===== 多显示器测试：{passed}/{total} 通过 =====")
sys.exit(0 if passed == total else 1)

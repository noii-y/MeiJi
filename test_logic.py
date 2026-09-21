# -*- coding: utf-8 -*-
"""通道一补充：无头逻辑测试（offscreen）"""
import os, sys, random
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
sys.path.insert(0, r"C:\ps6"); sys.path.insert(0, r"C:\plibs")

import pet as P
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint, QEvent
from PySide6.QtGui import QMouseEvent

app = QApplication([])
results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")

mgr = P.PetManager()
P.Pet.manager = mgr
p = mgr.spawn()

# 1. 初始40个movie
check("初始加载40个movie", len(p.movies)==40, str(len(p.movies)))

# 2. 四个尺寸切换不崩、movie数=40、尺寸正确
for sz,exp in [(50,52),(60,60),(100,100),(150,150)]:
    p.set_size(sz)
    app.processEvents()
    idle_w = p.movie_sizes["idle"].width()
    check(f"切尺寸{sz}: movie=40且idle宽<=目标", len(p.movies)==40 and idle_w<=sz+2,
          f"movies={len(p.movies)} idle_w={idle_w}")

# 3. face切换所有40表情不崩
ok_all = True
for k in list(P.FACES.keys()):
    try:
        p.face(k); app.processEvents()
    except Exception as e:
        ok_all = False; print("  err", k, e)
check("40表情逐个切换不崩", ok_all)

# 4. 单击延迟 + 双击取消
p.set_size(60)
p._click_token = 0
# 模拟单击release
class FakeBtn:
    def button(self): return Qt.LeftButton
p.mouseReleaseEvent(FakeBtn())
tok_after_single = p._click_token
# 立刻双击（应取消挂起的单击）
p.mouseDoubleClickEvent(FakeBtn())
check("双击使click token递增(取消单击)", p._click_token == tok_after_single+1,
      f"{tok_after_single}->{p._click_token}")

# 5. 拖拽边界钳制：模拟把鼠标甩到屏幕外
p._drag_pos = QPoint(50, 50)
p._press_start = QPoint(0,0)
class FakeMove:
    def button(self): return Qt.LeftButton
    def globalPosition(self):
        class GP:
            def toPoint(self2): return QPoint(-500, -500)  # 甩到屏幕外左上
        return GP()
p.mouseMoveEvent(FakeMove())
check("拖拽左上不越界 px>=0,py>=0", p.px>=0 and p.py>=0, f"px={p.px:.0f} py={p.py:.0f}")
class FakeMove2:
    def button(self): return Qt.LeftButton
    def globalPosition(self):
        class GP:
            def toPoint(self2): return QPoint(99999, 99999)
        return GP()
p.mouseMoveEvent(FakeMove2())
check("拖拽右下不越界", p.px<=p.screen_w-P.W and p.py<=p.screen_h-P.W,
      f"px={p.px:.0f} py={p.py:.0f} 上限={p.screen_w-P.W},{p.screen_h-P.W}")
p._drag_pos = None; p._moved = False

# 6. 自动轮换多样性：跑60次do_auto_step，统计不同表情
p.fullness = 90; p.mood = 90
seen = set()
away_count = 0
for _ in range(200):
    random.seed()  # 真随机
    before = p.auto_state
    p.do_auto_step()
    app.processEvents()
    if p._away_mode:
        away_count += 1
        p._away_mode = False  # 复位便于继续
    seen.add(p.auto_state)
check("自动轮换出现>=8种表情", len(seen)>=8, f"{len(seen)}种: {sorted(seen)[:10]}")
check("走开事件可触发(200次内)", away_count>=1, f"{away_count}次")

# 7. 饥饿表情
p.fullness = 10; p.mood = 90
hungry_faces = set()
for _ in range(30):
    p.do_auto_step(); app.processEvents()
    hungry_faces.add(p.auto_state)
check("饥饿时出哭/委屈/无辜", hungry_faces <= {"cry","wronged","innocent"} and len(hungry_faces)>=1,
      str(hungry_faces))

# 8. 5只上限
for _ in range(6):
    mgr.spawn(); app.processEvents()
check("最多5只", len(mgr.pets)==5, f"{len(mgr.pets)}只")
# summon菜单第6次不增加
p.summon()
check("第6次召唤被拒绝", len(mgr.pets)==5)

# 9. 菜单选中标记
p.set_size(100); p.set_activity(80)
p._refresh_menu_checks()
check("大小菜单100被勾选", p._size_actions[100].isChecked())
check("活跃度菜单80被勾选", p._act_actions[80].isChecked())
check("其他尺寸未勾选", not p._size_actions[50].isChecked())

# 10. 走开-回来流程
p2 = mgr.pets[0]
p2._away_mode=False; p2.walk_target=None
p2.start_away()
check("start_away: away模式+目标在屏幕外", p2._away_mode and p2.walk_target[0]>=p2.screen_w,
      f"tx={p2.walk_target[0]:.0f} screen_w={p2.screen_w}")
check("start_away: 当前脸=away", p2.current_face_key=="away", p2.current_face_key)

passed=sum(results); total=len(results)
print(f"\n===== 逻辑测试：{passed}/{total} 通过 =====")
sys.exit(0 if passed==total else 1)

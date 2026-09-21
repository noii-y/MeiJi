# -*- coding: utf-8 -*-
"""点击切换常驻表情 + 常驻表情不卡帧 的无头逻辑测试"""
import os, sys, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
sys.path.insert(0, r"C:\ps6"); sys.path.insert(0, r"C:\plibs")

import pet as P
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint

app = QApplication([])
res = []
def check(name, ok, detail=""):
    res.append(bool(ok)); print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")

mgr = P.PetManager(); P.Pet.manager = mgr
p = mgr.spawn()
p.set_size(60)

# 给 face / do_auto_step 装计数器
face_calls = []
orig_face = P.Pet.face
def spy_face(self, f):
    face_calls.append(f); return orig_face(self, f)
P.Pet.face = spy_face
auto_calls = []
orig_auto = P.Pet.do_auto_step
def spy_auto(self):
    auto_calls.append(1); return orig_auto(self)
P.Pet.do_auto_step = spy_auto

# 1. 点击池
check("点击池=39(40-away)", len(P.CLICK_POOL)==39, str(len(P.CLICK_POOL)))
check("away 不在点击池", "away" not in P.CLICK_POOL)
check("点击池每个键都能映射到自身movie",
      all(P.STATE_FACE.get(k)==k and k in p.movies for k in P.CLICK_POOL))

# 2. 单击 -> 常驻；连续多次 tick 不被重载(不卡帧)
face_calls.clear()
p._click_token += 1; tok = p._click_token
p._do_single_click(tok)
sel = p.auto_state
check("单击后 state==auto_state", p.state==sel==p.current_face_key, sel)
check("单击选中的不是away", sel!="away")
n0 = len(face_calls)
for _ in range(60):
    p.tick()
check("常驻表情跨60次tick不被重载(卡帧修复)", len(face_calls)==n0,
      f"额外face调用={len(face_calls)-n0}")
check("常驻表情跨tick仍是选中项", p.state==sel and p.current_face_key==P.STATE_FACE.get(sel))

# 3. 非idle常驻表情(模拟自动轮换到bliss)也不被逐帧重载
face_calls.clear()
p.auto_state="bliss"; p.state="bliss"; p.state_end=0
orig_face(p,"bliss")
face_calls.clear()
for _ in range(60):
    p.tick()
check("自动轮换的非idle表情(bliss)不卡帧", len(face_calls)==0 and p.current_face_key=="bliss",
      f"face调用={len(face_calls)} key={p.current_face_key}")

# 4. 连点200次绝不出现away，且能产生多种表情
seen=set()
for i in range(200):
    p._click_token += 1
    p._do_single_click(p._click_token)
    seen.add(p.auto_state)
check("连点200次不出现away", "away" not in seen)
check("连点能覆盖>=20种表情", len(seen)>=20, f"{len(seen)}种")

# 5. 双击喂食是临时反应，结束后回到选中表情
p.auto_state="sleep"; p.state="sleep"; p.state_end=0
orig_face(p,"sleep")
p.act("feed")
feed_face = p.current_face_key
check("喂食中显示进食类表情", feed_face in ("eat","salad","drink"), feed_face)
check("喂食中state是临时的(≠auto)", p.state!=p.auto_state)
p.state_end = time.time()*1000 - 1
p.tick()
check("喂食结束回到选中(sleep)", p.state=="sleep" and p.current_face_key=="sleep",
      f"{p.state}/{p.current_face_key}")

# 6. 拖拽结束回到选中
p.auto_state="cool"; p.state="cool"; p.state_end=0
orig_face(p,"cool")
class FakeBtn:
    def button(self): return Qt.LeftButton
p._drag_pos=QPoint(10,10); p._moved=True
p.mouseReleaseEvent(FakeBtn())
check("拖拽结束回到选中(cool)", p.state=="cool" and p.current_face_key=="cool",
      f"{p.state}/{p.current_face_key}")

# 7. 点击会重置自动计时，不会立刻被轮换；到时后自动轮换仍生效
p._click_token += 1; p._do_single_click(p._click_token)
auto_calls.clear()
p.tick()
check("点击后短时间内不触发自动轮换", len(auto_calls)==0, str(len(auto_calls)))
p.fullness=80; p.mood=80
p.last_auto_time = time.time()-100000
p.tick()
check("到时间后自动轮换仍会触发", len(auto_calls)>=1, str(len(auto_calls)))

print(f"\n===== 点击切换测试：{sum(res)}/{len(res)} 通过 =====")
sys.exit(0 if all(res) else 1)

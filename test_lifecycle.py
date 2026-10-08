# -*- coding: utf-8 -*-
"""批次B：单实例锁机制 + 关闭宠物的生命周期回收（offscreen）"""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
sys.path.insert(0, r"C:\ps6"); sys.path.insert(0, r"C:\plibs")

import pet as P
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSharedMemory

app = QApplication([])
results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")

# ---- 1. 单实例检测机制（与 __main__ 中相同的用法，用独立测试键）----
KEY = "MejiPet_TEST_SINGLETON"
pre = QSharedMemory(KEY)
while pre.attach():          # 清理上次失败可能残留的段
    pre.detach()

a = QSharedMemory(KEY)
check("启动前无实例(attach失败)", not a.attach())
check("首个实例 create 成功", a.create(1))
b = QSharedMemory(KEY)
check("第二个实例能检测到已存在(attach成功)", b.attach())
b.detach()
a.detach()                    # 首实例退出，释放
c = QSharedMemory(KEY)
check("首实例退出后段已释放", not c.attach())

# 结构检查：主程序确实在 __main__ 中使用了单实例键
src = open("pet.py", encoding="utf-8").read()
check("pet.py 含单实例锁代码", "MejiPet_Singleton_v1" in src and "QSharedMemory" in src)

# ---- 2. close_pet 生命周期回收 ----
P.Pet.manager = None
p = P.Pet()
p.close_pet()
check("close_pet 后 _alive=False", not p._alive)
check("主 tick/decay 定时器已停止", not p.timer.isActive() and not p.decay_timer.isActive())
# 挂起的回调在关闭后被调用也不应抛异常
try:
    p._do_single_click(p._click_token)
    p.start_walk("x")
    cb_ok = True
except Exception as e:
    cb_ok = False; print("  回调异常", e)
check("关闭后挂起回调安全不报错", cb_ok)

# ---- 3. 有关爱粒子时关闭，粒子被一并清理 ----
q = P.Pet()
q.spawn_hearts(3)
app.processEvents()
npart = len(q.particles)
q.close_pet()
check("带粒子关闭：粒子列表已清空", npart == 3 and len(q.particles) == 0, f"{npart}->0")

passed = sum(results); total = len(results)
print(f"\n===== 生命周期测试：{passed}/{total} 通过 =====")
sys.exit(0 if passed == total else 1)

# -*- coding: utf-8 -*-
"""确定性验证托盘"退出"链路不卡死：
复刻 pystray 菜单"退出"的真实动作(向 cmd_queue 投 __quit__)，
由 Qt 主线程 100ms 轮询 -> PetManager.quit_all() -> os._exit(0)。
生成5只宠物压测。父进程用超时判断是否干净退出。
"""
import sys, os
sys.path.insert(0, r"C:\ps6"); sys.path.insert(0, r"C:\plibs")
os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import pet

app = QApplication(sys.argv)
mgr = pet.PetManager()
pet.Pet.manager = mgr
for _ in range(5):
    mgr.spawn()
mgr.setup_tray()  # 真实创建 pystray 托盘图标与轮询

def fire_quit():
    # 与 pystray do_quit 完全一致
    mgr.cmd_queue.put("__quit__")
    print("HARNESS: __quit__ enqueued", flush=True)

QTimer.singleShot(2500, fire_quit)
# 看门狗：若 8 秒后仍活着，说明退出卡死，返回码 2
def watchdog():
    print("HARNESS: WATCHDOG TRIGGERED - quit hung!", flush=True)
    os._exit(2)
QTimer.singleShot(8000, watchdog)
sys.exit(app.exec())

# -*- coding: utf-8 -*-
"""批次C：配置原子写/损坏备份 + 本地日志（offscreen），结束后还原用户真实配置。"""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
sys.path.insert(0, r"C:\ps6"); sys.path.insert(0, r"C:\plibs")

import pet as P
from PySide6.QtWidgets import QApplication
app = QApplication([])

CFG = P.CFG_PATH
results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")

# 备份用户真实配置
orig_existed = os.path.exists(CFG)
orig_bytes = open(CFG, "rb").read() if orig_existed else None

def restore():
    for extra in (CFG + ".tmp", CFG + ".corrupt"):
        try:
            if os.path.exists(extra): os.remove(extra)
        except Exception: pass
    if orig_existed:
        tmp = CFG + ".restore.tmp"
        with open(tmp, "wb") as f: f.write(orig_bytes)
        os.replace(tmp, CFG)
    else:
        for p in (CFG,):
            if os.path.exists(p): os.remove(p)

try:
    # 1. 保存/读取往返
    P.save_cfg({"size": 100, "activity": 80})
    got = P.load_cfg()
    check("保存后读取一致", got == {**P.DEFAULTS, "size": 100, "activity": 80}, str(got))
    # 2. 原子写不留临时文件
    check("原子写后无 .tmp 残留", not os.path.exists(CFG + ".tmp"))
    # 3. 损坏配置：回退默认并备份
    with open(CFG, "w", encoding="utf-8") as f: f.write("{这不是合法json")
    got2 = P.load_cfg()
    check("损坏配置回退默认", got2 == dict(P.DEFAULTS), str(got2))
    check("损坏文件已备份为 .corrupt", os.path.exists(CFG + ".corrupt") and
          open(CFG + ".corrupt", encoding="utf-8").read().startswith("{"))
    # 4. 日志文件可写
    P.log.info("配置测试标记XYZ")
    for h in P.log.handlers: h.flush()
    logf = os.path.join(os.path.expanduser("~"), ".meji_pet.log")
    check("日志文件存在且含测试内容",
          os.path.exists(logf) and "配置测试标记XYZ" in open(logf, encoding="utf-8").read())
finally:
    restore()

# 5. 还原后配置回到用户原值
final = P.load_cfg()
check("测试后用户配置已还原", orig_bytes is None or final == {**P.DEFAULTS, **__import__("json").loads(orig_bytes.decode())},
      str(final))

passed = sum(results); total = len(results)
print(f"\n===== 配置/日志测试：{passed}/{total} 通过 =====")
sys.exit(0 if passed == total else 1)

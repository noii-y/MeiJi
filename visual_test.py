# -*- coding: utf-8 -*-
"""通道二+三：真实GUI进程内可视化/功能测试台（非offscreen，窗口真实显示）。
用 PrintWindow 抓自身窗口帧验证渲染；真实驱动状态机与菜单动作。"""
import os, sys, time, ctypes, random
from ctypes import wintypes
os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
sys.path.insert(0, r"C:\ps6"); sys.path.insert(0, r"C:\plibs")
import pet as P
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint

os.makedirs("vtest", exist_ok=True)
user32=ctypes.windll.user32; gdi32=ctypes.windll.gdi32
class BIH(ctypes.Structure):
    _fields_=[("biSize",wintypes.DWORD),("biWidth",wintypes.LONG),("biHeight",wintypes.LONG),
              ("biPlanes",wintypes.WORD),("biBitCount",wintypes.WORD),("biCompression",wintypes.DWORD),
              ("biSizeImage",wintypes.DWORD),("biXPels",wintypes.LONG),("biYPels",wintypes.LONG),
              ("biClrUsed",wintypes.DWORD),("biClrImportant",wintypes.DWORD)]
def grab(widget, name):
    hwnd=int(widget.winId()); r=wintypes.RECT(); user32.GetWindowRect(hwnd,ctypes.byref(r))
    w=r.right-r.left; h=r.bottom-r.top
    hdc=user32.GetDC(0); mem=gdi32.CreateCompatibleDC(hdc)
    hbmp=gdi32.CreateCompatibleBitmap(hdc,w,h); gdi32.SelectObject(mem,hbmp)
    user32.PrintWindow(hwnd,mem,3)
    bi=BIH(); bi.biSize=ctypes.sizeof(bi); bi.biWidth=w; bi.biHeight=-h; bi.biPlanes=1; bi.biBitCount=32
    buf=ctypes.create_string_buffer(w*h*4)
    gdi32.GetDIBits(mem,hbmp,0,h,buf,ctypes.byref(bi),0)
    from PIL import Image
    img=Image.frombuffer("RGBA",(w,h),buf,"raw","BGRA",0,1)
    img.save(f"vtest/{name}.png")
    gdi32.DeleteObject(hbmp); gdi32.DeleteDC(mem); user32.ReleaseDC(0,hdc)
    # 非透明(非黑)bbox
    px=img.load(); pts=[]
    for y in range(h):
        for x in range(w):
            rr,gg,bb,aa=px[x,y]
            if rr+gg+bb>60: pts.append((x,y))
    if not pts: return img,(0,0,0,0),0
    xs=[a for a,b in pts]; ys=[b for a,b in pts]
    return img,(min(xs),min(ys),max(xs),max(ys)),len(pts)

def pump(dur):
    end=time.time()+dur
    while time.time()<end:
        app.processEvents(); time.sleep(0.02)

R=[]
def check(name,ok,detail=""):
    R.append(ok); print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")

app=QApplication(sys.argv)
mgr=P.PetManager(); P.Pet.manager=mgr
p=mgr.spawn(); pump(1.2)

# DPR
dpr=app.devicePixelRatio()
print("devicePixelRatio=",dpr)

# ---- 四尺寸渲染：测量非透明bbox，应随尺寸增大 ----
bboxes={}
for s in [50,60,100,150]:
    p.set_size(s); pump(0.6)
    img,bb,n=grab(p,f"size_{s}")
    bw=bb[2]-bb[0]; bh=bb[3]-bb[1]
    bboxes[s]=(bw,bh,n)
    print(f"  size {s}: 物理bbox={bw}x{bh} 非黑像素={n}")
mono = bboxes[50][2]<bboxes[100][2]<bboxes[150][2]
check("四尺寸渲染像素随档位严格增大", mono, str({k:v[2] for k,v in bboxes.items()}))
# 小尺寸不应被裁切：非黑像素应明显>0且bbox边长合理(约 size*dpr)
ok50 = bboxes[50][2] > 1500 and bboxes[50][0]>0 and bboxes[50][1]>0
check("小尺寸50有完整内容(非只露眼角)", ok50, f"50档像素={bboxes[50][2]} bbox={bboxes[50][:2]}")

# ---- 单击切换常驻表情 ----
p.set_size(60); pump(0.4)
p._click_token+=1; tok=p._click_token
p._do_single_click(tok); pump(0.3)
img,bb,n=grab(p,"click")
clicked_face=p.current_face_key
check("单击切换到可循环表情(非away)", p.current_face_key in set(P.CLICK_POOL), p.current_face_key)
check("单击表情即常驻(state==auto_state)", p.state==p.auto_state==clicked_face,
      f"state={p.state} auto={p.auto_state}")
# 旧版1.5s就回弹；现在必须持续显示不回弹
pump(2.5)
check("单击表情持续2.5s以上不回弹", p.current_face_key==clicked_face and p.state==p.auto_state,
      f"state={p.state} face={p.current_face_key}")

# ---- 双击喂食，并验证取消挂起单击 ----
before_tok=p._click_token
class B:
    def button(self): return Qt.LeftButton
p.mouseReleaseEvent(B()); pump(0.05)   # 挂起一个单击
p.mouseDoubleClickEvent(B()); pump(0.4)  # 双击应取消它并喂食
feed_faces={"eat","salad","drink"}
img,bb,n=grab(p,"dblclick")
check("双击喂食表情", p.current_face_key in feed_faces, p.current_face_key)
check("双击取消了挂起单击(token递增)", p._click_token==before_tok+2, f"{before_tok}->{p._click_token}")
pump(2.8)
check("喂食结束回归", p.state==p.auto_state, p.state)

# ---- 拖拽表情 ----
p.face("drag"); pump(0.3)
img,bb,n=grab(p,"drag")
check("拖拽中显fume", p.current_face_key=="fume", p.current_face_key)

# ---- 菜单动作直接触发 ----
p._size_actions[100].trigger(); pump(0.4)
check("菜单选100→cfg=100且已重载", p.cfg["size"]==100 and p.movie_sizes["idle"].width() in (100,), str(p.movie_sizes["idle"].width()))
p._act_actions[80].trigger(); pump(0.2)
check("菜单活跃度80→cfg=80", p.cfg["activity"]==80, str(p.cfg["activity"]))
p._refresh_menu_checks(); pump(0.1)
check("菜单勾选标记正确", p._size_actions[100].isChecked() and p._act_actions[80].isChecked()
      and not p._size_actions[50].isChecked())
# 逗它子菜单：开心
for a in p.menu.actions():
    pass
# 找到逗它子菜单并触发第一项(开心)
face_sub=None
for a in p.menu.actions():
    if a.menu() and a.text().startswith("🎭"): face_sub=a.menu()
f0=face_sub.actions()[0]; f0.trigger(); pump(0.4)
check("逗它→开心 生效", p.current_face_key=="happy", p.current_face_key)
# 召唤
n0=len(mgr.pets)
for a in p.menu.actions():
    if a.text().startswith("🐣"): a.trigger()
pump(0.8)
check("菜单召唤一只→+1", len(mgr.pets)==n0+1, f"{n0}->{len(mgr.pets)}")

# ---- 走开再回来 ----
p.set_size(60)
p2=mgr.pets[0]
p2._away_mode=False; p2.walk_target=None; pump(0.2)
x0=p2.px
p2.start_away(); pump(0.3)
check("start_away: away模式+away脸+目标屏外", p2._away_mode and p2.current_face_key=="away" and p2.walk_target[0]>=p2.screen_w,
      f"face={p2.current_face_key} tx={p2.walk_target[0]:.0f}")
# 泵到走出屏幕并hide
hid=False
for i in range(120):
    pump(0.2)
    if not p2.isVisible(): hid=True; break
check("走开：走到屏外后hide", hid, f"px={p2.px:.0f} vis={p2.isVisible()}")
# 等回来(4s hide + 走回)
cameback=False
for i in range(120):
    pump(0.2)
    if p2.isVisible() and not p2._away_mode and p2.walk_target is None and p2.state==p2.auto_state:
        cameback=True; break
check("走开后自动回来并恢复自动状态", cameback, f"vis={p2.isVisible()} away={p2._away_mode} state={p2.state} px={p2.px:.0f}")

# ---- 自动轮换多样性（缩短间隔；临时屏蔽走开，专注测轮换）----
P.AUTO_INTERVAL=2
p2.cfg["activity"]=10
p2.last_auto_time=time.time()
p2.start_away=lambda *a,**k: None   # 屏蔽走开，避免占用观察窗
seen=set()
for i in range(140):
    pump(0.2)
    seen.add(p2.auto_state)
check("缩短间隔后自动轮换出>=6种表情", len(seen)>=6, f"{len(seen)}种 {sorted(seen)}")
P.AUTO_INTERVAL=600

passed=sum(R); total=len(R)
print(f"\n===== 真实GUI测试：{passed}/{total} 通过 =====")
app.quit()
sys.exit(0 if passed==total else 1)

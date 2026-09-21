# -*- coding: utf-8 -*-
"""真机EXE点击切换验收：启动EXE->抓idle->物理点击->连续抓帧验证换脸/在动/不回弹。"""
import os, sys, time, ctypes, subprocess, csv, io
from ctypes import wintypes
os.chdir(r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet")
os.makedirs("_analysis/exe_click", exist_ok=True)

# DPI 感知，坐标与Qt物理像素一致
try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception: pass
u=ctypes.windll.user32; g=ctypes.windll.gdi32; k=ctypes.windll.kernel32

from PIL import Image

EXE=os.path.abspath(r"dist\MejiPet.exe")
proc=subprocess.Popen([EXE])
print("launched, 等待onefile解压与窗口出现...")

def pet_hwnds():
    out=subprocess.run(['tasklist','/fo','csv','/fi','imagename eq MejiPet.exe'],
                       capture_output=True,text=True).stdout
    pids=set()
    for row in csv.reader(io.StringIO(out)):
        if len(row)>1 and row[0].strip('"').lower()=="mejipet.exe":
            pids.add(int(row[1]))
    res=[]
    WNDENUMPROC=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
    def cb(hwnd,l):
        p=wintypes.DWORD(); u.GetWindowThreadProcessId(hwnd,ctypes.byref(p))
        if p.value in pids and u.IsWindowVisible(hwnd):
            r=wintypes.RECT(); u.GetWindowRect(hwnd,ctypes.byref(r))
            cls=ctypes.create_unicode_buffer(256); u.GetClassNameW(hwnd,cls,256)
            if "QWindowToolSaveBits" in cls.value:
                res.append((hwnd,r))
        return True
    u.EnumWindows(WNDENUMPROC(cb),0)
    return res

hwnd=None
for _ in range(40):
    ws=pet_hwnds()
    if ws:
        hwnd=ws[0][0]; break
    time.sleep(1)
if not hwnd:
    print("未找到美叽窗口");
    subprocess.run(['taskkill','/IM','MejiPet.exe','/F'],capture_output=True); sys.exit(2)
r=ws[0][1]
print("pet window rect:",r.left,r.top,r.right-r.left,r.bottom-r.top, "窗口数",len(ws))

def grab(hwnd):
    r=wintypes.RECT(); u.GetWindowRect(hwnd,ctypes.byref(r))
    w=r.right-r.left; h=r.bottom-r.top
    hdc=u.GetDC(0); mem=g.CreateCompatibleDC(hdc)
    hbmp=g.CreateCompatibleBitmap(hdc,w,h); g.SelectObject(mem,hbmp)
    u.PrintWindow(hwnd,mem,3)
    class BIH(ctypes.Structure):
        _fields_=[("biSize",wintypes.DWORD),("biWidth",wintypes.LONG),("biHeight",wintypes.LONG),
                  ("biPlanes",wintypes.WORD),("biBitCount",wintypes.WORD),("biCompression",wintypes.DWORD),
                  ("biSizeImage",wintypes.DWORD),("biXPels",wintypes.LONG),("biYPels",wintypes.LONG),
                  ("biClrUsed",wintypes.DWORD),("biClrImportant",wintypes.DWORD)]
    bi=BIH(); bi.biSize=ctypes.sizeof(bi); bi.biWidth=w; bi.biHeight=-h; bi.biPlanes=1; bi.biBitCount=32
    buf=ctypes.create_string_buffer(w*h*4)
    g.GetDIBits(mem,hbmp,0,h,buf,ctypes.byref(bi),0)
    img=Image.frombuffer("RGBA",(w,h),buf,"raw","BGRA",0,1)
    g.DeleteObject(hbmp); g.DeleteDC(mem); u.ReleaseDC(0,hdc)
    return img

def body(img):
    """返回非透明(非黑)像素：bbox、数量、16x16占用网格、bbox裁片"""
    px=img.load(); W,H=img.size; pts=[]
    for y in range(H):
        for x in range(W):
            rr,gg,bb,aa=px[x,y]
            if rr+gg+bb>60: pts.append((x,y))
    if not pts: return (0,0,0,0),0,None,None
    xs=[a for a,b in pts]; ys=[b for a,b in pts]
    bb=(min(xs),min(ys),max(xs),max(ys))
    grid=set()
    for x,y in pts: grid.add((int(x/W*16),int(y/H*16)))
    crop=img.crop(bb)
    return bb,len(pts),grid,crop

def grid_diff(a,b):
    if a is None or b is None: return 999
    return len(a^b)

def click_center(hwnd):
    r=wintypes.RECT(); u.GetWindowRect(hwnd,ctypes.byref(r))
    cx=(r.left+r.right)//2; cy=(r.top+r.bottom)//2
    u.SetCursorPos(cx,cy); time.sleep(0.15)
    u.mouse_event(0x0002,0,0,0,0); time.sleep(0.05); u.mouse_event(0x0004,0,0,0,0)

def montage(crops, path, cols=None, bg=(255,255,255)):
    crops=[c for c in crops if c is not None]
    if not crops: return
    ch=max(c.height for c in crops); cw=max(c.width for c in crops)
    cols=cols or len(crops)
    rows=(len(crops)+cols-1)//cols
    canvas=Image.new("RGBA",(cols*cw,rows*ch),(0,0,0,0))
    for i,c in enumerate(crops):
        x=(i%cols)*cw+(cw-c.width)//2; y=(i//cols)*ch+(ch-c.height)//2
        canvas.alpha_composite(c.convert("RGBA"),(x,y))
    # 放到白底上便于肉眼看
    bgim=Image.new("RGBA",canvas.size,bg+(255,)); bgim.alpha_composite(canvas)
    bgim.save(path)

try:
    idle=grab(hwnd); ibb,inum,igrid,icrop=body(idle)
    montage([icrop],"_analysis/exe_click/idle_ref.png")
    print(f"[idle] bbox={ibb} pixels={inum} grid={len(igrid)}")

    summary=[]
    for ci in range(4):
        click_center(hwnd)
        time.sleep(0.8)  # 越过doubleClickInterval，单击已生效
        crops=[]; grids=[]; bbs=[]
        for fi in range(6):
            im=grab(hwnd); bb,n,gr,cr=body(im)
            crops.append(cr); grids.append(gr); bbs.append(bb)
            time.sleep(0.3)
        # 帧间最大差异（动画在动=>明显>0；卡死第一帧=>0）
        motion=max(grid_diff(grids[i],grids[i+1]) for i in range(len(grids)-1))
        changed=grid_diff(grids[2],igrid)  # 相对idle
        montage(crops,f"_analysis/exe_click/click{ci+1}_burst.png")
        # 4.x秒后再抓一帧，看是否回弹idle
        time.sleep(2.2)
        late=grab(hwnd); lbb,ln,lgr,lcrop=body(late)
        montage(crops+[lcrop],f"_analysis/exe_click/click{ci+1}_withlate.png")
        bounce=grid_diff(lgr,grids[-1])  # late与点击表情末帧差异
        to_idle=grid_diff(lgr,igrid)
        summary.append((ci+1,changed,motion,bounce,to_idle,bbs[-1],lbb))
        print(f"[click{ci+1}] vs_idle网格差={changed} 帧间最大动={motion} "
              f"late与本脸差={bounce} late与idle差={to_idle} bbox末={bbs[-1]} late={lbb}")
        igrid=grids[-1]  # 下一次点击以当前脸为基准

    print("\n判定：")
    print(" - vs_idle网格差应>0(点击换了脸)；帧间最大动应>0(GIF在动,非卡第一帧)")
    print(" - late与本脸差应较小、late与idle差应较大(4秒后仍停留点击表情,未回弹)")
finally:
    subprocess.run(['taskkill','/IM','MejiPet.exe','/F'],capture_output=True)

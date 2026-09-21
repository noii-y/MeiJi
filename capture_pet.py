# -*- coding: utf-8 -*-
"""抓桌宠窗口帧（PrintWindow，分层窗口专用）。
用法:
  capture_pet.py <进程名> [帧数] [帧间隔秒] [输出前缀]
打印每帧非透明像素bbox、与首帧差异像素数，证明动画；存png。
"""
import ctypes, sys, csv, io, subprocess, time
from ctypes import wintypes
from PIL import Image

user32 = ctypes.windll.user32; gdi32 = ctypes.windll.gdi32
target = sys.argv[1] if len(sys.argv)>1 else "MejiPet.exe"
N = int(sys.argv[2]) if len(sys.argv)>2 else 1
gap = float(sys.argv[3]) if len(sys.argv)>3 else 0.4
prefix = sys.argv[4] if len(sys.argv)>4 else "frame"

def pet_hwnds():
    out = subprocess.run(['tasklist','/fo','csv','/fi',f'imagename eq {target}'],
                         capture_output=True, text=True).stdout
    pids=set()
    for row in csv.reader(io.StringIO(out)):
        if len(row)>1 and row[0].strip('"').lower()==target.lower():
            pids.add(int(row[1]))
    res=[]
    WNDENUMPROC=ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, lp):
        pid=wintypes.DWORD(); user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids and user32.IsWindowVisible(hwnd):
            r=wintypes.RECT(); user32.GetWindowRect(hwnd, ctypes.byref(r))
            cls=ctypes.create_unicode_buffer(256); user32.GetClassNameW(hwnd,cls,256)
            if "QWindowToolSaveBits" in cls.value:  # 美叽主窗口
                res.append((hwnd,(r.left,r.top,r.right,r.bottom)))
        return True
    user32.EnumWindows(WNDENUMPROC(cb),0)
    return res

class BIH(ctypes.Structure):
    _fields_=[("biSize",wintypes.DWORD),("biWidth",wintypes.LONG),("biHeight",wintypes.LONG),
              ("biPlanes",wintypes.WORD),("biBitCount",wintypes.WORD),("biCompression",wintypes.DWORD),
              ("biSizeImage",wintypes.DWORD),("biXPels",wintypes.LONG),("biYPels",wintypes.LONG),
              ("biClrUsed",wintypes.DWORD),("biClrImportant",wintypes.DWORD)]

def grab(hwnd, rect):
    l,t,r,b=rect; w=r-l; h=b-t
    hdc=user32.GetDC(0); mem=gdi32.CreateCompatibleDC(hdc)
    hbmp=gdi32.CreateCompatibleBitmap(hdc,w,h); gdi32.SelectObject(mem,hbmp)
    user32.PrintWindow(hwnd,mem,3)
    bi=BIH(); bi.biSize=ctypes.sizeof(bi); bi.biWidth=w; bi.biHeight=-h
    bi.biPlanes=1; bi.biBitCount=32
    buf=ctypes.create_string_buffer(w*h*4)
    gdi32.GetDIBits(mem,hbmp,0,h,buf,ctypes.byref(bi),0)
    img=Image.frombuffer("RGBA",(w,h),buf,"raw","BGRA",0,1)
    gdi32.DeleteObject(hbmp); gdi32.DeleteDC(mem); user32.ReleaseDC(0,hdc)
    return img

def nonblack_mask(img):
    px=img.load(); w,h=img.size
    pts=[]
    for y in range(h):
        for x in range(w):
            rr,gg,bb,aa=px[x,y]
            # 透明区PrintWindow呈黑；非黑即美叽
            if rr+gg+bb > 60:
                pts.append((x,y))
    return pts

wins=pet_hwnds()
print(f"{target} 窗口数: {len(wins)}")
if not wins: sys.exit(2)
base=None
for i in range(N):
    for wi,(hwnd,rect) in enumerate(wins):
        img=grab(hwnd,rect)
        pts=nonblack_mask(img)
        if pts:
            xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
            bbox=(min(xs),min(ys),max(xs),max(ys))
        else:
            bbox=None
        fn=f"{prefix}_{i}_w{wi}.png"; img.save(fn)
        diff=""
        if base is not None and wi==0:
            bpx=base.load(); px=img.load(); d=0
            for y in range(0,img.size[1],2):
                for x in range(0,img.size[0],2):
                    if bpx[x,y][:3]!=px[x,y][:3]: d+=1
            diff=f" 与首帧采样差异={d}"
        if wi==0 and i==0: base=img
        print(f"帧{i} 窗{wi} rect={rect} 非透明像素={len(pts)} bbox={bbox}{diff} -> {fn}")
    if i<N-1: time.sleep(gap)

# -*- coding: utf-8 -*-
"""B方案批次G：眨眼合成器。
叠在 idle 真实54帧微动动画上（爪子/身体/耳朵会动），
只在每个5.4秒循环里、动作峰值的2帧闭眼（各100ms）。
默认输出 _rig_out 供预览；加 --install 同时写入 assets 四尺寸与根母版。
"""
import os, sys
from collections import deque
from PIL import Image, ImageDraw
import regen2 as R

os.makedirs("_rig_out", exist_ok=True)
frames, durs = R.cutout_flood(r"assets/meji_idle.gif")
frames = [f.copy() for f in frames]
frames = R.stabilize(frames)
frames = R.crop_union(frames)
H, W = frames[0].height, frames[0].width
BLACK = (15, 15, 15, 255)

def dark(p):
    r, g, b, a = p
    return a > 180 and r < 90 and g < 90 and b < 90

def components_of(pts):
    s = set(pts); out = []
    while s:
        seed = s.pop(); q = deque([seed]); comp = [seed]
        while q:
            x, y = q.popleft()
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if (nx,ny) in s:
                    s.remove((nx,ny)); q.append((nx,ny)); comp.append((nx,ny))
        xs=[p[0] for p in comp]; ys=[p[1] for p in comp]
        out.append(((min(xs),min(ys),max(xs),max(ys)), comp))
    return out

def find_eyes(im):
    w, h = im.size; px = im.load()
    ab = im.getbbox(); l,t,r,b = ab
    pts=[(x,y) for y in range(t,int(t+(b-t)*0.55)) for x in range(l+6,r-6) if dark(px[x,y])]
    eyes=[]
    for bb,comp in components_of(pts):
        bw=bb[2]-bb[0]; bh=bb[3]-bb[1]
        if 120<=len(comp)<=400 and 15<=bw<=28 and 15<=bh<=28:
            eyes.append((bb,comp))
    eyes.sort(key=lambda e:e[0][0])
    return eyes[:2]

def tex_src(px, w, h, x, y):
    """从下方复制真实脸纹（含网点），保留纹理。"""
    for cand in ((x,y+26),(x,y+30),(x,y-26),(x-8,y+26),(x+8,y+26)):
        cx,cy=cand
        if 0<=cx<w and 0<=cy<h:
            p=px[cx,cy]
            if p[3]>200 and not dark(p):
                return p[:3]
    return (252,252,255)

def close_frame(im, eyes):
    f=im.copy(); px=f.load(); w,h=f.size
    for bb,comp in eyes:
        x0,y0,x1,y1=bb
        rows={}
        for x,y in comp:
            rows.setdefault(y,[x,x]); rows[y][0]=min(rows[y][0],x); rows[y][1]=max(rows[y][1],x)
        for y in range(max(0,y0-1),min(h,y1+2)):
            xa,xb=rows.get(y,(None,None))
            if xa is None: continue
            for x in range(xa-1,xb+2):
                if 0<=x<w:
                    r,g,b=tex_src(px,w,h,x,y)
                    px[x,y]=(r,g,b,255)
        # 外圈残留灰像素
        for y in range(max(0,y0-2),min(h,y1+1)):
            for x in range(max(0,x0-2),min(w,x1+3)):
                r,g,b,a=px[x,y]
                if a>200 and r<195 and g<195 and b<195:
                    if y<33 and x>71: continue
                    if y>=44 and 83<=x<=93: continue
                    rr,gg,bb=tex_src(px,w,h,x,y)
                    px[x,y]=(rr,gg,bb,255)
        cx=(x0+x1)//2; cy=y0+int((y1-y0)*0.58)
        rx=(x1-x0)//2-2; ry=4
        dd=ImageDraw.Draw(f)
        dd.arc([cx-rx,cy-ry,cx+rx,cy+ry],start=12,end=168,fill=BLACK,width=3)
    return f

# 每帧找眼（失败则用帧0偏移兜底）
eye_cache={}
for k,f in enumerate(frames):
    e=find_eyes(f)
    if len(e)==2:
        eye_cache[k]=e
print("成功定位眼睛的帧:", len(eye_cache), "/", len(frames))

# 构造时间线：6个正常循环 + 1个特殊循环（pos5,6 闭眼）+ 2帧缓冲
# 闭眼帧强制 100ms，其余沿用原片时长
CYCLE=9
def build_timeline():
    seq=[]
    for k in range(54):  # 6个正常循环
        seq.append((frames[k].copy(), durs[k] if k<len(durs) else 100))
    for k in range(9):    # 特殊循环
        srcf=frames[k]
        if k in (5,6):
            e=eye_cache.get(k)
            f=close_frame(srcf,e) if e else srcf.copy()
            seq.append((f,100))
        else:
            seq.append((srcf.copy(), durs[k] if k<len(durs) else 100))
    # 缓冲：循环起点，避免闭眼帧直接跳到开头
    seq.append((frames[0].copy(), durs[0] if durs else 100))
    seq.append((frames[1].copy(), durs[1] if len(durs)>1 else 100))
    return seq

seq=build_timeline()
out=[x[0] for x in seq]; out_durs=[x[1] for x in seq]
print("时间线帧数", len(out))

for sz in R.SIZES:
    w0,h0=out[0].size
    ratio=sz/max(w0,h0)
    nw=max(1,round(w0*ratio)); nh=max(1,round(h0*ratio))
    rfs=[R.resample(f,nw,nh) for f in out]
    R.save_gif(rfs,out_durs,f"_rig_out/meji_blink_t_{sz}.gif")
    if "--install" in sys.argv:
        d=os.path.join("assets",str(sz)); os.makedirs(d,exist_ok=True)
        R.save_gif(rfs,out_durs,os.path.join(d,"meji_blink_t.gif"))
if "--install" in sys.argv:
    # 根目录母版（与四尺寸目录保持一致，计数用）
    import shutil
    shutil.copyfile(os.path.join("assets","150","meji_blink_t.gif"),
                    os.path.join("assets","meji_blink_t.gif"))
print("gifs done")

# 对比联系图：特殊循环 57-62（闭眼帧 59,60）
S=4; w,h=out[0].size; pad=8
sel=[(57,"57 normal"),(58,"58 normal"),(59,"59 CLOSED"),(60,"60 CLOSED"),(61,"61 normal"),(62,"62 normal")]
sheet=Image.new("RGB",(len(sel)*(w*S+pad)+pad,h*S+2*pad+16),(235,235,235))
d=ImageDraw.Draw(sheet)
for i,(k,name) in enumerate(sel):
    im=out[k]
    big=im.resize((w*S,h*S),Image.NEAREST)
    bg=Image.new("RGB",(w*S,h*S),(255,255,255))
    dd=ImageDraw.Draw(bg)
    for yy in range(0,h*S,12):
        for xx in range(0,w*S,12):
            if (xx//12+yy//12)%2==0: dd.rectangle([xx,yy,xx+11,yy+11],fill=(214,214,214))
    bg.paste(big,(0,0),big)
    x=pad+i*(w*S+pad)
    sheet.paste(bg,(x,pad+12))
    d.text((x+2,2),name,fill=(200,0,0) if "CLOSED" in name else (0,0,0))
sheet.save("_rig_out/_blink_seq.png")
print("saved seq")

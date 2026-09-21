# -*- coding: utf-8 -*-
"""v2 从原始白底GIF重建四尺寸（统一画布，修复away/rain几何与道具丢失，消除黑边）。
流程：统一画布flood-fill去白(全片并集框统一裁切) -> idle逐帧稳像
     -> 最近不透明色BFS外扩(消黑边,不洗白道具) -> LANCZOS缩放 -> alpha二值化
     -> 共享255色调色板/关dither -> 写 assets_new/{size}
"""
import os, glob, shutil
from collections import deque
from PIL import Image, ImageSequence
Image.MAX_IMAGE_PIXELS=None

ROOT=r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet\assets"
OUT =r"C:\Users\28030\Doubao\chats\2026-09-19\new-chat\meji-pet\assets_new"
SIZES=[50,60,100,150]; TIDX=255; ALPHA_TH=110
KEYS=["idle","happy","hug","angry","sleep","eat","excited","smug","kiss","laugh",
"phone","fan","hug2","joy","drunk","cry","bliss","wronged","pout","think","shy",
"gift","flower","drink","rain","present","relax","fume","furious","lieflat","stomp",
"cheer","cool","surprised","sushi","salad","innocent","blowkiss","glare","away"]

def is_white(r,g,b): return r>=235 and g>=235 and b>=235

def cutout_flood(path):
    """读原始白底GIF，统一画布去白；返回全画布RGBA帧(不裁切)与时长。"""
    im=Image.open(path); W,H=im.size; frames=[]; durs=[]
    for fr in ImageSequence.Iterator(im):
        durs.append(fr.info.get('duration',100))
        rgba=fr.convert('RGBA'); px=rgba.load()
        seen=bytearray(W*H); q=deque()
        def seed(x,y):
            i=y*W+x
            if not seen[i] and is_white(*px[x,y][:3]): seen[i]=1;q.append(i)
        for x in range(W):
            seed(x,0); seed(x,H-1)
        for y in range(H):
            seed(0,y); seed(W-1,y)
        while q:
            i=q.popleft(); x=i%W; y=i//W
            r,g,b,a=px[x,y]; px[x,y]=(r,g,b,0)
            for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if 0<=nx<W and 0<=ny<H:
                    j=ny*W+nx
                    if not seen[j] and is_white(*px[nx,ny][:3]): seen[j]=1;q.append(j)
        frames.append(rgba)
    return frames,durs

def crop_union(frames):
    W,H=frames[0].size
    union=[W,H,0,0]; anypx=False
    for f in frames:
        b=f.getbbox()
        if b:
            anypx=True; union[0]=min(union[0],b[0]); union[1]=min(union[1],b[1])
            union[2]=max(union[2],b[2]); union[3]=max(union[3],b[3])
    if not anypx: return frames
    pad=3; l=max(0,union[0]-pad); t=max(0,union[1]-pad)
    r=min(W,union[2]+pad); b=min(H,union[3]+pad)
    return [f.crop((l,t,r,b)) for f in frames]

def crop_tight_centered(frames):
    """逐帧紧裁切，再居中(水平居中/底部对齐)放到统一最大画布，适合位置移动类(away)。"""
    crops=[]; boxes=[]
    for f in frames:
        b=f.getbbox()
        if b:
            c=f.crop(b); crops.append(c); boxes.append(b)
        else:
            crops.append(None); boxes.append(None)
    mw=max((c.width for c in crops if c is not None), default=1)
    mh=max((c.height for c in crops if c is not None), default=1)
    out=[]; last=None
    for c in crops:
        if c is None:
            c=last if last is not None else Image.new('RGBA',(mw,mh),(0,0,0,0))
        last=c
        cv=Image.new('RGBA',(mw,mh),(0,0,0,0))
        x=(mw-c.width)//2; y=mh-c.height  # 水平居中、底部对齐
        cv.paste(c,(x,y),c); out.append(cv)
    return out

def main_comp(fr):
    w,h=fr.size; px=fr.load(); m=bytearray(w*h)
    for y in range(h):
        for x in range(w):
            if px[x,y][3]>160:m[y*w+x]=1
    seen=bytearray(len(m));best=None;bn=0
    for i in range(len(m)):
        if m[i] and not seen[i]:
            q=deque([i]);seen[i]=1;c=[]
            while q:
                j=q.popleft();c.append(j);x=j%w;y=j//w
                for nx,ny in((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if 0<=nx<w and 0<=ny<h:
                        k=ny*w+nx
                        if m[k] and not seen[k]:seen[k]=1;q.append(k)
            if len(c)>bn:bn=len(c);best=c
    if not best:return None
    xs=[p%w for p in best];ys=[p//w for p in best]
    return (min(xs)+max(xs))/2,(min(ys)+max(ys))/2

def stabilize(frames):
    cs=[main_comp(f) for f in frames]; ok=[c for c in cs if c]
    tx=sorted(c[0] for c in ok)[len(ok)//2]; ty=sorted(c[1] for c in ok)[len(ok)//2]
    w,h=frames[0].size; cv=(w+8,h+8); out=[]
    for f,c in zip(frames,cs):
        dx=int(round(tx-c[0])) if c else 0; dy=int(round(ty-c[1])) if c else 0
        cnv=Image.new('RGBA',cv,(0,0,0,0)); cnv.paste(f,(4+dx,4+dy),f); out.append(cnv)
    return out

def collapse_empty(frames, durs):
    """合并全透明空帧到前一帧(时长累加)，规避Pillow对全空帧的GIF编码损坏；总时长不变。"""
    out_f=[]; out_d=[]; lead=0
    for f,d in zip(frames,durs):
        if f.getchannel('A').getbbox() is None:
            if out_f: out_d[-1]+=d
            else: lead+=d
        else:
            out_f.append(f); out_d.append(d+ (lead if not out_f else 0)); lead=0
    if not out_f:  # 全空极端情况，兜底
        out_f=[frames[0]]; out_d=[sum(durs)]
    return out_f,out_d

def bleed(fr):
    """最近不透明色BFS外扩到透明区，避免缩放引入黑色毛边。"""
    w,h=fr.size; px=fr.load()
    R=bytearray(w*h);G=bytearray(w*h);B=bytearray(w*h); filled=bytearray(w*h)
    q=deque()
    for y in range(h):
        for x in range(w):
            r,g,b,a=px[x,y]
            if a>200:
                i=y*w+x;R[i]=r;G[i]=g;B[i]=b;filled[i]=1;q.append(i)
    while q:
        i=q.popleft();x=i%w;y=i//w
        for nx,ny in((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0<=nx<w and 0<=ny<h:
                j=ny*w+nx
                if not filled[j]:
                    filled[j]=1;R[j]=R[i];G[j]=G[i];B[j]=B[i];q.append(j)
    out=Image.new('RGBA',(w,h)); op=out.load(); ap=fr.getchannel('A').load()
    for y in range(h):
        for x in range(w):
            i=y*w+x; op[x,y]=(R[i],G[i],B[i],ap[x,y])
    return out

def resample(fr,nw,nh):
    b=bleed(fr).resize((nw,nh),Image.LANCZOS)
    a=b.getchannel('A').point(lambda v:255 if v>=ALPHA_TH else 0)
    b.putalpha(a); return b

def save_gif(rfs,durs,dst):
    rgbs=[Image.alpha_composite(Image.new('RGBA',f.size,(255,255,255,255)),f).convert('RGB') for f in rfs]
    n=len(rgbs);step=max(1,n//8);sample=rgbs[::step][:8]
    strip=Image.new('RGB',(sample[0].width,sum(f.height for f in sample)));y=0
    for f in sample: strip.paste(f,(0,y));y+=f.height
    pal=strip.quantize(colors=255,method=Image.MEDIANCUT,dither=Image.Dither.NONE)
    pf=[]
    for f,rgb in zip(rfs,rgbs):
        p=rgb.quantize(palette=pal,dither=Image.Dither.NONE)
        amask=f.getchannel('A').point(lambda v:255 if v==0 else 0)
        p.paste(Image.new('P',f.size,TIDX),(0,0),amask)
        pl=p.getpalette();pl[TIDX*3:TIDX*3+3]=[0,0,0];p.putpalette(pl);pf.append(p)
    pf[0].save(dst,save_all=True,append_images=pf[1:],duration=durs,loop=0,
               disposal=2,transparency=TIDX,optimize=False)

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    for key in KEYS:
        src=os.path.join(ROOT,f"meji_{key}.gif"); name=f"meji_{key}_t.gif"
        if not os.path.exists(src): print("缺原片",key);continue
        try:
            frames,durs=cutout_flood(src)
            frames,durs=collapse_empty(frames,durs)
            frames=crop_union(frames)
            if key=='idle': frames=stabilize(frames)
            w0,h0=frames[0].size
            if key=='away':
                # 大特写穿过取景框：缩放基准用“身体最大尺寸”，保证本体与其它表情等大
                ref=0
                for f in frames:
                    b=f.getbbox()
                    if b: ref=max(ref,b[2]-b[0],b[3]-b[1])
                ref=ref or max(w0,h0)
            else:
                ref=max(w0,h0)
            for sz in SIZES:
                if key=='away':
                    # 身体尽量接近目标，但画布不超窗(≤min(200,目标*1.4))，避免被200窗口裁切
                    cap=min(200,int(sz*1.4))
                    ratio=min(sz/ref, cap/max(w0,h0))
                else:
                    ratio=sz/ref
                nw=max(1,int(round(w0*ratio)));nh=max(1,int(round(h0*ratio)))
                rfs=[resample(f,nw,nh) for f in frames]
                d=os.path.join(OUT,str(sz));os.makedirs(d,exist_ok=True)
                save_gif(rfs,durs,os.path.join(d,name))
            print("OK",name,frames[0].size,"帧",len(frames),"ref",int(ref))
        except Exception as e:
            import traceback;print("ERR",key,repr(e));traceback.print_exc()
    print("done")

if __name__=='__main__': main()

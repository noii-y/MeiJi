# -*- coding: utf-8 -*-
import os
import regen2 as r
key='away'; name=f"meji_{key}_t.gif"
src=os.path.join(r.ROOT,f"meji_{key}.gif")
frames,durs=r.cutout_flood(src)
frames,durs=r.collapse_empty(frames,durs)
frames=r.crop_union(frames)
w0,h0=frames[0].size
ref=0
for f in frames:
    b=f.getbbox()
    if b: ref=max(ref,b[2]-b[0],b[3]-b[1])
print("away 并集",(w0,h0),"ref",ref,"帧",len(frames))
for sz in r.SIZES:
    cap=min(200,int(sz*1.4))
    ratio=min(sz/ref, cap/max(w0,h0))
    nw=max(1,int(round(w0*ratio)));nh=max(1,int(round(h0*ratio)))
    rfs=[r.resample(f,nw,nh) for f in frames]
    d=os.path.join(r.OUT,str(sz));os.makedirs(d,exist_ok=True)
    r.save_gif(rfs,durs,os.path.join(d,name))
    print("saved",sz,(nw,nh),"cap",cap)

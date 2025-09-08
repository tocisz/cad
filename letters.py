#%% Imports
from math import sqrt
from build123d import *
from ocp_vscode import show
#%% a
cx = Location((0.5,0.5))
LW = 0.05 # line width
with BuildSketch() as ssb:
    with Locations(cx):
        SlotCenterToCenter(sqrt(2), 2*LW, 45)
show(ssb.sketch)
#%%
mirror_x_plane = Plane.XZ.move(cx)
mirror_xy_plane = Plane.XZ.move(Location(cx.position, 45))
with BuildSketch() as sab:
    add(ssb.sketch.mirror(mirror_x_plane))
show(sab.sketch)
#%%
lmw = RadiusArc((0, 0), (1, 1), 1)
with BuildSketch() as smb:
    with BuildLine():
        add(lmw)
        # RadiusArc((0, 0), (1, 1), 1)
    make_face()
    offset(amount=LW)
show(smb.sketch)
#%%
with BuildSketch() as sib:
    add(smb.sketch.mirror(mirror_x_plane))
show(sib.sketch)
#%%
with BuildSketch() as stb:
    add(smb.sketch.mirror(mirror_xy_plane))
show(stb.sketch)
#%%
with BuildSketch() as sob:
    add(stb.sketch.mirror(mirror_x_plane))
show(sob.sketch)
#%%
with BuildSketch() as skb:
    with BuildLine():
        TangentArc([(0,0), lmw @ 0.5], tangent=(1,0))
        TangentArc([lmw @ 0.5, (1,1)], tangent=(1,-1))
    make_face()
    offset(amount=LW)
show(skb.sketch)
#%%
with BuildSketch() as swb:
    add(skb.sketch.mirror(mirror_xy_plane))
show(swb.sketch)
#%%
with BuildSketch() as syb:
    add(skb.sketch.mirror(mirror_x_plane))
show(syb.sketch)
#%%
with BuildSketch() as spb:
    with BuildLine() as lpb:
        r = (cx.position - (lmw @ 0.5)).length
        add(Wire.make_circle(r).moved(cx))
    f = make_face()
    offset(amount=LW)
    with BuildSketch() as inside:
        add(f)
        offset(amount=-LW)
    add(inside.sketch, mode=Mode.SUBTRACT)
    add(smb.sketch)
show(spb.sketch)
#%%
with BuildSketch() as slb:
    add(spb.sketch.mirror(mirror_xy_plane))
show(slb.sketch)
#%%
with BuildSketch() as seb:
    add(spb.sketch.mirror(mirror_x_plane))
show(seb.sketch)
#%%
# Based on circle: center on horizontal line y = 0.5, coincident with cx, and M arc
with BuildSketch() as srb:
    with BuildLine():
        k1 = Vector(0.2, 0.6)
        k2 = Vector(0.8, 0.4)
        a1 = TangentArc([(0,0),k1], tangent=(0,1))
        a2 = TangentArc([a1@1, cx.position], tangent=a1%1)
        a3 = TangentArc([a2@1, k2], tangent=a2%1)
        TangentArc([a3@1, (1,1)], tangent=a3%1)
    make_face()
    offset(amount=LW)
show(srb.sketch)
# %%
with BuildSketch() as sub:
    add(srb.sketch.mirror(mirror_x_plane))
show(sub.sketch)
# %%
with BuildSketch() as scb:
    add(srb.sketch.mirror(mirror_xy_plane))
show(scb.sketch)
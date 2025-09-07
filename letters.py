#%% Imports
from build123d import *
from ocp_vscode import show
from math import radians, tan
import copy
#%% a
la = Line((0, 1), (1, 0))
la
#%%
ls = Line((0, 0), (1, 1))
ls
#%%
lm = RadiusArc((0, 0), (1, 1), 1)
lm
#%%
lo = RadiusArc((0, 1), (1, 0), 1)
lo
#%%
lt = RadiusArc((0, 0), (1, 1), -1)
lt
#%%
li = RadiusArc((0, 1), (1, 0), -1)
li
#%%
with BuildLine() as lkb:
    TangentArc([(0,0), lm @ 0.5], tangent=(1,0))
    TangentArc([lm @ 0.5, (1,1)], tangent=(1,-1))
lk = lkb.wire()
lk
#%%
with BuildLine() as lwb:
    TangentArc([(0,0), lt @ 0.5], tangent=(0,1))
    TangentArc([lt @ 0.5, (1,1)], tangent=(-1,1))
lw = lwb.wire()
lw
#%%
with BuildLine() as lyb:
    TangentArc([(0,1), li @ 0.5], tangent=(1,0))
    TangentArc([li @ 0.5, (1,0)], tangent=(1,1))
ly = lyb.wire()
ly
#%%
cx = Location((0.5,0.5))
with BuildLine() as llb:
    add(lt)
    r = (cx.position - (lt @ 0.5)).length
    add(Wire.make_circle(r).moved(cx))
ll = Compound(llb.wires())
ll
#%%
with BuildLine() as leb:
    add(li)
    r = (cx.position - (li @ 0.5)).length
    add(Wire.make_circle(r).moved(cx))
le = Compound(leb.wires())
le
#%%
with BuildLine() as lpb:
    add(lm)
    r = (cx.position - (lm @ 0.5)).length
    add(Wire.make_circle(r).moved(cx))
lp = Compound(lpb.wires())
lp
#%%
# Based on circle: center on horizontal line y = 0.5, coincident with cx, and M arc
with BuildLine() as lrb:
    k1 = Vector(0.2, 0.6)
    k2 = Vector(0.8, 0.4)
    a1 = TangentArc([(0,0),k1], tangent=(0,1))
    a2 = TangentArc([a1@1, cx.position], tangent=a1%1)
    a3 = TangentArc([a2@1, k2], tangent=a2%1)
    TangentArc([a3@1, (1,1)], tangent=a3%1)
lr = Compound(lrb.wires())
lr

# %%

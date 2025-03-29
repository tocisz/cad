#%%
import OCP
from build123d import *
from ocp_vscode import *
from math import sqrt
#%%
# 10 thread spools arranged similarly to billard balls in a triangle

r1 = 6*MM # inside
r2 = 9*MM # outside
r3 = 15*MM # max spool with thread

l1 = 5*MM
l2 = 2*MM
l3 = 10*MM

# Vectors for generating tringle grid
gen = [
    r3 * Vector(2, 0),
    r3 * Vector(1, sqrt(3))
]
gen
#%%
# Generate points
N = 4
locs = []
center = gen[0]+gen[1]
for i in range(N):
    for j in range(N-i):
        locs.append(gen[0]*i + gen[1]*j - center)
locs
#%%
mirror_plane = Plane.YZ
flip_x = OCP.gp.gp_Trsf()
flip_x.SetMirror(
    OCP.gp.gp_Ax2(mirror_plane.origin.to_pnt(), mirror_plane.z_dir.to_dir())
)
flip_x = Matrix(flip_x)

margin = [ # why rotation is reversed ? default is bottom view (Y going down) ?
    gen[1].rotate(axis=Axis.Z, angle=-90).transform(flip_x),
    gen[1].rotate(axis=Axis.Z, angle=-90),
    gen[0].rotate(axis=Axis.Z, angle=90),
]
margin
#%%
outline = [
    locs[0]   + margin[0],
    locs[-1]  + margin[1],
    locs[N-1] + margin[2]
]
outline
#%%
with BuildSketch() as base:
    with BuildLine():
        Polyline(outline, close=True)
    make_face()
    fillet(base.vertices(), radius=r3)

show(base)
# %%
with BuildSketch() as r1circles:
    with Locations(locs):
        Circle(radius=r1)

with BuildSketch() as r2circles:
    with Locations(locs):
        Circle(radius=r2)

show(base, r1circles, r2circles)
#%%
with BuildPart() as bottom:
    add(base)
    extrude(amount=l1)
    with Locations([(0,0,l1)]):
        add(r2circles)
        extrude(amount=-l2, mode=Mode.SUBTRACT)
    with Locations([(0,0,l1-l2)]):
        add(r1circles)
        extrude(amount=l3)
show(bottom)
#%%
export_step(bottom.part, "thread_box.step")
# %%

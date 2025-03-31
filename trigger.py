#%%
from build123d import *
from ocp_vscode import *
import math
#%%
w = 64*MM
r = 20*MM
h = 5*MM
d = 2*MM
angle = math.degrees(math.atan2(h, w/2))

with BuildSketch() as outline:
    Triangle(a=w, B=angle, C=angle, align=(Align.CENTER,Align.MIN))
    fillet(outline.vertices().sort_by(Axis.Y)[-1], radius=r)
    fillet(outline.vertices().sort_by(Axis.Y).group_by(Axis.Y)[0], radius=0.4*MM)

show(outline.sketch)

# %%
with BuildPart() as part:
    add(outline)
    extrude(amount=d)
show(part.part)
# %%
export_step(part.part, "trigger.step")

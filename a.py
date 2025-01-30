# %%
import cadquery as cq
from ocp_vscode import *
# %%
w1 = 3.42
w2 = 3.32
w3 = 4.0
w4 = 13.6
w5 = 4.5
w6 = 3.48

l1 = 3
l2 = 1
l3 = 3
l4 = 1.5
l5 = 2.1-l4
l6 = 42.2 - (l4+l5)
l7 = 1 # round to 0

ls1 = l1
ls2 = ls1+l2
ls3 = ls2+l3
ls4 = ls3+l4
ls5 = ls4+l5
ls6 = ls5+l6
ls7 = ls6+l7

profile = (
    cq.Workplane("XZ")
    .moveTo(0, 0)
    .hLine(w1/2)
    # .lineTo(w1/2, ls1)
    # .lineTo(w2/2, ls1)
    # .lineTo(w2/2, ls2)
    # .lineTo(w1/2, ls2)
    .line((w3-w1)/2, ls3)
    .hLine((w4-w3)/2)
    .vLine(l4)
    .line((w5-w4)/2, l5)
    .line((w6-w5)/2, l6)
    .line(-w6/2, l7)
    .close()
)

show(profile, position=(0, -90, 0))
# %%

grove = (
    cq.Workplane("XZ")
    .moveTo(w2, l1)
    .rect(1, l2)   
)
gr = grove.revolve(360, (0, 0, 0), (0, 1, 0))
show(gr)
# %%

spindle = profile.revolve(360, (0, 0, 0), (0, 1, 0))

show(spindle)
# %%

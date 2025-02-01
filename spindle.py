
# %%
import cadquery as cq
from ocp_vscode import *
import numpy as np
# %%

# Define widths
w = np.array([
    3.42, # bottom
    0.1,  # notch
    4.0,  # below spool base
    13.6, # spool base
    4.5,  # above spool base
    3.48  # top
])
r = w / 2  # Radius is half of a diameter

# Define lengths
l = np.array([
    3, # under notch
    1, # notch length
    3, # above notch
    1.5, # spool base
    2.1 - 1.5 # top part of spool base
])
ls = np.cumsum(l)
ls = np.append(ls, 51) # total length

# Define constuction segments
e = np.array([
    [(0, 0), (0, ls[2])], # bottom left
    [(r[0], 0), (r[2], ls[2])], # bottom right
    [(0, ls[4]), (r[4], ls[4])], # spike base
    [(0, ls[5]), (r[5], ls[5])], # spike top
    [(0, ls[2]), (r[3], ls[2])], # spool base bottom
    [(r[3], ls[2]), (r[3], ls[3])], # spool right
])

notch_point = (l[0] + l[1]/2) / ls[2]
fr = 0.5 # default fillet radius

s = cq.Sketch()
for i in range(e.shape[0]):
    s = s.segment(tuple(e[i][0]), tuple(e[i][1]), f"e{i+1}", True)
s = s.segment((0, l[0]), (1, l[0]), "middle", True)
for i in range(e.shape[0]):
    s = s.constrain(f"e{i+1}", "Fixed", None)
s = s.constrain("middle", "Orientation", (1,0))
s = s.constrain("middle", "e1", "Distance", (0.0, notch_point, 0.0))
s = s.constrain("middle", "e2", "Distance", (1.0, notch_point, 0.0))
s = s.solve()
s = s.select("e1", "e2").hull()
s = s.select("e3", "e4").hull()
s = s.reset().vertices(">(1,1,0)").fillet(r[5])
s = s.reset().vertices(">X", tag="middle").rect(w[1], l[1], mode="s")
s = s.select("e3", "e5", "e6").hull(tag="base")
s = s.reset().vertices(">(1,1,0)", tag="base").fillet(fr)
s = s.clean()
s = s.reset().vertices("<<X[2]").fillet(fr)
# show(s)

body = cq.Workplane("XZ").placeSketch(s).revolve()
show(body)

#%%
cq.exporters.export(body, "spindle.stl")
cq.exporters.export(body, "spindle.step")

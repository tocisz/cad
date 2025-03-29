
# %%
import cadquery as cq
from ocp_vscode import *
import numpy as np
from helper import *
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

notch_point = (l[0] + l[1]/2) / ls[2]
fr = 0.5 # default fillet radius
#%%
s1 = cq.Sketch()
# constuction segments
s1 = s1.segment((0, 0),        (0, ls[2]),    "e1", True) # bottom left
s1 = s1.segment((r[0], 0),     (r[2], ls[2]), "e2", True) # bottom right
s1 = s1.segment((0, ls[4]),    (r[4], ls[4]), "e3", True) # spike base
s1 = s1.segment((0, ls[5]),    (r[5], ls[5]), "e4", True) # spike top
s1 = s1.segment((0, ls[2]),    (r[3], ls[2]), "e5", True) # spool base bottom
s1 = s1.segment((r[3], ls[2]), (r[3], ls[3]), "e6", True) # spool right
s1 = s1.segment((0, l[0]), (1, l[0]), "middle", True)
s1 = fix(s1, [f"e{i}" for i in range(1,7)])
s1 = s1.constrain("middle", "e1", "Distance", (0.0, notch_point, 0.0))
s1 = s1.constrain("middle", "e2", "Distance", (1.0, notch_point, 0.0))
s1 = s1.solve()
s1 = s1.select("e1", "e2").hull()
s1 = s1.select("e3", "e4").hull()
s1 = s1.reset().vertices(">(1,1,0)").fillet(r[5])
s1 = s1.reset().vertices(">X", tag="middle").rect(2*w[1], l[1], mode="s")
s1 = s1.select("e3", "e5", "e6").hull(tag="base")
s1 = s1.reset().vertices(">(1,1,0)", tag="base").fillet(fr)
s1 = s1.clean()
s1 = s1.reset().vertices("<<X[2]").fillet(fr)
# show(s1, position=(0, 0, 90), target=(0, 25, 0))

body1 = cq.Workplane("XZ").placeSketch(s1).revolve()
# show(body1)

#%%
r0 = 8/2
r1 = 46/2
r2 = 54/2
h = 8
thick = 2.3
ttop = 1
t2 = 1
distance = 0.2
fr1 = 0.4
fr2 = 0.4
fr3 = 1

e_ref = (r[4], ls[4]), (r[5], ls[5])
e_ref1 = tuple(map(lambda p: move(p, (distance, 0)), e_ref))

s = cq.Sketch()
# s = s.segment(*e_ref, "ex", True)
p1 = (r2, ls[4]+h)
p2 = (r1+t2, ls[4])
s = s.segment(p1, p2, "outer")
s = s.segment(p2, e_ref1[0], "bottom") # base bottom
l1 = horizontal_line(ls[4]+h)
p1 = intersection_of_lines(line_from_points(*e_ref1),l1)
s = s.segment(e_ref1[0], p1, "inner")
p3 = move(p1,(ttop,0))
s = s.segment(p1, p3, "h1") # inner rim
p4 = (r0, ls[4]+thick)
s = s.segment(p3, p4, "s1") # slope down
p5 = (r1, ls[4]+thick)
s = s.segment(p4, p5, "b1") # upper bottom
p6 = (r2-ttop, ls[4]+h)
s = s.segment(p5, p6, "s1") # slope up
s = s.close()
s = s.assemble()
s = s.reset().vertices(">Y").fillet(fr1)
s = s.reset().vertices(">>Y[1]").fillet(fr2)
s = s.reset().vertices("<Y").chamfer(fr3)
s = s.reset().vertices(">>Y[1]").fillet(2*fr3)
s = s.reset().vertices(">>Y[2]").fillet(2*fr3)

show(s1, s, position=(0, 0, 90), target=(0, 25, 0))

# %%
body2 = cq.Workplane("XZ").placeSketch(s).revolve()

# %%

show(body1, body2)

#%%

glue = 0.05
# Create a half-space block that covers only y > 0
clip_box = cq.Workplane("XY").box(20, 20, 120).translate((0, 10+glue, 0))  # Positioned to cover y > 0

# Intersect the solid with the clipping box
body3 = body1.intersect(clip_box)
show(body3)

body1.export("half.step")
#%%
cq.exporters.export(body1, "spindle1.stl")
cq.exporters.export(body1, "spindle1.step")
cq.exporters.export(body2, "spindle2.stl")
cq.exporters.export(body2, "spindle2.step")

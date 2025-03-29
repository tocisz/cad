#%%
import numpy as np

#%%
import cadquery as cq
from ocp_vscode import *
#%%
from helper import *
def dist(A):
    return np.sqrt(np.sum(A**2))

# %%
a = 2
b = 8.0
O = np.array([0.0,0.0])
A = np.array([0.0,a])
B = np.array([b,0.0])
AB = B-A
M = (A+B)/2
MA = (A+M)/2
MB = (B+M)/2
lAB = dist(AB)
dAB=AB/lAB
rot90 = np.array([[0,-1],[1,0]])
dABrot = np.dot(dAB, rot90)
lABrot = line_from_points(MA,MA+dABrot)
X = intersection_of_lines(lABrot, vertical_line(0))
dx = dist(A-X)-dist(MA-X)
MAx = MA-dABrot*dx
MBx = MB+dABrot*dx

w = 0.2

s = (cq.Sketch()
    #  .segment(tuple(B),tuple(O))
     .segment(tuple(O),tuple(A),"ox",True)
     .arc(tuple(A),tuple(MAx),tuple(M))
     .arc(tuple(MBx),tuple(B))
     .assemble()
     .wires().offset(w)
     .reset().vertices("<Y",tag="ox")
     .circle(a+w)
    #  .clean()
    #  .segment(tuple(MA),tuple(MAx))
    #  .segment(tuple(MA), tuple(X))
)
# show(s)
#%%
p1 = cq.Workplane("XY").placeSketch(s).extrude(2*b)
p2 = p1.transformed(rotate=(0, 0, 120)).placeSketch(s).extrude(2*b)
p3 = p1.transformed(rotate=(0, 0, 240)).placeSketch(s).extrude(2*b)

part = p1.union(p2).union(p3).translate((0,0,-b))
show(part)

#%%
box = cq.Workplane("XY").box(2*b,2*b,2*b).translate((0,0,3/4*b))
sp1 = cq.Workplane("XY").sphere(b)
sp2 = cq.Workplane("XY").sphere(b-w)
sp = cq.Workplane("XY").add(sp1).cut(sp2).cut(part).intersect(box)

show(sp, show_result=False)
# %%
cone = cq.Solid.makeCone(a,b-w,b-a)
cone = cone.shell([cone.faces("<Z"),cone.faces(">Z")], w)

# print(type(part)) # class 'cadquery.cq.Workplane'
# partrot = cq.Workplane("XY").transformed(rotate=(0,0,0)).add(part.rotate)
# print(type(partrot)) # class 'cadquery.cq.Workplane'
# show(partrot)

w2 = 0.4 # guessed
cw = cq.Workplane("XY").add(cone).translate((0,0,b)).cut(part.rotate((0,0,0),(1,0,0),180).translate((0,0,b))).union()
print(type(cw))

all = cq.Workplane("XY").add(sp).add(cw).union()
show(all)

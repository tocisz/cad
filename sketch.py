#%%
import cadquery as cq
from ocp_vscode import *
#%%

result = (
    cq.Sketch()
    .trapezoid(4, 3, 90)
    .vertices()
    .circle(0.5, mode="s")
    .reset()
    .vertices()
    .fillet(0.25)
    .reset()
    .rarray(0.6, 1, 5, 1)
    .slot(1.5, 0.4, mode="s", angle=90)
    .reset()
)
show(result)
# %%

result = (
    cq.Sketch()
    .rect(1, 2, mode="c", tag="base")
    .vertices(tag="base")
    .circle(0.7)
    .reset()
    .edges("|Y", tag="base")
    .ellipse(1.2, 1, mode="i")
    .reset()
    .rect(2, 2, mode="i")
    .clean()
)
show(result)

# %%
result = (
    cq.Sketch()
    .segment((0.0, 0), (0.0, 2.0))
    .segment((2.0, 0))
    .close()
    .arc((0.6, 0.6), 0.4, 0.0, 360.0)
    .assemble(tag="face")
    .edges("%LINE",tag="face")
    .vertices()
    .fillet(0.2)
)
show(result)

# %%
result = (
    cq.Sketch()
    .arc((0, 0), 1.0, 0.0, 360.0)
    .arc((1, 1.5), 0.5, 0.0, 360.0)
    .segment((0.0, 2), (-1, 3.0))
    .hull()
)
show(result)
# %%

# this is strange...
# this arc has its dimensions, but solver will change them...
# what can be changed what not?
# everything can be changes if not fixed?
# looks like.. changing parameters of arc gives the same result
result = (
    cq.Sketch()
    .segment((0, 0), (0, 3.0), "s1")
    .arc((0.0, 3.0), (1.5, 1.5), (0.0, 0.0), "a1")
    .constrain("s1", "Fixed", None)
    .constrain("s1", "a1", "Coincident", None)
    .constrain("a1", "s1", "Coincident", None)
    .constrain("s1", "a1", "Angle", 45)
    .solve()
    .assemble()
)
show(result)
# %%

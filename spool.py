# %%
import cadquery as cq
from ocp_vscode import *

# %%
# Parameters
shaft_diameter = 10  # Diameter of the spindle shaft (mm)
shaft_length = 20  # Length of the spindle shaft (mm)
flange_diameter = 30  # Diameter of the flanges (mm)
flange_thickness = 2  # Thickness of each flange (mm)
hole_diameter = 5  # Diameter of the central hole (mm)
fillet_radius = 1  # Radius for fillets (mm)

# Create the shaft
shaft = cq.Workplane("XY").circle(shaft_diameter / 2).extrude(shaft_length)

# Create the flanges
flange1 = cq.Workplane("XY").circle(flange_diameter / 2).extrude(flange_thickness)
#flange1 = flange1.edges("<Z").fillet(fillet_radius)
flange2 = cq.Workplane("XY").circle(flange_diameter / 2).extrude(flange_thickness).translate((0, 0, shaft_length - flange_thickness))
#flange2 = flange2.edges(">Z").fillet(fillet_radius)

# Combine parts
spindle = shaft.union(flange1).union(flange2)
spindle = spindle.faces("<Z").workplane().hole(hole_diameter, shaft_length + 2 * flange_thickness)

# Show the result
show(spindle)

# %%
spindle.export("spindle.step")
# %%

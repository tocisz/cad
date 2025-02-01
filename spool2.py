# %%
import cadquery as cq
from ocp_vscode import *

# %%
# Parameters
shaft_diameter = 10  # Diameter of the spindle shaft (mm)
shaft_length = 20  # Length of the spindle shaft (mm)
flange_diameter = 30  # Diameter of the flanges (mm)
thickness = 2  # Thickness of each flange (mm)
hole_diameter = 5  # Diameter of the central hole (mm)
fillet_radius = 1  # Radius for fillets (mm)

# Create 2D profile
# profile = (cq.Workplane("XZ")
#     .moveTo(shaft_diameter / 2, 0)
#     .lineTo(flange_diameter / 2, 0)
#     .lineTo(flange_diameter / 2, thickness)
#     .lineTo(shaft_diameter / 2+thickness, thickness)
#     .lineTo(shaft_diameter / 2+thickness, shaft_length - thickness)
#     .lineTo(flange_diameter / 2, shaft_length - thickness)
#     .lineTo(flange_diameter / 2, shaft_length)
#     .lineTo(shaft_diameter / 2, shaft_length)
#     .lineTo(shaft_diameter / 2, 0)
#     .close())

profile = (cq.Sketch()
    .segment((shaft_diameter / 2, 0), (flange_diameter / 2, 0))
    .segment((flange_diameter / 2, thickness))
    .segment((shaft_diameter / 2 + thickness, thickness))
    .segment((shaft_diameter / 2 + thickness, shaft_length - thickness))
    .segment((flange_diameter / 2, shaft_length - thickness))
    .segment((flange_diameter / 2, shaft_length))
    .segment((shaft_diameter / 2, shaft_length))
    .close()
    .assemble(tag="t1")
    .edges("%LINE", tag="t1")
    .vertices()
    .chamfer(1)
)

print(type(profile))

show(profile)
# %%

# Revolve to create the spindle
spindle = cq.Workplane("XZ").placeSketch(profile) #.revolve(360, (0, 0, 0), (0, 1, 0))


# Add fillets
#spindle = spindle.edges().fillet(fillet_radius)

# Show the result
show(spindle)

# %%
spindle.export("spindle2.step")
# %%

#%%
from build123d import *
from ocp_vscode import show
from math import cos, pi

# %%
# Inner dimensions (mm)
inner_x, inner_y, inner_z = 55, 22.8, 12
wall = 1  # wall thickness

screw_distance = 46
flap_r = 4
flap_d = 1.5

slot_spacing = 7
slot_d = 3

# Outer enclosure dimensions (mm)
outer_x, outer_y, outer_z = inner_x+2*wall, inner_y+2*wall, inner_z+wall

with BuildPart() as enclosure:
    # Create the outer box
    base = Box(outer_x, outer_y, outer_z)

    # M3 nut cavity: nominal width across flats is ~5mm
    nut_flat = 5.6
    nut_depth = 2.6  # common depth
    screw_dia = 3.1  # clearance for M3

    # Positions of screws
    screw_pos_y = outer_y/2 - wall - nut_flat/2 - 1.1
    positions = [(-screw_distance/2, screw_pos_y), (screw_distance/2, screw_pos_y),
                 (-screw_distance/2, -screw_pos_y), (screw_distance/2, -screw_pos_y)]

    # Sketch on the bottom face for nut cavities
    bottom_face = enclosure.faces().sort_by(Axis.Z)[0]
    with BuildSketch(bottom_face):
        with Locations(positions):
            RegularPolygon(radius=nut_flat / (2 * cos(pi / 6)), side_count=6)

    # Cut nut cavities
    extrude(amount=-nut_depth, mode=Mode.SUBTRACT)

    # Shell the part inward to create the cavity, leaving top open
    top_face = enclosure.faces().sort_by(Axis.Z)[-1]
    offset(amount=-wall, openings=top_face)

    # Drill screw holes through bottom face aligned with nut cavities
    with BuildSketch(bottom_face):
        with Locations(positions[0:2]):
            Circle(radius=screw_dia / 2)

    # Cut holes upward
    extrude(amount=-outer_z, mode=Mode.SUBTRACT)

    right_face = enclosure.faces().sort_by(Axis.X)[0]
    with BuildSketch(right_face):
        with Locations([(0,-slot_spacing/2),(0,slot_spacing/2)]):
            SlotOverall(width=outer_z/2+slot_d, height=slot_d, align=(Align.MIN, Align.CENTER))
    extrude(amount=-2*wall, mode=Mode.SUBTRACT)

    flap_dist = inner_x/2+flap_r
    with BuildSketch(bottom_face):
        SlotCenterToCenter(center_separation=2*flap_dist, height=2*flap_r)
    extrude(amount=-flap_d, mode=Mode.ADD)
    with BuildSketch(bottom_face):
        with Locations([(-flap_dist,0),(flap_dist,0)]):
            Circle(radius=screw_dia/2)
    extrude(amount=-flap_d, mode=Mode.SUBTRACT)

show(enclosure.part)
# %%
print(screw_pos_y*2)
# %%
export_step(enclosure.part, "enclosure.step")

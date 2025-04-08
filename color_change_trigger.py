# %%
from build123d import *
from ocp_vscode import show
import math
# %%
shapes = import_svg("drawing.svg", label_by='inkscape:label')
# %%
with BuildSketch() as from_bottom:
    add(shapes.faces().sort_by(SortBy.AREA,reverse=True)[0])
show(from_bottom.sketch)

# %%
h1 = 3.2*MM
h2 = 5.8*MM
from_bottom_bb = from_bottom.face().bounding_box()
from_bottom_size = from_bottom_bb.size
w = from_bottom_size.X # measured 14.4
w1 = 6*MM
l = from_bottom_size.Y

with BuildSketch() as from_side:
    Polygon((0,0),(0,h2),(w1,h1),(w,h1),(w,0), align=(Align.MAX, Align.MIN))
show(from_side.sketch)
# %%
h0 = 1.6*MM
cutout_h = 12*MM
slot1_l = 9*MM
slot1_d = 5.5*MM
slot1_d2 = 8*MM
slot1_loc = Vector(-0.8*MM, 3*MM) # from bottom right
slot1_separation = 8*MM # approximataly, not quite right
slot1_locX = Vector(-slot1_d2/2-slot1_loc.X, slot1_loc.Y+slot1_d/2)
slot2_d = slot1_d
slot2_left = (14.4-7.3)*MM
slot2_bottom = 12*MM
slot2_loc = Vector(slot2_d/2, slot2_bottom)
slot2_width = slot2_left+slot2_d/2 # goes d/2 outside on right
drill1_d = 3.5*MM # measure..
drill1_loc = Vector(-2*MM, 26*MM)
drill2_slot1_distance = 37.7
drill2_d1 = 5*MM
drill2_d2 = 8*MM
drill2_loc = Vector(-6.2*MM-slot1_d/2,drill2_slot1_distance+(slot1_d+drill2_d1)/2)
drill3_d = 4.5*MM
drill3_loc = Vector(-1.5*MM, 46.5*MM)

# rectangle pocket on the bottom
pocket_depth = 1.3*MM
pocket_width1, pocket_height1 = 13*MM, 10*MM
pocket_width2, pocket_height2 = 11*MM, 8*MM
pocket_loc = Vector(0, 27*MM)

with BuildPart(Plane.XZ) as main:
    add(from_side.sketch)
    extrude(amount=-l)

    bottom_face = main.faces().sort_by(Axis.Z)[0]
    bottom_face_bb = bottom_face.bounding_box()
    with BuildSketch(bottom_face) as base:
        with Locations(from_bottom_bb.center()):
            add(from_bottom.face(), rotation=180)
    extrude(amount=-h2, mode=Mode.INTERSECT)

    with BuildSketch(Plane.XY.offset(h1)) as rect_cut:
        Rectangle(width=w, height=cutout_h,align=(Align.MAX, Align.MIN))
    extrude(amount=h2-h1, mode=Mode.SUBTRACT)

    with BuildSketch() as bottom_drilling:
        with Locations(slot1_loc):
            SlotOverall(width=slot1_l, height=slot1_d, align=(Align.MAX, Align.MIN))
        with Locations(drill2_loc):
            Circle(radius=drill2_d1/2)
        with Locations(slot2_loc):
            SlotOverall(width=slot2_width, height=slot2_d, align=(Align.MAX, Align.MIN))
        with Locations(drill1_loc):
            Circle(radius=drill1_d/2, align=(Align.MAX, Align.MIN))
        with Locations(drill3_loc):
            Circle(radius=drill3_d/2, align=(Align.MAX, Align.MIN))
    extrude(amount=h2, mode=Mode.SUBTRACT)

    with BuildSketch(Plane.XY.offset(h0)) as top_drilling:
        with Locations(slot1_locX):
            # TODO translate to SlotOverall, use same alignment
            SlotCenterToCenter(center_separation=slot1_separation, height=slot1_d2)
        with Locations(drill2_loc):
            Circle(radius=drill2_d2/2)
    extrude(amount=h2, mode=Mode.SUBTRACT)

    with BuildSketch() as bottom_pocket1:
        with Locations(pocket_loc):
            Rectangle(width=pocket_width1, height=pocket_height1, align=(Align.MAX, Align.MIN))
    with BuildSketch(Plane.XY.offset(pocket_depth)) as bottom_pocket2:
        with Locations(bottom_pocket1.face().center()):
            Rectangle(width=pocket_width2, height=pocket_height2)
    loft([bottom_pocket1.sketch.face(), bottom_pocket2.sketch.face()], mode=Mode.SUBTRACT)

    with BuildSketch(Plane.XY.offset(h1)) as top_profile:
        with BuildLine() as bl:
            Polyline([(0,24),(0,30),(-3,30),(-w,12+6),(-w,12),(6-w,12),(0,24)])
        make_face()
    extrude(top_profile.sketch, amount=8)

show(main.part)
# %%
export_step(main.part, "color_change_trigger.step")

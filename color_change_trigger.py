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
slot1_separation = 7*MM # approximataly
slot1_locX = Vector(-slot1_d2/2, slot1_loc.Y+slot1_d/2)
slot2_d = slot1_d
slot2_left = (14.4-7.3)*MM
drill1_r = 3.5*MM # measure..
drill2_slot1_distance = 37.7
drill2_d1 = 5*MM
drill2_d2 = 8*MM
drill2_loc = Vector(-6.2*MM-slot1_d/2,drill2_slot1_distance+(slot1_d+drill2_d1)/2)
drill3_r = 4.5*MM
with BuildPart(Plane.XZ) as main:
    add(from_side.sketch)
    extrude(amount=-l)

    bottom_face = main.faces().sort_by(Axis.Z)[0]
    bottom_face_bb = bottom_face.bounding_box()
    with BuildSketch(bottom_face) as base:
        with Locations(from_bottom_bb.center()):
            add(from_bottom.face(), rotation=180)
    extrude(amount=-h2, mode=Mode.INTERSECT)

    with BuildSketch(Plane(origin=Vector(Z=h1))) as rect_cut:
        Rectangle(width=w, height=cutout_h,align=(Align.MAX, Align.MIN))
    extrude(amount=h2-h1, mode=Mode.SUBTRACT)

    with BuildSketch() as bottom_drilling:
        with Locations(slot1_loc):
            SlotOverall(width=slot1_l, height=slot1_d, align=(Align.MAX, Align.MIN))
        with Locations(drill2_loc):
            Circle(radius=drill2_d1/2)
    extrude(amount=h2, mode=Mode.SUBTRACT)

    with BuildSketch(Plane(origin=Vector(Z=h0))) as top_drilling:
        with Locations(slot1_locX):
            SlotCenterToCenter(center_separation=slot1_separation, height=slot1_d2)
        with Locations(drill2_loc):
            Circle(radius=drill2_d2/2)
    extrude(amount=h2, mode=Mode.SUBTRACT)
show(main.part)
# %%
export_step(main.part, "color_change_trigger.step")
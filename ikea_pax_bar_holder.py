"""IKEA PAX bar holder — reverse-engineered from cad/ikea_pax_bar_holder.stl.

Style: sketches extruded upward, like cad/bicycle_stand.py and
cad/color_change_trigger.py:

  1. base sketch (footprint at z=0) -> extrude up 0..3.5,
     with two screw holes subtracted as true circles;
  2. holder sketch (bar-seat profile at z=3.5) -> extrude up 3.5..18.5;
  3. diagonal gusset (brace under the holder overhang) added last.

All arcs are true circles fitted to the STL boundary loops
(max residual ~5e-10 mm); round holes are real circles, so the
triangle artefacts of the STL disappear.

Units: STL units = mm.
"""
# %% Imports
import math

from build123d import *
from ocp_vscode import show

# %% Dimensions (mm), from fitted STL boundary loops
#
# Only fitted values are hardcoded once; everything else is derived below,
# so each dimension has a single source of truth.
BASE_H = 3.5
TOP_Z = 18.5
HOLDER_H = TOP_Z - BASE_H  # 3.5 -> 18.5

R_OUTER = 14.0  # base SW/NW arcs and holder top/bottom arcs
R_EAST = 11.0  # base NE/SE arcs
R_SMALL = 9.0  # base N/S-small arcs and bar-seat slot

# shared centres: footprint origin doubles as holder bottom centre,
# seat height doubles as slot / top centre
BOT_C = (0.0, 0.0)
SEAT_C = (0.0, 18.0)
SLOT_C = SEAT_C
TOP_C = SEAT_C
BOT_R = R_OUTER
TOP_R = R_OUTER
SLOT_R = R_SMALL  # inner semicircle: the bar seat

# base outline (footprint, z = 0): a rounded rectangle on the west plus a
# rounded slot on the east; the slot/rect junctions get small fillets.
# Fitted screw-hole centres, each stated once.
BASE_NE_C = (38.0, 41.0)
BASE_SE_C = (38.0, -23.0)
HOLE_CENTRES = (BASE_NE_C, BASE_SE_C)
HOLE_R = 3.25
# east slot: axis through the screw holes, tips flush with the east arcs
SLOT_W = 2 * R_EAST
SLOT_MID = (
    (HOLE_CENTRES[0][0] + HOLE_CENTRES[1][0]) / 2,
    (HOLE_CENTRES[0][1] + HOLE_CENTRES[1][1]) / 2,
)
SLOT_LEN = (BASE_NE_C[1] + R_EAST) - (BASE_SE_C[1] - R_EAST)
# west rounded rectangle: x from the outer radius to the slot's east wall
# (rounded east corners hide inside the slot), y from the southern outer
# tangent to the northern small-arc tangent
RECT_WEST = SEAT_C[0] - R_OUTER
RECT_SOUTH = BOT_C[1] - R_OUTER
RECT_NORTH = BASE_NE_C[1] - R_SMALL
RECT_EAST = SLOT_MID[0] + SLOT_W / 2  # slot's east wall
JUNC_X = SLOT_MID[0] - SLOT_W / 2  # slot's west wall: rect/slot junction axis
RECT_C = ((RECT_WEST + RECT_EAST) / 2, (RECT_SOUTH + RECT_NORTH) / 2)
RECT_W, RECT_H = RECT_EAST - RECT_WEST, RECT_NORTH - RECT_SOUTH

# holder outline (bar-seat profile, z = 3.5..18.5): fitted fillets kept,
# shared circles/axes derived above
LEG_X = SLOT_R
LEG_Y = -5.294850839  # inner leg bottom (slot opening)
FIL_E_C = (10.915282195687096, -4.521257921607456)
FIL_E_R = 2.065611747409030
FIL_E_A0 = -158.005949111644
FIL_E_SWEEP = 135.505949084557
FIL_W_C = (-11.027479153399675, -5.294850838344032)
FIL_W_R = 2.027479153561825
FIL_W_A0 = -122.752084492399
FIL_W_SWEEP = 122.752084473861
BRIDGE_E_ANG = -22.5  # fillet-end angle on FIL_E circle
BRIDGE_B_ANG = -15.0  # bridge angle on the outer BOT_C circle
BRIDGE_E = (  # fillet end, on the FIL_E circle
    FIL_E_C[0] + FIL_E_R * math.cos(math.radians(BRIDGE_E_ANG)),
    FIL_E_C[1] + FIL_E_R * math.sin(math.radians(BRIDGE_E_ANG)),
)
BRIDGE_B = (  # outer circle point at BRIDGE_B_ANG
    BOT_C[0] + BOT_R * math.cos(math.radians(BRIDGE_B_ANG)),
    BOT_C[1] + BOT_R * math.sin(math.radians(BRIDGE_B_ANG)),
)
W_OUTER_SWEEP = 30.0  # outer arc from 180 deg up to the west fillet

# gusset (diagonal brace, wall y = 0..18), derived from the part envelope
GUS_X0 = R_OUTER  # inner edge under the holder legs (x=14)
GUS_X1 = BASE_SE_C[0] + R_EAST  # outer edge flush with the base east (38+11)
GUS_Z0, GUS_Z1 = BASE_H, TOP_Z
GUS_Y0, GUS_Y1 = BOT_C[1], SEAT_C[1]


# %% Sketches
def base_sketch():
    """Footprint: west rounded rectangle + east slot, junctions filleted."""
    with BuildSketch() as sec:
        with Locations(Location(RECT_C)):
            RectangleRounded(RECT_W, RECT_H, R_OUTER)
        with Locations(Location(SLOT_MID)):
            SlotOverall(SLOT_LEN, SLOT_W, rotation=90)
        # Concave rect/slot junctions get the small radius; they sit at
        # (JUNC_X, RECT_NORTH/SOUTH), distinct from the slot-tip corners
        # at the same x.
        junc = sec.vertices().filter_by(
            lambda v: abs(v.center().X - JUNC_X) < 1e-6
            and (
                abs(v.center().Y - RECT_NORTH) < 1e-6
                or abs(v.center().Y - RECT_SOUTH) < 1e-6
            )
        )
        fillet(junc.sort_by(Axis.Y), radius=R_SMALL)
        with Locations(*HOLE_CENTRES):
            Circle(HOLE_R, mode=Mode.SUBTRACT)
    return sec.sketch


def holder_sketch():
    """Bar-seat profile: inner slot, fillets, tangent bridge, outer arcs."""
    with BuildSketch(Plane.XY.offset(BASE_H)) as sec:
        with BuildLine():
            # All arcs first, then @-to-@ straights bridge arc endpoints.
            seat = CenterArc(SLOT_C, SLOT_R, 180.0, -180.0)
            fil_e = CenterArc(FIL_E_C, FIL_E_R, FIL_E_A0, FIL_E_SWEEP)
            outer_e = CenterArc(BOT_C, BOT_R, BRIDGE_B_ANG, -BRIDGE_B_ANG)
            top = CenterArc(TOP_C, TOP_R, 0.0, 180.0)
            outer_w = CenterArc(BOT_C, BOT_R, 180.0, W_OUTER_SWEEP)
            fil_w = CenterArc(FIL_W_C, FIL_W_R, FIL_W_A0, FIL_W_SWEEP)
            Line(seat @ 0, fil_w @ 1)  # west inner leg
            Line(seat @ 1, fil_e @ 0)  # east inner leg
            Line(fil_e @ 1, outer_e @ 0)  # tangent bridge
            Line(outer_e @ 1, top @ 0)  # east outer vertical
            Line(top @ 1, outer_w @ 0)  # west outer vertical
            Line(outer_w @ 1, fil_w @ 0)  # closes the loop
        make_face()
    return sec.sketch


def gusset_profile():
    """Diagonal brace triangle (side profile); draws the current wire."""
    base = Line((GUS_X0, GUS_Z0), (GUS_X1, GUS_Z0))
    Line(base @ 1, (GUS_X0, GUS_Z1))  # hypotenuse up to the holder top
    Line((GUS_X0, GUS_Z1), base @ 0)  # inner vertical back to the start


# %% Model
def pax_bar_holder():
    with BuildPart() as model:
        add(base_sketch())
        extrude(amount=BASE_H)
        add(holder_sketch())
        extrude(amount=HOLDER_H)
        # NOTE: the gusset profile lives on Plane.XZ, so it must be drawn
        # inside this BuildPart (add() of an outside XZ sketch extrudes
        # along Z instead of Y).
        with BuildSketch(Plane.XZ.offset(GUS_Y0)):
            with BuildLine():
                gusset_profile()
            make_face()
        extrude(amount=-(GUS_Y1 - GUS_Y0))
    model.part.label = "IKEA PAX bar holder"
    return model.part


part = pax_bar_holder()
try:
    show(part)
except Exception as e:
    print(f"[viewer] pominięto show: {type(e).__name__}")
# %% Export STEP
export_step(part, "ikea_pax_bar_holder.step")

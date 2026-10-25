"""IKEA PAX bar holder — simplified mid-hole variant.

The holder reuses the clipped base outline instead of reproducing the
fitted outer fillets. Its bar slot remains exact: an 18 mm wide opening
with a 9 mm radius seat centred at (0, 18).

Original feature sequence: third screw hole + head counterbore.

Style: sketches extruded upward, like cad/bicycle_stand.py and
cad/color_change_trigger.py:

  1. base sketch (footprint at z=0) -> extrude up 0..3.5,
     with three screw holes subtracted as true circles
     (extra hole midway between the two originals);
  2. holder sketch (bar-seat profile at z=3.5) -> extrude up 3.5..18.5;
  3. diagonal gusset (brace under the holder overhang) added last;
  4. counterbore recess for the extra screw head cut from the gusset
     slope down to a flat bottom (10 mm dia for a 9 mm head).

The base dimensions and functional bar seat retain their fitted circular
geometry. The simplified outer holder is derived from those dimensions
rather than from the original outer-fillet loops.

Units: STL units = mm.
"""
# %% Imports
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
# extra screw hole: exactly midway between the two base holes
MID_HOLE_C = SLOT_MID
# counterbore for the screw head, cut from the gusset slope downward
CBORE_R = 5.0  # 10 mm dia recess for a 9 mm head
CBORE_BOTTOM = BASE_H  # same screw-head bearing height as the outer holes

# simplified holder: keep the exact bar slot, but derive its outside from
# the base instead of carrying over all fitted outer-fillet constants
HOLDER_FILLET = 2.0

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
        with Locations(*HOLE_CENTRES, MID_HOLE_C):
            Circle(HOLE_R, mode=Mode.SUBTRACT)
    return sec.sketch


def holder_sketch():
    """Clipped base outline with the exact round-top bar slot removed."""
    with BuildSketch(Plane.XY.offset(BASE_H)) as sec:
        # Intersect the base with a capsule centred on the bar. R14 around
        # the R9 seat and x=+/-14 around x=+/-9 give a uniform 5 mm wall.
        # Clipping also removes all base screw holes from this sketch.
        add(base_sketch())
        with Locations((BOT_C[0], (RECT_SOUTH + RECT_NORTH) / 2)):
            SlotOverall(
                RECT_H, 2 * R_OUTER, rotation=90, mode=Mode.INTERSECT
            )

        # Exact functional surface: vertical walls 18 mm apart and a 9 mm
        # radius semicircular seat at the original centre.
        with Locations(SLOT_C):
            Circle(SLOT_R, mode=Mode.SUBTRACT)
        slot_bottom = RECT_SOUTH - R_OUTER  # below the part: open the legs
        slot_h = SLOT_C[1] - slot_bottom
        with Locations((SLOT_C[0], slot_bottom + slot_h / 2)):
            Rectangle(2 * SLOT_R, slot_h, mode=Mode.SUBTRACT)

        # Round the two leg tips; the wall may be thinner only at these ends.
        lower_corners = sec.vertices().filter_by(
            lambda v: v.center().Y < -1e-6
        )
        fillet(lower_corners, radius=HOLDER_FILLET)
    return sec.sketch

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
                base = Line((GUS_X0, GUS_Z0), (GUS_X1, GUS_Z0))
                Line(base @ 1, (GUS_X0, GUS_Z1))
                Line((GUS_X0, GUS_Z1), base @ 0)
            make_face()
        extrude(amount=-(GUS_Y1 - GUS_Y0))
        # counterbore recess for the middle screw head: cut from the gusset
        # slope down to a flat bottom; leaves a full ring of material
        # around the 10 mm recess inside the 18 mm wide gusset.
        with BuildSketch(Plane.XY.offset(CBORE_BOTTOM)):
            with Locations(MID_HOLE_C):
                Circle(CBORE_R)
        extrude(amount=GUS_Z1 - CBORE_BOTTOM, mode=Mode.SUBTRACT)
    model.part.label = "IKEA PAX bar holder, simplified mid-hole variant"
    return model.part


part = pax_bar_holder()
try:
    show(part)
except Exception as e:
    print(f"[viewer] pominięto show: {type(e).__name__}")
# %% Export STEP
export_step(part, "ikea_pax_bar_holder_mid_hole_simple.step")

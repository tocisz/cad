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
from build123d import *
from ocp_vscode import show

# %% Dimensions (mm), from fitted STL boundary loops
BASE_H = 3.5
HOLDER_H = 15.0  # 3.5 -> 18.5

# base outline (footprint, z = 0)
BASE_NE_C = (38.0, 41.0)
BASE_NE_R = 11.0
BASE_SE_C = (38.0, -23.0)
BASE_SE_R = 11.0
BASE_NS_C = (18.0, 41.0)  # N-small arc centre (also S-small y=-23)
BASE_NS_R = 9.0
BASE_SW_C = (0.0, 0.0)
BASE_SW_R = 14.0
BASE_NW_C = (0.0, 18.0)
BASE_NW_R = 14.0
HOLE_CENTRES = ((38.0, 41.0), (38.0, -23.0))
HOLE_R = 3.25

# holder outline (bar-seat profile, z = 3.5..18.5)
SLOT_C = (0.0, 18.0)
SLOT_R = 9.0      # inner semicircle: the bar seat
TOP_C = (0.0, 18.0)
TOP_R = 14.0      # outer top semicircle
BOT_C = (0.0, 0.0)
BOT_R = 14.0      # outer bottom circle (legs)
LEG_X = 9.0
LEG_Y = -5.294850839  # inner leg bottom (slot opening)
FIL_E_C = (10.915282195687096, -4.521257921607456)
FIL_E_R = 2.065611747409030
FIL_E_A0 = -158.005949111644
FIL_E_SWEEP = 135.505949084557
FIL_W_C = (-11.027479153399675, -5.294850838344032)
FIL_W_R = 2.027479153561825
FIL_W_A0 = -122.752084492399
FIL_W_SWEEP = 122.752084473861
BRIDGE_E = (12.823658611, -5.311733316)   # fillet end (-22.5 deg)
BRIDGE_B = (13.522961568, -3.623466631)   # outer circle point (-15 deg)

# gusset (diagonal brace, wall y = 0..18)
GUS_X0, GUS_X1 = 14.0, 49.0
GUS_Z0, GUS_Z1 = 3.5, 18.5
GUS_Y0, GUS_Y1 = 0.0, 18.0


# %% Sketches
def base_sketch():
    """Footprint of the part with two true-circle screw holes."""
    with BuildSketch() as sec:
        with BuildLine():
            CenterArc((18.0, 41.0), 9.0, 0.0, -90.0)      # N-small -> (18, 32)
            Line((18.0, 32.0), (0.0, 32.0))               # north straight
            CenterArc((0.0, 18.0), 14.0, 90.0, 90.0)      # NW quarter -> (-14, 18)
            Line((-14.0, 18.0), (-14.0, 0.0))             # west straight
            CenterArc((0.0, 0.0), 14.0, 180.0, 90.0)      # SW quarter -> (0, -14)
            Line((0.0, -14.0), (18.0, -14.0))             # south straight
            CenterArc((18.0, -23.0), 9.0, 90.0, -90.0)    # S-small -> (27, -23)
            CenterArc((38.0, -23.0), 11.0, 180.0, 180.0)  # SE semicircle -> (49, -23)
            Line((49.0, -23.0), (49.0, 41.0))             # east straight
            CenterArc((38.0, 41.0), 11.0, 0.0, 180.0)     # NE semicircle -> (27, 41)
        make_face()
        with Locations(*HOLE_CENTRES):
            Circle(HOLE_R, mode=Mode.SUBTRACT)
    return sec.sketch


def holder_sketch():
    """Bar-seat profile: inner slot, fillets, tangent bridge, outer arcs."""
    with BuildSketch(Plane.XY.offset(BASE_H)) as sec:
        with BuildLine():
            Line((-LEG_X, LEG_Y), (-LEG_X, 18.0))            # west inner leg up
            CenterArc(SLOT_C, SLOT_R, 180.0, -180.0)         # bar seat via (0, 27)
            Line((LEG_X, 18.0), (LEG_X, LEG_Y))              # east inner leg down
            CenterArc(FIL_E_C, FIL_E_R, FIL_E_A0, FIL_E_SWEEP)  # east fillet
            Line(BRIDGE_E, BRIDGE_B)                         # tangent bridge
            CenterArc(BOT_C, BOT_R, -15.0, 15.0)             # outer arc -> (14, 0)
            Line((14.0, 0.0), (14.0, 18.0))                  # east outer vertical
            CenterArc(TOP_C, TOP_R, 0.0, 180.0)              # outer top semicircle
            Line((-14.0, 18.0), (-14.0, 0.0))                # west outer vertical
            CenterArc(BOT_C, BOT_R, 180.0, 30.0)             # outer arc -> (-12.12, -7)
            CenterArc(FIL_W_C, FIL_W_R, FIL_W_A0, FIL_W_SWEEP)  # west fillet
        make_face()
    return sec.sketch


def gusset_sketch():
    """Diagonal brace under the holder overhang (side profile, y 0..18)."""
    # Note: Plane.XZ normal is -Y, so offset(0) + extrude(-18) spans y 0..18.
    with BuildSketch(Plane.XZ.offset(GUS_Y0)) as sec:
        with BuildLine():
            Line((GUS_X0, GUS_Z0), (GUS_X1, GUS_Z0))
            Line((GUS_X1, GUS_Z0), (GUS_X0, GUS_Z1))
            Line((GUS_X0, GUS_Z1), (GUS_X0, GUS_Z0))
        make_face()
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
                Line((GUS_X0, GUS_Z0), (GUS_X1, GUS_Z0))
                Line((GUS_X1, GUS_Z0), (GUS_X0, GUS_Z1))
                Line((GUS_X0, GUS_Z1), (GUS_X0, GUS_Z0))
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

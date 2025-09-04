#%% Imports
from build123d import *
from ocp_vscode import show
import copy
# %%
def square_profile(d = 30, l = 100, r = 5, angle = 45):
    with BuildSketch() as sq:
        Rectangle(d, d)
        fillet(sq.vertices(), r)
    with BuildPart() as profile:
        extrude(sq.sketch, l)
        top = profile.faces().sort_by(Axis.Z)[-1]
        cut_plane = Plane.XY.rotated((45,0,0)).move(Location((0,0,d/2))).reverse()
        with BuildSketch(cut_plane) as cut:
            Rectangle(2*d, 2*d)
        extrude(cut.sketch, 2*d, mode=Mode.SUBTRACT)
        RigidJoint(label="flat_out", joint_location=top.center_location)
        RigidJoint(label="flat_in", joint_location=top.center_location * Rotation((0,180,0)))
        RigidJoint(label="angle_out", joint_location=cut_plane.location)
        RigidJoint(label="angle_in", joint_location=cut_plane.location * Rotation((0,180,0)))
    return profile.part

show(square_profile())

# %%
def bicycle_stand( b_width = 100, b_height = 5, b_length = 40, h = 800, l = 500):
    with BuildPart() as base:
        with BuildSketch() as bottom_sk:
            Rectangle(b_width, b_length)
        extrude(bottom_sk.sketch, b_height)
        top = base.faces().sort_by(Axis.Z)[-1]
        RigidJoint(label="central", joint_location=Location(top.center_location.position, Axis.X.direction, 180))

    b1 = copy.copy(base.part)
    b2 = copy.copy(base.part)
    p1v = square_profile(l=h)
    p2v = copy.copy(p1v)
    p1h = square_profile(l=l/2)
    p2h = copy.copy(p1h)
    b1.joints["central"].connect_to(p1v.joints["flat_out"])
    p1v.joints["angle_out"].connect_to(p1h.joints["angle_in"])
    p1h.joints["flat_out"].connect_to(p2h.joints["flat_in"])
    p2h.joints["angle_out"].connect_to(p2v.joints["angle_in"])
    p2v.joints["flat_out"].connect_to(b2.joints["central"])

    ass = Compound([b1, p1v, p1h, p2h, p2v, b2], label="bicycle stand")
    return ass
bs = bicycle_stand()
show(bs)
# %%
export_step(bs, "bicycle_stand.step")
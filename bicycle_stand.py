#%% Imports
from build123d import *
from ocp_vscode import show
from math import radians, tan
import copy
# %% Square profile with angled cut
def square_profile(l = 100, d = 30, r = 5, angle = 45):
    with BuildSketch() as sq:
        Rectangle(d, d)
        # fillet(sq.vertices(), r) # causes problem later
    with BuildPart() as profile:
        extrude(sq.sketch, l)
        top = profile.faces().sort_by(Axis.Z)[-1]

        zshift = (d/2)*tan(radians(angle))
        cut_plane = Plane.XY.rotated((angle,0,0)).move(Location(Vector(Z=zshift))).reverse()
        with BuildSketch(cut_plane) as cut:
            Rectangle(2*d, 2*d)
        extrude(cut.sketch, 2*d, mode=Mode.SUBTRACT)
        RigidJoint(label="flat_out", joint_location=top.center_location)
        RigidJoint(label="flat_out90", joint_location=top.center_location * Rot(Z=-90))
        RigidJoint(label="flat_out90l", joint_location=top.center_location * Rot(Z=90)) # what's the problem?
        RigidJoint(label="flat_in", joint_location=top.center_location * Rot(Y=180))
        RigidJoint(label="angle_out", joint_location=cut_plane.location)
        RigidJoint(label="angle_in", joint_location=cut_plane.location * Rot(Y=180))
    return profile.part

pp = square_profile()
pp2 = copy.copy(pp)
pp.joints["flat_out90"].connect_to(pp2.joints["flat_in"])
show(pp, pp2, pp.joints["flat_out90"].location)

# %% Bicycle stand
def bicycle_stand(h = 800, l = 500, b_width = 100, b_height = 2, b_length = 40):
    with BuildPart() as base:
        Box(b_width, b_length, b_height)
        top = base.faces().sort_by(Axis.Z)[-1]
        RigidJoint(label="central", joint_location=Location(top.center_location.position, Axis.X.direction, 180))

    b1 = copy.copy(base.part)
    b2 = copy.copy(base.part)
    p1v = square_profile(h)
    p2v = copy.copy(p1v)
    p1h = square_profile(l/2)
    p2h = copy.copy(p1h)
    b1.joints["central"].connect_to(p1v.joints["flat_out"])
    p1v.joints["angle_out"].connect_to(p1h.joints["angle_in"])
    p1h.joints["flat_out"].connect_to(p2h.joints["flat_in"])
    p2h.joints["angle_out"].connect_to(p2v.joints["angle_in"])
    p2v.joints["flat_out"].connect_to(b2.joints["central"])

    return Compound([b1, p1v, p1h, p2h, p2v, b2], label="bicycle stand")

# bs = bicycle_stand()
# show(bs)
## %% Bicycle stand 2
def bicycle_stand2(h = 800, l = 500, w = 1500, b_width = 100, b_height = 2, b_length = 40):
    with BuildPart() as bottom_builder:
        bt1r = square_profile(w/2)
        bt1r.locate(Location(Vector(Y=w/2), Axis.X.direction, 90))
        bt1l = copy.copy(bt1r)
        bt1r.joints["flat_out"].connect_to(bt1l.joints["flat_in"])
        add(bt1r)
        add(bt1l)
        RigidJoint(label="angle1_out", joint_location=bt1r.joints["angle_out"].location)
        RigidJoint(label="angle2_in", joint_location=bt1l.joints["angle_in"].location)
        top = bottom_builder.faces().sort_by(Axis.Z)[-1]
        RigidJoint(label="center", joint_location=top.center_location)
    b1 = bottom_builder.part
    b1.label = "b 1"
    b2 = copy.copy(b1)
    b2.label = "b 2"

    with BuildPart() as v1_builder:
        v1u = square_profile(h/2)
        v1d = copy.copy(v1u)
        v1u.joints["flat_out90"].connect_to(v1d.joints["flat_in"])
        add(v1u)
        add(v1d)
        RigidJoint(label="angle1_in", joint_location=v1d.joints["angle_in"].location)
        RigidJoint(label="angle2_out", joint_location=v1u.joints["angle_out"].location)
    v1 = v1_builder.part
    v1.label = "v 1"
    v4 = copy.copy(v1)
    v4.label = "v 4"

    with BuildPart() as v2_builder:
        v1u = square_profile(h/2)
        v1d = copy.copy(v1u)
        v1u.joints["flat_out90l"].connect_to(v1d.joints["flat_in"])
        add(v1d)
        add(v1u, clean=False)
        RigidJoint(label="angle1_in", joint_location=v1d.joints["angle_in"].location)
        RigidJoint(label="angle2_out", joint_location=v1u.joints["angle_out"].location)
    v2 = v2_builder.part
    v2.label = "v 2"
    v3 = copy.copy(v2)
    v3.label = "v 3"
    # v2 = v1.mirror(Plane.YZ) # mirrors only the shape, not the joints

    with BuildPart() as h1b:
        h1 = square_profile(l/2)
        h2 = copy.copy(h1)
        h1.joints["flat_out"].connect_to(h2.joints["flat_in"])
        add(h1)
        add(h2)
        RigidJoint(label="angle1_in", joint_location=h1.joints["angle_in"].location)
        RigidJoint(label="angle2_out", joint_location=h2.joints["angle_out"].location)
    h1 = h1b.part
    h1.label = "h 1"
    h2 = copy.copy(h1)
    h2.label = "h 2"
    h3 = copy.copy(h1)
    h3.label = "h 3"

    v5 = square_profile(h-30)
    v5.label = "v 5"
    v6 = copy.copy(v5)
    v6.label = "v 6"

    b1.joints["angle1_out"].connect_to(v1.joints["angle1_in"])
    b1.joints["angle2_in"].connect_to(v2.joints["angle2_out"])
    v1.joints["angle2_out"].connect_to(h1.joints["angle1_in"])
    h1.joints["angle2_out"].connect_to(v3.joints["angle1_in"])
    v3.joints["angle2_out"].connect_to(b2.joints["angle2_in"])
    b2.joints["angle1_out"].connect_to(v4.joints["angle1_in"])
    v2.joints["angle1_in"].connect_to(h2.joints["angle2_out"])
    b1.joints["center"].connect_to(v5.joints["flat_in"])
    v5.joints["angle_out"].connect_to(h3.joints["angle1_in"])
    h3.joints["angle2_out"].connect_to(v6.joints["angle_in"])

    return Compound(children=[b1, v1, v2, h1, v3, b2, v4, h2, v5, h3, v6], label="Bicycle stand 2")

bs = bicycle_stand2()
show(bs)
# %% Export STEP
export_step(bs, "bicycle_stand.step")
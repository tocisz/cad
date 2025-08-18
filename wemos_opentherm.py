#%%
import copy
import numpy as np
from build123d import *
from math import radians, tan
from ocp_vscode import show
#%%
d1_step = import_step("WeMos_D1_Mini_ESP8266_v8.step")

def find_by_label(shape: Compound, target: str):
    """Return a list of subshapes (Compounds, Solids, etc.) with a matching label"""
    matches = []
    if shape.label == target:
        matches.append(shape)
    if hasattr(shape, "children"):
        for child in shape.children:
            matches.extend(find_by_label(child, target))
    return matches

d1_main = find_by_label(d1_step, "COMPOUND")[0]
d1_main.label = "D1 Main"
d1_main.color = (0.8, 0.8, 0.8)
d1_bbox = d1_main.bounding_box()
d1_size = d1_bbox.size

d1_usb = find_by_label(d1_step, "USB")[0]
d1_usb.label = "USB Port"
d1_usb.color = (0.8, 0.8, 0.2)
d1_usb_bbox = d1_usb.bounding_box()
d1_usb_size = d1_usb_bbox.size

d1_usb_offset = d1_usb_bbox.center() - d1_bbox.center()

d1_switch = find_by_label(d1_step, "Switch")[0]
d1_switch.label = "Switch"
d1_switch.color = (0.8, 0.2, 0.2)
d1_switch_bbox = d1_switch.bounding_box()
d1_switch_size = d1_switch_bbox.size

#%%
d1_switch_offset = d1_switch_bbox.center() - d1_bbox.center()

d1_full = Compound(children=[d1_main, d1_usb, d1_switch], label="d1_full")

d1_pcb_measured_thinkness = 1.4
hat_thickness = 2.0
hat_distance_from_d1 = 10.5 + d1_pcb_measured_thinkness

screw_pos_back = 4.5
screw_pos_side = 10

with BuildPart() as hat_board:
    with BuildSketch(Plane.XY.offset(hat_distance_from_d1)):
        Rectangle(d1_bbox.size.X, d1_bbox.size.Y)
    extrude(amount=hat_thickness)

    hat_bbox = hat_board.part.bounding_box()
    screw1 = Vector(hat_bbox.max.X - screw_pos_side, hat_bbox.max.Y - screw_pos_back, hat_bbox.max.Z)
    screw2 = screw1 + Vector(-3.5, 0, 0)
    RigidJoint(label="screw1", joint_location=Location(screw1))
    RigidJoint(label="screw2", joint_location=Location(screw2))
hat_board.part.label = "OpenTherm Hat Board"
hat_board.part.color = (0.8, 0.6, 0.6)

with BuildPart() as test:
    with BuildSketch(Plane.XY):
        Circle(1)
    extrude(amount=8)
    RigidJoint(label="test_joint")

test1 = copy.copy(test.part)
hat_board.part.joints["screw1"].connect_to(test1.joints["test_joint"])

test2 = copy.copy(test.part)
hat_board.part.joints["screw2"].connect_to(test2.joints["test_joint"])

hat = Compound(children=[hat_board.part, test1, test2], label="OpenTherm Hat")

show(d1_full, hat)

#%%
bbox = d1_full.bounding_box()

clearance = 0.4
wall_thickness = 1.2
extra_height = 5  # mm above board
bottom_space = 3  # mm below usb

# Outer box
outer_size = (
    bbox.size.X + 2 * (clearance + wall_thickness),
    bbox.size.Y + 2 * (clearance + wall_thickness),
    bbox.size.Z + extra_height + wall_thickness + bottom_space,  # includes bottom wall
)

outer_pos = (
    bbox.min.X - (clearance + wall_thickness),
    bbox.min.Y - (clearance + wall_thickness),
    bbox.min.Z - wall_thickness - bottom_space,
)

fin_length = 25
fin_width = 1.2
fin_height = d1_bbox.min.Z - d1_usb_bbox.min.Z + bottom_space
fin_position_x = d1_size.X / 2 - 3.5
fin_position_y = d1_size.Y / 2 + clearance

usb_cutout_width = 10.8
usb_cutout_height = 8

with BuildPart() as housing:
    with BuildSketch(Plane.XY.offset(outer_pos[2])):
        Rectangle(outer_size[0], outer_size[1], align=(Align.CENTER, Align.CENTER))
    extrude(amount=outer_size[2])

    # Pick the top face
    top_face = housing.faces().sort_by(Axis.Z)[-1]
    bottom_face = housing.faces().sort_by(Axis.Z)[0]
    back_face = housing.faces().sort_by(Axis.Y)[-1]
    right_face = housing.faces().sort_by(Axis.X)[-1]

    # Hollow it out with open top
    offset(amount=-wall_thickness, openings=[top_face])

    # Add fins
    with BuildSketch(Plane(bottom_face).reverse().offset(wall_thickness)) as fins_sketch:
        with Locations([(fin_position_x, -fin_position_y), (-fin_position_x, -fin_position_y)]):
            Rectangle(fin_width, fin_length, align=(Align.CENTER, Align.MIN))
    extrude(amount=fin_height, mode=Mode.ADD)

    # Fillet vertical edges
    fillet(housing.edges().filter_by(Axis.Z), 0.4)

    back_face_z_shift = back_face.bounding_box().size.Z/2

    # Add cutout for USB
    with BuildSketch(Plane(back_face).reverse().move(Location((0,0,wall_thickness-back_face_z_shift)))):
        r = Rectangle(usb_cutout_width, usb_cutout_height, align=(Align.CENTER, Align.MIN))
        fillet(r.vertices(), 1)
    extrude(amount=wall_thickness, mode=Mode.SUBTRACT)

    # Add cutout for switch
    switch_cutout_width = d1_switch_size.Y
    switch_cutout_height = d1_switch_size.Z
    with BuildSketch(Plane(right_face).reverse().move(Location((0, d1_switch_bbox.center().Y, d1_switch_bbox.center().Z)))):
        r = Rectangle(switch_cutout_width, switch_cutout_height)
        fillet(r.vertices(), 1)
    extrude(amount=wall_thickness, mode=Mode.SUBTRACT)

housing.part.label = "Housing"
housing.part.color = (0.6, 0.6, 1)

all = Compound(children=[
        d1_full, hat, housing.part
    ], label="All")

show(all,
    clip_normal_1=(0, -1, 0), clip_slider_1=14.1,
    clip_normal_2=(0, 0, 1), clip_slider_2=6.99)
#%%
latch_angle = 30
latch_angle2 = 90-latch_angle
latch_thickness = 1.2
latch_length = 15
latch_depth = 0.8
latch_width = 5

with BuildPart() as latch:

    with BuildSketch() as latch_sketch:
        r = Rectangle(latch_length, latch_thickness, align=(Align.MIN, Align.MAX))
        Triangle(a=latch_depth*2/tan(radians(latch_angle)), B=latch_angle, C=latch_angle, align=(Align.MIN, Align.MIN))

        chamfer(r.vertices().group_by(Axis.X)[-1].sort_by(Axis.Y)[0], length=latch_thickness/tan(radians(latch_angle)), angle=latch_angle)
        chamfer(r.vertices().group_by(Axis.X)[0].sort_by(Axis.Y)[0], length=latch_thickness, angle=latch_angle2)

    extrude(amount=latch_width)

    # Joint should be placed inside the box on it's rim
    sel = latch.part.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2].vertices()
    middle = np.array(tuple(sel[0]+sel[1]))/2
    middle[1] = 0 # reset Y to 0
    # TODO how to set rotation of the joint? I guess (0, -1, 0) is the right direction
    RigidJoint(label="latch_joint", joint_location=Location(middle))

show(latch.part, Vertex(middle))
# %%

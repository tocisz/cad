#%% Imports
import copy
from curses.textpad import rectangle
from dis import Positions
from matplotlib.transforms import offset_copy
import numpy as np
from build123d import *
from math import radians, tan
from ocp_vscode import show

#%% Load WeMos D1 Mini STEP file
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
d1_main.color = Color(0.8, 0.8, 0.8)

d1_usb = find_by_label(d1_step, "USB")[0]
d1_usb.label = "USB Port"
d1_usb.color = Color(0.8, 0.8, 0.2)

d1_switch = find_by_label(d1_step, "Switch")[0]
d1_switch.label = "Switch"
d1_switch.color = Color(0.8, 0.2, 0.2)

#%% Screw mock
screw_diameter = 2.5
with BuildPart() as screw_mock:
    screw_length = 8
    with BuildSketch(Plane.XY):
        Circle(screw_diameter/2)
    extrude(amount=screw_length)
    RigidJoint(label="joint")

show(screw_mock.part)

#%% to92 mock
with BuildPart() as to92_mock:
    width = 3.3
    length = 4.4
    height = 4.3
    with BuildSketch(Plane.XY) as sk:
        r = Rectangle(width, height)
        fillet(r.vertices().group_by(Axis.X)[-1], height/2-0.001)
    extrude(amount=height)
    RigidJoint(label="joint")

show(to92_mock.part, sk.sketch_local)

#%% Upper hat board mock
d1_full = Compound(children=[d1_main, d1_usb, d1_switch], label="Wemos D1")

d1_pcb_measured_thinkness = 1.4
hat_thickness = 2.0
hat_distance_from_d1 = 10.5 + d1_pcb_measured_thinkness

screw_pos_back = 4.5
screw_pos_side = 10

with BuildPart() as hat_board:
    with BuildSketch(Plane.XY.offset(hat_distance_from_d1)):
        Rectangle(d1_main.bounding_box().size.X, d1_main.bounding_box().size.Y)
    extrude(amount=hat_thickness)

    hat_bbox = hat_board.part.bounding_box()
    screw1 = Vector(hat_bbox.max.X - screw_pos_side, hat_bbox.max.Y - screw_pos_back, hat_bbox.max.Z)
    screw2 = screw1 + Vector(-3.5, 0, 0)
    RigidJoint(label="screw1", joint_location=Location(screw1))
    RigidJoint(label="screw2", joint_location=Location(screw2))
    bs18b20_location = Location((hat_bbox.max.X-4, hat_bbox.max.Y-3, hat_bbox.max.Z), Axis.Z.direction, 90)
    RigidJoint(label="bs18b20", joint_location=bs18b20_location)
hat_board.part.label = "OpenTherm Hat Board"
hat_board.part.color = Color(0.8, 0.6, 0.6)

screw_mocks = {i: copy.copy(screw_mock.part) for i in range(1,3)}
for i, mock in screw_mocks.items():
    mock.label = f"Screw {i}"
    mock.color = hat_board.part.color
    hat_board.part.joints[f"screw{i}"].connect_to(mock.joints["joint"])

bs18b20 = copy.copy(to92_mock.part)
bs18b20.label = "BS18B20"
bs18b20.color = hat_board.part.color
hat_board.part.joints["bs18b20"].connect_to(bs18b20.joints["joint"])

hat = Compound(children=[hat_board.part, bs18b20] + list(screw_mocks.values()), label="OpenTherm Hat")

show(d1_full, hat)

#%% Latch part
latch_angle = 30
latch_angle2 = 90-latch_angle
latch_thickness = 0.8
latch_length = 8
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
    sel = latch.part.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2]
    middle = np.array(sel.location_at(0.5).position.to_tuple())
    middle[1] = 0 # reset Y to 0
    joint = Location(middle, Axis.Y.direction, -90)
    RigidJoint(label="latch_joint", joint_location=joint)

show(latch.part)
#%% Sketches for lower part of the housing
bbox = d1_full.bounding_box()

clearance = 0.4
wall_thickness = 1.2
extra_height = 2.5  # mm above board
bottom_space = 3  # mm below usb

fin_length = 25
fin_width = 1.2
fin_height = d1_main.bounding_box().min.Z - d1_usb.bounding_box().min.Z + bottom_space
fin_position_x = d1_main.bounding_box().size.X / 2 - 3.5
fin_position_y = d1_main.bounding_box().size.Y / 2 + clearance

usb_cutout_width = 10.8
usb_cutout_height = 8

bottom_plane = Plane.XY.offset(bbox.min.Z - bottom_space)
middle_plane = bottom_plane.offset(fin_height)
with BuildSketch(bottom_plane) as hat_bottom_inner:
    Rectangle(bbox.size.X, bbox.size.Y)
    offset(amount=clearance)
with BuildSketch(bottom_plane) as hat_bottom_outer:
    Rectangle(bbox.size.X, bbox.size.Y)
    offset(amount=clearance+wall_thickness)
with BuildSketch(bottom_plane) as hat_bottom:
    add(hat_bottom_outer)
    add(hat_bottom_inner, mode=Mode.SUBTRACT)
    with Locations([(fin_position_x, -fin_position_y), (-fin_position_x, -fin_position_y)]):
        r = Rectangle(fin_width, fin_length, align=(Align.CENTER, Align.MIN))
        fillet(r.vertices(), clearance)
with BuildSketch(middle_plane) as hat_middle:
    add(hat_bottom_outer)
    add(hat_bottom_inner, mode=Mode.SUBTRACT)

show(d1_full, hat_bottom.sketch, hat_middle.sketch)

#%% Lower part of the housing
middle_extrude_height = d1_main.bounding_box().max.Z-middle_plane.location.position.Z+extra_height
with BuildPart() as housing:
    extrude(hat_bottom_outer.sketch, amount=-wall_thickness)
    extrude(hat_bottom.sketch, amount=fin_height)
    extrude(hat_middle.sketch, amount=middle_extrude_height)

    # Add cutout for USB
    back_face = housing.faces().sort_by(Axis.Y)[-1]
    back_face_z_shift = back_face.bounding_box().size.Z/2
    with BuildSketch(Plane(back_face).reverse().move(Location((0,0,wall_thickness-back_face_z_shift)))):
        r = Rectangle(usb_cutout_width, usb_cutout_height, align=(Align.CENTER, Align.MIN))
        fillet(r.vertices(), 1)
    extrude(amount=wall_thickness, mode=Mode.SUBTRACT)

    # Add cutout for switch
    right_face = housing.faces().sort_by(Axis.X)[-1]
    switch_cutout_width = d1_switch.bounding_box().size.Y
    switch_cutout_height = d1_switch.bounding_box().size.Z
    switch_cutout_z_shift = 0.95 # why it's needed?
    with BuildSketch(Plane(right_face).reverse().move(Location((0, d1_switch.bounding_box().center().Y, d1_switch.bounding_box().center().Z+switch_cutout_z_shift)))):
        r = Rectangle(switch_cutout_width, switch_cutout_height)
        fillet(r.vertices(), 1)
    extrude(amount=wall_thickness, mode=Mode.SUBTRACT)

    sel = housing.part.faces().sort_by(Axis.Z)[-1]
    sel = sel.edges().filter_by(Axis.X).sort_by(Axis.Y)
    loc1 = Location(sel[1].location_at(0.5).position, Axis.Z.direction, 180)
    RigidJoint(label="housing_joint_1", joint_location=loc1)
    loc2 = Location(sel[-2].location_at(0.5).position)
    RigidJoint(label="housing_joint_2", joint_location=loc2)

housing.part.label = "Housing"
housing.part.color = Color(0.6, 0.6, 1)

latches = {i: copy.copy(latch.part) for i in range(1,3)}
for i, lt in latches.items():
    lt.label = f"Latch {i}"
    lt.color = housing.part.color
    housing.part.joints[f"housing_joint_{i}"].connect_to(lt.joints["latch_joint"])

housing_assembly = Compound(children=[housing.part] + list(latches.values()), label="Housing Assembly")

show(d1_full, hat, housing_assembly)

#%% Sketches for upper part of the housing
sketch_plane = Plane.XY.offset(hat.bounding_box().max.Z+clearance)
with BuildSketch(sketch_plane) as cutouts:
    with Locations(hat_board.part.joints["screw1"].location,
                hat_board.part.joints["screw2"].location):
        Circle(screw_diameter/2+clearance)

with BuildSketch(sketch_plane) as upper_housing_outline:
    r1 = Rectangle(d1_main.bounding_box().size.X + 2*(clearance + wall_thickness),
                   d1_main.bounding_box().size.Y + 2*(clearance + wall_thickness))
    r1_corner = r1.vertices().group_by(Axis.X)[-1].sort_by(Axis.Y)[-1]
    corner_cut_x = r1_corner.X - bs18b20.bounding_box().min.X + clearance
    corner_cut_y = r1_corner.Y - bs18b20.bounding_box().min.Y + clearance
    
    with Locations(r1_corner):
        Rectangle(corner_cut_x, corner_cut_y, mode=Mode.SUBTRACT,
                  align=(Align.MAX, Align.MAX))
    middle_vertex = upper_housing_outline.vertices().group_by(Axis.X)[1].sort_by(Axis.Y)[0]
    fillet(middle_vertex, clearance)
    fillet(upper_housing_outline.vertices() - middle_vertex, wall_thickness+clearance)

with BuildSketch(sketch_plane) as upper_housing_wall:
    add(upper_housing_outline.sketch)
    offset(amount=-wall_thickness, mode=Mode.SUBTRACT)

extrude_distance = sketch_plane.location.position.Z - hat_board.part.bounding_box().max.Z - clearance
sketch_plane_middle = sketch_plane.offset(-extrude_distance)
with BuildSketch(sketch_plane_middle) as upper_housing_middle:
    add(upper_housing_wall)
    with Locations(r1_corner):
        Rectangle(corner_cut_x+wall_thickness+clearance,
                  corner_cut_y+wall_thickness+clearance,
                  mode=Mode.SUBTRACT, align=(Align.MAX, Align.MAX))

show(d1_full, hat, housing_assembly,
     upper_housing_outline.sketch, cutouts.sketch,
     upper_housing_wall.sketch, upper_housing_middle.sketch)
#%% Upper part of the housing
extrude_distance2 = sketch_plane_middle.location.position.Z - housing.part.bounding_box().max.Z
with BuildPart() as upper_housing:
    with BuildSketch(sketch_plane) as sketch1:
        add(upper_housing_outline.sketch)
        make_hull(cutouts.sketch.edges(), mode=Mode.SUBTRACT)
    extrude(sketch1.sketch, amount=wall_thickness)
    extrude(upper_housing_wall.sketch, amount=-extrude_distance)
    extrude(upper_housing_middle.sketch, amount=-extrude_distance2)
    for lt in latches.values():
        offset(lt, amount=0.2, mode=Mode.SUBTRACT)

    back_face = upper_housing.faces().sort_by(Axis.Y)[-1]
    back_plane = Plane(back_face)
    with BuildSketch(back_plane) as cutout_for_wires:
        # origin set to upper right corner
        s1bbMin = back_plane.to_local_coords(screw_mocks[2].bounding_box().min)
        s1bbMax = back_plane.to_local_coords(screw_mocks[1].bounding_box().max)
        cut_height = 4.5
        with Locations(s1bbMin):
            rect_size = s1bbMax - s1bbMin
            rect = Rectangle(rect_size.X, cut_height, align=(Align.MIN, Align.MAX))
        fillet(cutout_for_wires.vertices(), 1)
    extrude(cutout_for_wires.sketch, amount=-wall_thickness, mode=Mode.SUBTRACT)

upper_housing.part.label = "Upper Housing"
upper_housing.part.color = Color(0.6, 0.9, 1)

all = Compound(children=[
        d1_full, hat, housing_assembly, upper_housing.part
    ], label="All")

show(all)
#%% Housing corner
upper_plane = middle_plane.offset(middle_extrude_height)
with BuildSketch(upper_plane) as upper_sketch:
    add(hat_middle.sketch)
    with Locations(r1_corner):
        corner_cut_x1 = r1_corner.X - bs18b20.bounding_box().min.X + wall_thickness + clearance
        corner_cut_y1 = r1_corner.Y - bs18b20.bounding_box().min.Y + wall_thickness + clearance
        Rectangle(corner_cut_x1, corner_cut_y1, mode=Mode.INTERSECT,
                    align=(Align.MAX, Align.MAX))
with BuildPart() as housing_corner:
    extrude(upper_sketch.sketch, amount=extrude_distance2-2*clearance)
housing_corner.part.label = "Housing corner"
housing_corner.part.color = housing.part.color

housing_assembly = Compound(children=[housing.part, housing_corner.part] + list(latches.values()),
                            label="Housing Assembly")

all = Compound(children=[
        d1_full, hat, housing_assembly, upper_housing.part
    ], label="All")

show(all)
#%%
export_step(all, "wemos_opentherm_assembly.step")
# %%

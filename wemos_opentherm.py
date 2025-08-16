#%%
from build123d import *
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

d1_switch_offset = d1_switch_bbox.center() - d1_bbox.center()

d1_full = Compound(children=[d1_main, d1_usb, d1_switch], label="d1_full")

show(d1_full)

#%%
bbox = d1_full.bounding_box()

clearance = 0.8
wall_thickness = 1.2
extra_height = 10  # mm above board
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

    # Hollow it out with open top
    offset(amount=-wall_thickness, openings=[top_face])

    # Add fins
    with BuildSketch(Plane(bottom_face).reverse().offset(wall_thickness)) as fins_sketch:
        with Locations([(fin_position_x, -fin_position_y), (-fin_position_x, -fin_position_y)]):
            Rectangle(fin_width, fin_length, align=(Align.CENTER, Align.MIN))
    extrude(amount=fin_height, mode=Mode.ADD)

    back_face_height = back_face.bounding_box().size.Z/2

    # Add cutout for USB
    with BuildSketch(Plane(back_face).reverse().move(Location((0,0,wall_thickness-back_face_height)))) as usb_sketch:
        Rectangle(usb_cutout_width, usb_cutout_height, align=(Align.CENTER, Align.MIN))
    extrude(amount=wall_thickness, mode=Mode.SUBTRACT)

housing.part.label = "Housing"
housing.part.color = (0.6, 0.6, 1)

all = Compound(children=[d1_full, housing.part], label="All Components")

show(all,
    clip_normal_1=(0, -1, 0), clip_slider_1=14.1,
    clip_normal_2=(0, 0, 1), clip_slider_2=6.99)

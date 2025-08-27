#%% Imports
from build123d import BuildSketch, RegularPolygon, PolarLocations, add
from ocp_vscode import show
from math import sin, cos, radians
import numpy as np
#%%
def hexflake(spacing = 6, shape = RegularPolygon(3, 6, rotation=30), level = 3):
    with BuildSketch() as hex:
        if level == 0:
            add(shape)
        else:
            s = hexflake(spacing, shape, level-1)
            add(s)
            with PolarLocations(spacing*3**(level-1), 6):
                add(s)
    return hex.sketch

def hexflake2(spacing = 6, shape = RegularPolygon(3, 6, rotation=30), level = 4):
    base = spacing*np.array([
        [cos(radians(60)), sin(radians(60))],
        [cos(radians(60)), -sin(radians(60))]
    ])
    # Translation offsets chosen to visually align recursive hexflake copies.
    offsets = np.array([
        [0, 0],
        [-1, 0],
        [-1, -4],
        [-8, -9],
    ])
    with BuildSketch() as hex:
        if level == 0:
            add(shape)
        else:
            s = hexflake2(spacing, shape, level-1)
            add(s)

            s1 = s.translate(tuple(np.inner(offsets[level-1], base.T)))
            with PolarLocations(spacing*3**(level-1), 6):
                add(s1)
    return hex.sketch

# hex = hexflake2()
# show(hex)
#%%
# from build123d import ExportSVG, Color
# hex = hexflake()
# exporter = ExportSVG()
# exporter.add_layer("flake", fill_color=Color(0.5,0.5,0.5))
# exporter.add_shape(hex, layer="flake")
# exporter.write("hexflake.svg")

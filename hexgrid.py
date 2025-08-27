#%% Imports
from build123d import BuildSketch, RegularPolygon, PolarLocations, add
from ocp_vscode import show
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

#%%
# from build123d import ExportSVG, Color
# hex = hexflake()
# exporter = ExportSVG()
# exporter.add_layer("flake", fill_color=Color(0.5,0.5,0.5))
# exporter.add_shape(hex, layer="flake")
# exporter.write("hexflake.svg")

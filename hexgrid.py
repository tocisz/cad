#%% Imports
from build123d import BuildSketch, RegularPolygon, PolarLocations, add
from ocp_vscode import show
#%%
def hexflake(spacing = 6, shape = RegularPolygon(3, 6, rotation=30), level = 3):
    with BuildSketch() as hex:
        if level == 0:
            add(shape)
        else:
            r1 = hexflake(spacing, shape, level-1)
            add(r1)
            sp = pow(3,level-1)*spacing
            with PolarLocations(sp, 6):
                add(r1)
    return hex.sketch


show(hexflake())
# #%%
# exporter = ExportSVG()
# exporter.add_layer("flake", fill_color=Color(0.5,0.5,0.5))
# exporter.add_shape(hex.sketch, layer="flake")
# exporter.write("hexflake.svg")

# %%
from build123d import *
from ocp_vscode import show
# %%
monotile_svg = import_svg("monotile-1.000-1.000-0.000.svg")
svg_height = monotile_svg.face().bounding_box().size.Y
# %%
monotile_height = 169*MM
blade = 1.2*MM
fugue = 5*MM # czy to nie za duzo?
rim = 10*MM

with BuildSketch() as monotile:
    f = add(monotile_svg.face())
    scale(f, by=monotile_height/svg_height)

with BuildSketch() as inside:
    add(monotile.face())
    offset(amount=-fugue/2)

with BuildSketch() as plus_blade:
    add(inside.face())
    offset(amount=blade)

with BuildSketch() as outside:
    add(plus_blade)
    offset(amount=rim)
    add(plus_blade, mode=Mode.SUBTRACT)
    
show(inside.sketch, outside.sketch)
# %%
exporter = ExportSVG()
exporter.add_layer("Inside")
exporter.add_layer("Outside")
exporter.add_shape(inside.sketch, layer="Inside")
exporter.add_shape(outside.sketch, layer="Outside")
exporter.write("spectre_sketches.svg")

# %%
area_cm2 = monotile.face().area / 100
one_m2_in_cm2 = 100**2*1.05 # assume 5% shrinkage
tiles_in_m2 = one_m2_in_cm2 / area_cm2
tiles_in_m2
# %%
extrude_amount = 10*MM
with BuildPart() as inside_part:
    add(inside.sketch)
    extrude(amount=extrude_amount)
inside_part.part.label = "inside"

with BuildPart() as outside_part:
    add(outside.sketch)
    extrude(amount=extrude_amount)
outside_part.part.label = "outside"

assembly = Compound(label="together", children=[outside_part.part, inside_part.part])
show(assembly)

#%%
export_step(assembly, "spectre.step")
export_brep(assembly, "spectre.brep")
export_stl(assembly, "spectre.stl")
# %%

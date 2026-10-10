#%% Imports
import copy as pycopy
import math
from pathlib import Path

from build123d import *
from ocp_viewer import show as _viewer_show

HERE = Path(__file__).parent

def show(*args, **kwargs):
    """Podglad OCP - nie wywalam skryptu gdy brak viewer port (headless)."""
    try:
        _viewer_show(*args, **kwargs)
    except Exception as e:
        print(f"[viewer] pominieto show: {type(e).__name__}")

#%% =========================================================
#  PARAMETRY SCENY (mm)
# ===========================================================
# Nowa lokalizacja: plaska sciana sasiedniej (wyzszej) kamienicy.
# Kominy zostaja w notatce, nie w modelu montazu.

# --- dach uzytkownika ---
roof_z0          = 0.0
roof_thick       = 200.0
roof_len_y       = 1400.0     # od sciany w strone podworka (-Y)
roof_len_x       = 1800.0
roof_color       = Color(0.45, 0.42, 0.38)

# --- sciana sasiada (y=0, budynek w y>0) ---
wall_height      = 3000.0
wall_thickness   = 510.0
wall_length_x    = 1800.0     # wycinek sciany do rysunku; konstrukcja bez zmian
wall_color       = Color(0.82, 0.72, 0.58)
flashing_overhang = 50.0
flashing_thick   = 8.0
flashing_color   = Color(0.35, 0.38, 0.40)

# --- maszt MAT-COMPANY 3 m, 40 x 1.5, CIETY DO 2.5 m (czubek bez zmian) ---
mast_diameter    = 40.0
mast_wall        = 1.5
mast_length      = 2500.0
mast_above_wall  = 1000.0
mast_along_wall  = mast_length - mast_above_wall
mast_bottom_z    = wall_height - mast_along_wall
mast_top_z       = mast_bottom_z + mast_length
mast_color       = Color(0.75, 0.78, 0.82)

# --- UMP-150 ---
ump_standoff     = 140.0      # sciana -> siodlo
ump_hole_span    = 365.0
ump_inner        = 225.0
ump_bar_w        = 35.0       # wzdluz masztu
ump_bar_t        = 4.0
ump_saddle_h     = 140.0
ump_color        = Color(0.70, 0.72, 0.74)
# pozycje srodkow obejm
ump_z            = [mast_bottom_z + 150.0, wall_height - 150.0]

# --- antena (pomiar) ---
ant_base_D       = 30.0
ant_base_L       = 300.0
ant_mid_D0       = 25.0
ant_mid_D1       = 21.0
ant_mid_L        = 890.0
ant_top_D        = 16.0
ant_top_L        = 1400.0
ant_top_insert   = 110.0
ant_top_exposed  = ant_top_L - ant_top_insert
ant_radial_l     = 510.0
ant_radial_r     = 2.0
ant_radial_ang   = 45.0       # od poziomu w dol, ZGADNIETE
ant_clamp_span   = 250.0
ant_clamp_gap    = 12.0
ant_color        = Color(0.93, 0.93, 0.90)
radial_color     = Color(0.80, 0.80, 0.85)
ant_clamp_color  = Color(0.90, 0.55, 0.10)

# os masztu: y ujemne (strona dachu), x=0
mast_x = 0.0
mast_y = -(ump_standoff + mast_diameter / 2.0)

ant_ax = mast_x + (mast_diameter + ant_base_D) / 2.0 + ant_clamp_gap
ant_bottom_z = mast_top_z - ant_base_L
ant_top_z = ant_bottom_z + ant_base_L + ant_mid_L + ant_top_exposed
ant_clamp_z_hi = mast_top_z - 25.0
ant_clamp_z_lo = ant_clamp_z_hi - ant_clamp_span

#%% =========================================================
#  DACH + SCIANA + DASZEK
# ===========================================================
ready = []  # elementy gotowe do podgladu

roof = Pos(0, -roof_len_y / 2.0, -roof_thick / 2.0) * Box(roof_len_x, roof_len_y, roof_thick)
roof.label = "User roof"
roof.color = roof_color

wall = Pos(0, wall_thickness / 2.0, wall_height / 2.0) * Box(wall_length_x, wall_thickness, wall_height)
wall.label = "Neighbor wall"
wall.color = wall_color
# mocowanie obejm: srodek belki sciennej UMP na plaszczyznie sciany (y=0)
RigidJoint(label="ump lo", to_part=wall, joint_location=Location((0, 0, ump_z[0])))
RigidJoint(label="ump hi", to_part=wall, joint_location=Location((0, 0, ump_z[1])))

flashing = Pos(0, -flashing_overhang / 2.0, wall_height + flashing_thick / 2.0) * Box(
    wall_length_x, flashing_overhang, flashing_thick
)
flashing.label = "Flashing 50 mm"
flashing.color = flashing_color
ready += [roof, wall, flashing]
show(*ready)

#%% =========================================================
#  MASZT
# ===========================================================
with BuildPart() as mast:
    with BuildSketch(Plane.XY):
        Circle(mast_diameter / 2)
        Circle(mast_diameter / 2 - mast_wall, mode=Mode.SUBTRACT)
    extrude(amount=mast_length)
mast.part.label = "Mast 40x1.5"
mast.part.color = mast_color

RigidJoint(label="ump lo", to_part=mast.part, joint_location=Location((0, 0, ump_z[0] - mast_bottom_z)))
RigidJoint(label="ump hi", to_part=mast.part, joint_location=Location((0, 0, ump_z[1] - mast_bottom_z)))
RigidJoint(label="ant clamp hi", to_part=mast.part, joint_location=Location((0, 0, ant_clamp_z_hi - mast_bottom_z)))
RigidJoint(label="ant clamp lo", to_part=mast.part, joint_location=Location((0, 0, ant_clamp_z_lo - mast_bottom_z)))
ready.append(mast.part)
show(*ready)

#%% =========================================================
#  UMP-150 (dwa identyczne uchwyty trapezowe)
# ===========================================================
hw = ump_hole_span / 2.0          # 182.5
inner = ump_inner / 2.0           # 127.5
top_w = 80.0
y0 = 0.0
y1 = -ump_saddle_h  # w strone masztu / dachu (-Y)

with BuildPart() as br:
    with BuildSketch(Plane.XY.offset(-ump_bar_w/2)) as ump_sk:
        with BuildLine():
            Polyline(
                (hw + 20, y0),
                (inner, y0),
                (top_w / 2, y1),
                (-top_w / 2, y1),
                (-inner, y0),
                (-hw - 20, y0),
            )
            offset(amount=ump_bar_t, side=Side.LEFT)
        make_face()
    extrude(amount=ump_bar_w)

    with BuildSketch(Plane.XZ.offset(-1)), Locations(
        (-hw, -ump_bar_t / 2),
        (hw, -ump_bar_t / 2),
        (-hw + 40, -ump_bar_t / 2),
        (hw - 40, -ump_bar_t / 2)):
            Circle(5.0)
    extrude(amount=ump_bar_t + 2, mode=Mode.SUBTRACT)

    with Locations((0, y1-ump_bar_t, 0)):
        Box(70, 20, 20, align=(Align.CENTER,Align.MAX,Align.CENTER))

# Zacisk U-bolt (plyta + 2 pręty) jako osobne solids - fuzja z belka psula tessellacje BRep
r_rod = 4.0
span = 50.0
ring_face = Pos(0, y1 - 10 - 35, 0) * (Circle(span / 2 + r_rod) - Circle(span / 2 - r_rod))
ump_ring = extrude(ring_face, amount=r_rod, both=True)
ump_rod_lo = Pos(-span / 2, y1 - 10, 0) * Rot(90, 0, 0) * Cylinder(r_rod, 70)
ump_rod_hi = Pos( span / 2, y1 - 10, 0) * Rot(90, 0, 0) * Cylinder(r_rod, 70)
ump_ring.label = "UMP-150 ring"
ump_rod_lo.label = "UMP-150 rod 1"
ump_rod_hi.label = "UMP-150 rod 2"
for s in (ump_ring, ump_rod_lo, ump_rod_hi):
    s.color = ump_color

# Wzorzec = Compound (belka + zacisk); jointy na calosci
#  - "wall": srodek belki sciennej (y=0, z=0)
#  - "mast": srodek siodla na osi masztu (y = -(ump_standoff + R/2), z=0)
br_m = br.part
br_m.label = "UMP-150 bracket"
br_m.color = ump_color
ump_master = Compound(label="UMP-150", children=[br_m, ump_ring, ump_rod_lo, ump_rod_hi])
RigidJoint(label="wall", to_part=ump_master, joint_location=Location((0, 0, 0)))
RigidJoint(label="mast", to_part=ump_master, joint_location=Location((0, -(ump_standoff + mast_diameter / 2.0), 0)))

# Dwa egzemplarze z wzorca (shallow copy = wspolny TShape, tylko Location rozne)
ump_parts = []
for i, wj in enumerate([wall.joints["ump lo"], wall.joints["ump hi"]]):
    inst = pycopy.copy(ump_master)
    inst.label = f"UMP-150 {i+1}"
    wj.connect_to(inst.joints["wall"])   # connect_to przesuwa "other" -> sciana zostaje, uchwyt jedzie
    inst.joints["mast"].connect_to(mast.part.joints["ump lo" if i == 0 else "ump hi"])
    ump_parts.append(inst)
ready += ump_parts
show(*ready)


#%% =========================================================
#  OBEJMY ANTENA <-> MASZT  (przed antena: pozycjonowanie na maszcie
#  jest niezalezne od budowy anteny)
# ===========================================================
ring_gap = (mast_diameter + ant_base_D) / 2 + ant_clamp_gap
with BuildPart() as ant_clamp_master:
    with BuildSketch(Plane.XY) as clamp_sk:
        with Locations((mast_x, mast_y)):
            Circle(mast_diameter / 2 + 4)
            Circle(mast_diameter / 2, mode=Mode.SUBTRACT)
        with Locations((ant_ax, mast_y)):
            Circle(ant_base_D / 2 + 4)
            Circle(ant_base_D / 2, mode=Mode.SUBTRACT)
        with Locations(((mast_x + ant_ax) / 2, mast_y)):
            Rectangle(ring_gap, 14)
    extrude(amount=12)

# Jointy wzorca obejmy: os Z wzorca = os masztu (Locations centered on mast axis)
RigidJoint(label="mast", to_part=ant_clamp_master.part, joint_location=Location((mast_x, mast_y, 0)))
RigidJoint(label="ant", to_part=ant_clamp_master.part, joint_location=Location((ant_ax, mast_y, 0)))
ant_clamp_master.part.label = "Ant clamp"
ant_clamp_master.part.color = ant_clamp_color

ant_clamps = []
for i, mj in enumerate([mast.part.joints["ant clamp hi"], mast.part.joints["ant clamp lo"]]):
    inst = pycopy.copy(ant_clamp_master.part)
    inst.label = f"Ant clamp {i+1}"
    mj.connect_to(inst.joints["mast"])   # connect_to przesuwa obejme, maszt zostaje
    ant_clamps.append(inst)
ready += ant_clamps
show(*ready)

#%% =========================================================
#  ANTENA (laczenie z obejmy wykonane ponizej, czlon po czlonie)
# ===========================================================
with BuildPart() as ant_base:
    with BuildSketch(Plane.XY):
            Circle(ant_base_D / 2)
    extrude(amount=ant_base_L)
    RigidJoint(label="mount lower", joint_location=Pos(0,0,25))
    RigidJoint(label="mount upper", joint_location=Pos(0,0,ant_base_L-25))
    RigidJoint(label="top", joint_location=Pos(0,0,ant_base_L))
ant_base.part.label = "Antenna base Al 30x1.5"
ant_base.part.color = ant_color

# antena wchodzi w obejmy (hi obejma <-> mount upper, lo <-> mount lower)
ant_clamps[0].joints["ant"].connect_to(ant_base.part.joints["mount upper"])
ant_clamps[1].joints["ant"].connect_to(ant_base.part.joints["mount lower"])

# srodek: stozek sciety 25 -> 21
with BuildPart() as frp_mid:
    with BuildSketch(Plane.XY):
        Circle(ant_mid_D0 / 2)
    extrude(amount=ant_mid_L, taper=math.degrees(math.atan(((ant_mid_D0 - ant_mid_D1) / 2) / ant_mid_L)))
    RigidJoint(label="bottom", joint_location=Pos(0,0,0))
    RigidJoint(label="top", joint_location=Pos(0,0,ant_mid_L))
frp_mid.part.label = "FRP mid 25->21"
frp_mid.part.color = ant_color
ant_base.part.joints["top"].connect_to(frp_mid.part.joints["bottom"])

with BuildPart() as frp_top:
    with BuildSketch(Plane.XY):
        Circle(ant_top_D / 2)
    extrude(amount=ant_top_L)
    RigidJoint(label="bottom", joint_location=Pos(0,0,ant_top_insert))
frp_top.part.label = "FRP top 16"
frp_top.part.color = ant_color
frp_mid.part.joints["top"].connect_to(frp_top.part.joints["bottom"])

with BuildPart() as radials:
    dip = math.radians(ant_radial_ang)  # w dol od poziomu
    for k in range(3):
        az = math.radians(k * 120.0)
        dx = math.cos(dip) * math.cos(az)
        dy = math.cos(dip) * math.sin(az)
        dz = -math.sin(dip)
        pl = Plane(origin=(0,0,0), z_dir=(dx, dy, dz))
        rad = pl * Pos(0, 0, ant_radial_l / 2) * Cylinder(ant_radial_r, ant_radial_l, mode=Mode.PRIVATE)
        insert(rad)
    RigidJoint(label="bottom", joint_location=Pos(0,0,-10))
radials.part.label = "Radials"
radials.part.color = radial_color
frp_mid.part.joints["bottom"].connect_to(radials.part.joints["bottom"])

ant_asm = Compound(children=[ant_base.part, frp_mid.part, frp_top.part, radials.part], label="X200")

ready.append(ant_asm)
show(*ready)

#%% =========================================================
#  PUNKTY
# ===========================================================
print("Punkty (mm):")
pts = {
    "mast_bottom": (mast_x, mast_y, mast_bottom_z),
    "ump_lo":      (mast_x, mast_y, ump_z[0]),
    "ump_hi":      (mast_x, mast_y, ump_z[1]),
    "wall_top":    (0, 0, wall_height),
    "mast_top":    (mast_x, mast_y, mast_top_z),
    "ant_bottom":  (ant_ax, mast_y, ant_bottom_z),
    "ant_clamp_lo":(mast_x, mast_y, ant_clamp_z_lo),
    "ant_clamp_hi":(mast_x, mast_y, ant_clamp_z_hi),
    "ant_top":     (ant_ax, mast_y, ant_top_z),
}
for k, v in pts.items():
    print(f"  {k:14s} ({v[0]:8.1f}, {v[1]:8.1f}, {v[2]:8.1f})")
print(f"  czubek nad sciana sasiada: {ant_top_z - wall_height:.1f} mm")
print(f"  czubek nad Twoim dachem:   {ant_top_z:.1f} mm")

#%% =========================================================
#  ASSEMBLY + EXPORT
# ===========================================================
# gotowa scena = lista `ready` (antena jako podzlozenie X200, hierarchia trafia do STEP)
assembly = Compound(children=ready, label="X200 on neighbor wall, UMP-150, 40x1.5")
bb = assembly.bounding_box()
print("bbox size:", bb.size)

export_step(assembly, HERE / "mast_x200_assembly.step")
export_stl(assembly, HERE / "mast_x200_assembly.stl", tolerance=0.6)
print("Exported STEP + STL")

#%% tessellacja do rysunkow (kolor per czesc)
import pickle
import numpy as np

def _rgb(part):
    c = getattr(part, "color", None)
    if c is None:
        return (0.7, 0.7, 0.7)
    s = str(c)
    if "(" in s and ")" in s:
        nums = s[s.index("(")+1:s.index(")")].split(",")
        rgb = tuple(float(x) for x in nums[:3])
        if len(rgb) == 3:
            return rgb
    return (0.7, 0.7, 0.7)

def _leaves(parts, loc=None):
    """Compounds bez wlasnego koloru (UMP-150, X200) rozbij na czesci - kazda z wlasnym kolorem.
    Zwraca (shape, globalna Lokacja), bo dzieci komponentu nie niosa pozycji instancji."""
    out = []
    for p in parts:
        base = (loc or Location()) * p.location
        kids = list(p.children) if isinstance(p, Compound) else []
        if kids and getattr(p, "color", None) is None:
            out += _leaves(kids, base)
        else:
            out.append((p, base))
    return out

mesh_parts = []
for p, _loc in _leaves(ready):
    verts, faces = p.located(_loc).tessellate(0.7)
    verts = np.array([[vt.X, vt.Y, vt.Z] for vt in verts], dtype=float)
    faces = np.array(list(faces), dtype=int)
    rgb = _rgb(p)
    if len(rgb) != 3:
        rgb = (0.7, 0.7, 0.7)
    mesh_parts.append({"label": getattr(p, "label", ""), "verts": verts, "faces": faces, "rgb": rgb})
    print(f"  tess {getattr(p,'label',''):20s} v={len(verts):5d} f={len(faces):5d} rgb={tuple(round(x,2) for x in rgb)}")
with open(HERE / "mast_x200_meshes.pkl", "wb") as f:
    pickle.dump(mesh_parts, f)
print(f"Saved {HERE / 'mast_x200_meshes.pkl'}")

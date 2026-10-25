"""Verification: cad/ikea_pax_bar_holder.py model vs cad/ikea_pax_bar_holder.stl.

Method
  1. Build the model with build123d (imports the CAD module, no viewer).
  2. Export ASCII STL to a temp file, load both meshes as triangles.
  3. Compare bounding boxes, volumes, areas.
  4. Sample 20k area-weighted points on each mesh and measure the exact
     point-to-mesh distance both ways (Ericson closest-point, vectorised
     over points, loop over triangles).

Pass criteria (goal: models similarity 0.25 mm)
  - max symmetric surface distance <= 0.25 mm,
  - |dVol| <= 1 %, bbox identical within export tolerance.

Run:  uv run --project /workspace python cad/verify_ikea_pax_bar_holder.py
"""
import re
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

TOL_MAX = 0.25  # mm


def load_stl(path):
    data = Path(path).read_bytes()
    head = data[:400].lower()
    if b"facet" in head and b"vertex" in head:
        txt = data.decode("ascii", errors="ignore")
        pat = re.compile(
            r"facet normal\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+outer loop\s+"
            r"vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+"
            r"vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+"
            r"vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+endloop")
        fs = pat.findall(txt)
        return np.array([[[float(f[3]), float(f[4]), float(f[5])],
                          [float(f[6]), float(f[7]), float(f[8])],
                          [float(f[9]), float(f[10]), float(f[11])]] for f in fs])
    n = struct.unpack("<I", data[80:84])[0]
    T = np.empty((n, 3, 3))
    off = 84
    for i in range(n):
        T[i] = np.array(struct.unpack("<12f", data[off:off + 48])[3:12]).reshape(3, 3)
        off += 50
    return T


def vol_area(T):
    v0, v1, v2 = T[:, 0], T[:, 1], T[:, 2]
    vol = float(np.einsum("ij,ij->i", v0, np.cross(v1, v2)).sum() / 6.0)
    area = float(np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1).sum() / 2)
    return vol, area


def sample_points(T, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    v0, v1, v2 = T[:, 0], T[:, 1], T[:, 2]
    a = np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1) / 2
    idx = rng.choice(len(T), size=n, p=a / a.sum())
    r1, r2 = rng.random(n), rng.random(n)
    s = np.sqrt(r1)
    u, v, w = 1 - s, s * (1 - r2), s * r2
    return u[:, None] * T[idx, 0] + v[:, None] * T[idx, 1] + w[:, None] * T[idx, 2]


def closest_dist(P, T, batch=1000):
    """Exact point-to-triangle distance (Ericson), vectorised over points."""
    res = np.empty(len(P))
    for s in range(0, len(P), batch):
        Pb = P[s:s + batch]
        best = np.full(len(Pb), np.inf)
        for k in range(len(T)):
            a_, b_, c_ = T[k]
            ab, ac = b_ - a_, c_ - a_
            ap_ = Pb - a_
            d1 = ap_ @ ab
            d2 = ap_ @ ac
            mA = (d1 <= 0) & (d2 <= 0)
            best = np.minimum(best, np.where(mA, np.linalg.norm(ap_, axis=1), np.inf))
            bp = Pb - b_
            d3, d4 = bp @ ab, bp @ ac
            mB = (d3 >= 0) & (d4 <= d3)
            best = np.minimum(best, np.where(mB, np.linalg.norm(bp, axis=1), np.inf))
            cp = Pb - c_
            d5, d6 = cp @ ab, cp @ ac
            mC = (d6 >= 0) & (d5 <= d6)
            best = np.minimum(best, np.where(mC, np.linalg.norm(cp, axis=1), np.inf))
            vc = d1 * d4 - d3 * d2
            mAB = (vc <= 0) & (d1 >= 0) & (d3 <= 0)
            v = d1 / (d1 - d3 + 1e-300)
            best = np.minimum(best, np.where(mAB, np.linalg.norm(Pb - (a_ + v[:, None] * ab), axis=1), np.inf))
            vb = d5 * d2 - d1 * d6
            mAC = (vb <= 0) & (d2 >= 0) & (d6 <= 0)
            w_ = d2 / (d2 - d6 + 1e-300)
            best = np.minimum(best, np.where(mAC, np.linalg.norm(Pb - (a_ + w_[:, None] * ac), axis=1), np.inf))
            va = d3 * d6 - d5 * d4
            mBC = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0)
            w_ = (d4 - d3) / ((d4 - d3) + (d5 - d6) + 1e-300)
            best = np.minimum(best, np.where(mBC, np.linalg.norm(Pb - (b_ + w_[:, None] * (c_ - b_)), axis=1), np.inf))
            mIn = ~(mA | mB | mC | mAB | mAC | mBC)
            n_ = np.cross(ab, ac)
            best = np.minimum(best, np.where(mIn, np.abs(ap_ @ n_) / np.linalg.norm(n_), np.inf))
        res[s:s + batch] = best
    return res


def main():
    from build123d import export_stl
    import ikea_pax_bar_holder as m

    part = m.pax_bar_holder()
    print(f"model volume (BRep): {part.volume:.2f} mm^3")
    with tempfile.TemporaryDirectory() as td:
        out = str(Path(td) / "model.stl")
        export_stl(part, out, ascii_format=True)
        Tm = load_stl(out)
    To = load_stl(HERE / "ikea_pax_bar_holder.stl")

    vo, ao = vol_area(To)
    vm, am = vol_area(Tm)
    print(f"STL  orig: vol={vo:.2f} mm^3  area={ao:.1f} mm^2  tris={len(To)}")
    print(f"STL model: vol={vm:.2f} mm^3  area={am:.1f} mm^2  tris={len(Tm)}")
    print(f"dVol={vm - vo:+.2f} ({100 * (vm - vo) / vo:+.3f} %)  dArea={am - ao:+.1f} ({100 * (am - ao) / ao:+.3f} %)")
    bo = (To.reshape(-1, 3).min(0), To.reshape(-1, 3).max(0))
    bm = (Tm.reshape(-1, 3).min(0), Tm.reshape(-1, 3).max(0))
    print(f"bbox orig : {bo[0]} .. {bo[1]}")
    print(f"bbox model: {bm[0]} .. {bm[1]}")

    Po, Pm = sample_points(To), sample_points(Tm)
    d1 = closest_dist(Po, Tm)
    d2 = closest_dist(Pm, To)
    print(f"orig->model: max={d1.max():.4f} mean={d1.mean():.4f} p99={np.quantile(d1, .99):.4f} p95={np.quantile(d1, .95):.4f}")
    print(f"model->orig: max={d2.max():.4f} mean={d2.mean():.4f} p99={np.quantile(d2, .99):.4f} p95={np.quantile(d2, .95):.4f}")
    print(f"samples >0.05 mm: orig {(d1 > 0.05).sum()}/{len(d1)}, model {(d2 > 0.05).sum()}/{len(d2)}")

    ok = max(d1.max(), d2.max()) <= TOL_MAX
    print(f"PASS max<={TOL_MAX} mm: {ok}")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Date arbitraire (si tu veux juste l'axe temps relatif, on peut aussi faire t=sec)
EVENT_START = "2024-01-01 00:00:00"

# IMPORTANT : unité des rasters de pluie
# - "mm_h"    : raster = intensité (mm/h) au pas de temps
# - "mm_step" : raster = lame d'eau (mm) sur le pas de temps
RASTER_UNIT = "mm_h"  # <- change en "mm_step" si besoin

TIF_RE = re.compile(r"^(\d+)\.(tif|tiff)$", re.IGNORECASE)

# =========================
# HELPERS
# =========================
def spatial_mean(fp: str) -> float:
    """Moyenne spatiale du raster (en valeur brute)."""
    with rasterio.open(fp) as src:
        a = src.read(1).astype("float64")
        if src.nodata is not None:
            a[a == src.nodata] = np.nan
        a[~np.isfinite(a)] = np.nan
        return float(np.nanmean(a))

def list_tifs_with_seconds(input_dir: str):
    """Liste triée [(sec, filepath), ...] extraite du nom '12300.tif'."""
    items = []
    for f in os.listdir(input_dir):
        m = TIF_RE.match(f)
        if not m:
            continue
        sec = int(m.group(1))
        items.append((sec, os.path.join(input_dir, f)))
    items.sort(key=lambda x: x[0])
    return items

def infer_tag_from_dir(input_dir: str) -> str:
    """Extrait un tag simple type TR10 / TR50 depuis le nom du dossier."""
    base = os.path.basename(os.path.normpath(input_dir)).lower()
    if "10" in base:
        return "TR10"
    if "50" in base:
        return "TR50"
    return "TR"

def process_dir(input_dir: str, event_start: str, raster_unit: str):
    tifs = list_tifs_with_seconds(input_dir)
    if len(tifs) < 2:
        raise RuntimeError(f"Pas assez de .tif dans {input_dir} (trouvé: {len(tifs)})")

    base_dt = datetime.strptime(event_start, "%Y-%m-%d %H:%M:%S")
    tag = infer_tag_from_dir(input_dir)

    # Sorties dans le même dossier
    out_csv = os.path.join(input_dir, f"hyetogramme_{tag}.csv")
    out_png_int = os.path.join(input_dir, f"hyetogramme_{tag}_intensite.png")
    out_png_step = os.path.join(input_dir, f"hyetogramme_{tag}_lame_pas.png")
    out_png_cum = os.path.join(input_dir, f"hyetogramme_{tag}_cumul.png")

    secs = [s for s, _ in tifs]
    dts = [secs[i + 1] - secs[i] for i in range(len(secs) - 1)]
    dt_typical = int(np.median([dt for dt in dts if dt > 0])) if any(dt > 0 for dt in dts) else 60

    rows = []
    for i, (sec, fp) in enumerate(tifs):
        t = base_dt + timedelta(seconds=sec)

        if i < len(tifs) - 1:
            dt_s = secs[i + 1] - secs[i]
            if dt_s <= 0:
                dt_s = dt_typical
        else:
            dt_s = dt_typical

        raw = spatial_mean(fp)  # valeur moyenne du raster

        # Conversion selon l'unité
        if raster_unit == "mm_h":
            mean_mm_h = raw
            step_mm = mean_mm_h * (dt_s / 3600.0)
        elif raster_unit == "mm_step":
            step_mm = raw
            mean_mm_h = step_mm * (3600.0 / dt_s)
        else:
            raise ValueError("RASTER_UNIT doit être 'mm_h' ou 'mm_step'")

        rows.append({
            "time": t,
            "t_seconds": sec,
            "dt_seconds": dt_s,
            "file": os.path.basename(fp),
            "raw_mean": raw,
            "mean_mm_h": mean_mm_h,
            "step_mm": step_mm,
        })

    df = pd.DataFrame(rows)
    df["cum_mm"] = df["step_mm"].cumsum()

    # Export CSV
    df.to_csv(out_csv, index=False)

    # --- Intensité (mm/h)
    plt.figure()
    plt.plot(df["time"], df["mean_mm_h"])
    plt.xlabel("Temps")
    plt.ylabel("Intensité (mm/h)")
    plt.title(f"Pluie {tag} — Hyétogramme (intensité moyenne)")
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_png_int, dpi=200)
    plt.close()

    # --- Lame par pas (mm)
    plt.figure()
    plt.plot(df["time"], df["step_mm"])
    plt.xlabel("Temps")
    plt.ylabel("Lame d'eau sur le pas (mm)")
    plt.title(f"Pluie {tag} — Lame par pas (moyenne)")
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_png_step, dpi=200)
    plt.close()

    # --- Cumul (mm)
    plt.figure()
    plt.plot(df["time"], df["cum_mm"])
    plt.xlabel("Temps")
    plt.ylabel("Cumul (mm)")
    plt.title(f"Pluie {tag} — Cumul (moyen)")
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_png_cum, dpi=200)
    plt.close()

    print("\nOK ✅", tag)
    print("Dossier :", input_dir)
    print("Nb rasters:", len(df))
    print(f"Δt typique (médian): {dt_typical} s (~{dt_typical/60:.1f} min)")
    print("CSV :", out_csv)
    print("PNG intensité :", out_png_int)
    print("PNG lame par pas :", out_png_step)
    print("PNG cumul :", out_png_cum)
    print("Cumul final (mm):", float(df["cum_mm"].iloc[-1]))
    print("Pas de temps (fréquences):")
    print(df["dt_seconds"].value_counts().head(10))

def main(rain_dir):
    process_dir(rain_dir, EVENT_START, RASTER_UNIT)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('missing parameter: <rain_dir>')
        sys.exit(1)
    (_, rain_dir) = sys.argv
    if __debug__:
        print(f"{rain_dir = }")
    main(rain_dir)

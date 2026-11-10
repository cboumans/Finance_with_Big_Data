"""Small helpers for looking at hubs from space: NASA GIBS (MODIS) and Sentinel-2.

Both services are free and need no login.
"""
import io
import math

import numpy as np
import requests
from PIL import Image

GIBS_WMS = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
STAC = "https://earth-search.aws.element84.com/v1/search"


def bbox(lat, lon, half_km):
    """(west, south, east, north) in degrees for a square of side 2*half_km around a point."""
    dlat = half_km / 111.0
    dlon = half_km / (111.0 * math.cos(math.radians(lat)))
    return lon - dlon, lat - dlat, lon + dlon, lat + dlat


def gibs_true_color(lat, lon, date, half_km=150, px=700, layer="MODIS_Terra_CorrectedReflectance_TrueColor"):
    """MODIS true-colour image (250 m) centred on a point, as an RGB array. `date` = 'YYYY-MM-DD'."""
    w, s, e, n = bbox(lat, lon, half_km)
    r = requests.get(GIBS_WMS, timeout=60, params=dict(
        SERVICE="WMS", REQUEST="GetMap", VERSION="1.1.1", LAYERS=layer, STYLES="",
        FORMAT="image/png", SRS="EPSG:4326", BBOX=f"{w},{s},{e},{n}",
        WIDTH=px, HEIGHT=px, TIME=str(date)))
    r.raise_for_status()
    return np.asarray(Image.open(io.BytesIO(r.content)).convert("RGB")), (w, s, e, n)


def s2_search(lat, lon, start, end, limit=200):
    """Sentinel-2 L2A scenes covering a point. Returns a list of STAC items sorted by date."""
    r = requests.post(STAC, timeout=60, json=dict(
        collections=["sentinel-2-l2a"], intersects=dict(type="Point", coordinates=[lon, lat]),
        datetime=f"{start}T00:00:00Z/{end}T23:59:59Z", limit=limit))
    r.raise_for_status()
    items = r.json()["features"]
    return sorted(items, key=lambda i: i["properties"]["datetime"])


def s2_chip(item, lat, lon, half_km=3):
    """True-colour (10 m) chip around a point from a Sentinel-2 item, as an RGB array."""
    import rasterio
    from rasterio.warp import transform
    from rasterio.windows import Window
    href = item["assets"]["visual"]["href"]
    with rasterio.open(href) as ds:
        (x,), (y,) = transform("EPSG:4326", ds.crs, [lon], [lat])
        row, col = ds.index(x, y)
        half = int(half_km * 1000 / ds.res[0])
        win = Window(col - half, row - half, 2 * half, 2 * half)
        return ds.read([1, 2, 3], window=win, boundless=True, fill_value=0).transpose(1, 2, 0)


def bbox_margin(item, lat, lon):
    """Degrees from the point to the nearest edge of the scene's bounding box (bigger = more central)."""
    w, s, e, n = item["bbox"]
    return min(lon - w, e - lon, lat - s, n - lat)


def s2_best_chip(items, lat, lon, half_km=4):
    """Among several scenes of the same day, return (item, chip) with the least no-data (black) pixels.

    Neighbouring Sentinel-2 tiles overlap, and a hub near a tile edge can fall in a no-data strip.
    """
    best = None
    for it in sorted(items, key=lambda i: -bbox_margin(i, lat, lon))[:3]:
        chip = s2_chip(it, lat, lon, half_km)
        nodata = float((chip.sum(axis=2) == 0).mean())
        if best is None or nodata < best[0]:
            best = (nodata, it, chip)
    return best[1], best[2]

"""
Preset Earth-observation satellites for the interference analysis.

Live elements are fetched from CelesTrak by catalogue number at analysis time;
the fallback elements below are only used when CelesTrak cannot be reached.
They were fetched on 2026-09-06 and drift with age like any TLE.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class EOPreset:
    norad_id: int
    name: str
    fov_degrees: float  # full opening angle of the nadir-pointed cone
    fallback_line1: str
    fallback_line2: str
    note: str = ""


PRESETS: dict[str, EOPreset] = {
    "sentinel-2a": EOPreset(
        norad_id=40697,
        name="SENTINEL-2A",
        fov_degrees=20.6,
        fallback_line1="1 40697U 15028A   26249.19369740 -.00000074  00000+0 -11786-4 0  9993",
        fallback_line2="2 40697  98.5625 322.8712 0001225  85.6513 274.4810 14.30818788585312",
        note="MSI optical imager, 290 km swath from 786 km",
    ),
    "landsat-8": EOPreset(
        norad_id=39084,
        name="LANDSAT 8",
        fov_degrees=15.0,
        fallback_line1="1 39084U 13008A   26249.19255234  .00000148  00000+0  42980-4 0  9999",
        fallback_line2="2 39084  98.2233 318.3368 0001261  96.5506 263.5836 14.57111098709697",
        note="OLI/TIRS optical imagers, 185 km swath from 705 km",
    ),
    "sentinel-1a": EOPreset(
        norad_id=39634,
        name="SENTINEL-1A",
        fov_degrees=5.0,
        fallback_line1="1 39634U 14016A   26249.13466127  .00000070  00000+0  24340-4 0  9993",
        fallback_line2="2 39634  98.1598 255.4043 0001431  84.6530 275.4833 14.59802392661823",
        note="C-band SAR is side-looking; approximated here as a narrow nadir cone",
    ),
}

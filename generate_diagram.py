#!/usr/bin/env python3
"""Generates azure-multi-region.excalidraw in the same directory as this script."""

import json
import os
import hashlib

# ---------- Helpers ----------

def make_id(name):
    return hashlib.md5(name.encode()).hexdigest()[:16]

def make_seed(eid):
    return int(eid, 16) % (2**31)

def rect(name, x, y, w, h, bg, stroke, dashed=False, label=None, font_size=14, bold=False):
    eid = make_id(name)
    elements = [{
        "id": eid,
        "type": "rectangle",
        "x": x, "y": y, "width": w, "height": h,
        "angle": 0,
        "strokeColor": stroke,
        "backgroundColor": bg,
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "dashed" if dashed else "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "roundness": {"type": 3},
        "seed": make_seed(eid),
        "version": 1,
        "versionNonce": 0,
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
    }]
    if label:
        elements.append(text(f"{name}_label", label, x, y, w, font_size, stroke, bold=bold))
    return elements

def text(name, content, x, y, w, font_size=13, color="#000000", bold=False):
    eid = make_id(name)
    return {
        "id": eid,
        "type": "text",
        "x": x, "y": y, "width": w, "height": font_size + 6,
        "angle": 0,
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "roundness": None,
        "seed": make_seed(eid),
        "version": 1,
        "versionNonce": 0,
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
        "text": content,
        "fontSize": font_size,
        "fontFamily": 2,
        "textAlign": "center",
        "verticalAlign": "top",
        "baseline": font_size,
        "containerId": None,
        "originalText": content,
        "fontWeight": "bold" if bold else "normal",
    }

def arrow(name, x1, y1, x2, y2, color="#868e96"):
    eid = make_id(name)
    dx, dy = x2 - x1, y2 - y1
    return {
        "id": eid,
        "type": "arrow",
        "x": x1, "y": y1,
        "width": abs(dx), "height": abs(dy),
        "angle": 0,
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "roundness": {"type": 2},
        "seed": make_seed(eid),
        "version": 1,
        "versionNonce": 0,
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
        "points": [[0, 0], [dx, dy]],
        "lastCommittedPoint": None,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": "arrow",
    }

# ---------- Layout constants ----------

CANVAS_W = 2100

# Front Door
AFD_W, AFD_H = 500, 70
AFD_X = (CANVAS_W - AFD_W) // 2
AFD_Y = 40

# Regions
REGION_W, REGION_H = 560, 520
REGION_Y = 180
REGION_GAP = 60
REGION_START_X = (CANVAS_W - (3 * REGION_W + 2 * REGION_GAP)) // 2

REGIONS = [
    {"name": "eastus",  "label": "East US"},
    {"name": "westeu",  "label": "West Europe"},
    {"name": "seasia",  "label": "Southeast Asia"},
]

# Shared services
SHARED_Y = 760
SHARED_H = 100
SHARED_W = 420
SHARED_GAP = 40
SHARED_START_X = (CANVAS_W - (4 * SHARED_W + 3 * SHARED_GAP)) // 2

SHARED = [
    {"name": "cosmos",   "label": "Azure Cosmos DB\n(Multi-region writes)", "bg": "#ffe8cc", "stroke": "#d9480f"},
    {"name": "acr",      "label": "Azure Container\nRegistry (Global)",     "bg": "#f3d9fa", "stroke": "#7048e8"},
    {"name": "keyvault", "label": "Azure Key Vault",                         "bg": "#fff3bf", "stroke": "#f59f00"},
    {"name": "monitor",  "label": "Azure Monitor\n+ Log Analytics",          "bg": "#ffe3e3", "stroke": "#c92a2a"},
]

# Colors
C_AFD_BG,   C_AFD_STR   = "#fff3bf", "#e67700"
C_REG_BG,   C_REG_STR   = "transparent", "#495057"
C_ENV_BG,   C_ENV_STR   = "#e3fafc", "#0c8599"
C_APP_BG,   C_APP_STR   = "#d3f9d8", "#2f9e44"
C_LACR_BG,  C_LACR_STR  = "#f3d9fa", "#7048e8"
C_ARROW     = "#868e96"

# ---------- Build elements ----------

elements = []

# Azure Front Door
elements += rect("afd", AFD_X, AFD_Y, AFD_W, AFD_H, C_AFD_BG, C_AFD_STR,
                 label="Azure Front Door", font_size=16, bold=True)

# Region coordinates for arrows later
region_coords = {}

for i, reg in enumerate(REGIONS):
    rx = REGION_START_X + i * (REGION_W + REGION_GAP)
    ry = REGION_Y

    region_coords[reg["name"]] = {"x": rx, "y": ry, "w": REGION_W, "h": REGION_H}

    # Region border
    elements += rect(f"reg_{reg['name']}", rx, ry, REGION_W, REGION_H,
                     C_REG_BG, C_REG_STR, dashed=True)
    elements.append(text(f"reg_{reg['name']}_title", reg["label"],
                         rx, ry + 10, REGION_W, 15, C_REG_STR, bold=True))

    # Container Apps Environment
    env_x, env_y = rx + 20, ry + 50
    env_w, env_h = REGION_W - 40, 280
    elements += rect(f"env_{reg['name']}", env_x, env_y, env_w, env_h,
                     C_ENV_BG, C_ENV_STR,
                     label="Container Apps Environment", font_size=13, bold=True)

    # Container App inside env
    app_x, app_y = env_x + 20, env_y + 60
    app_w, app_h = env_w - 40, 180
    elements += rect(f"app_{reg['name']}", app_x, app_y, app_w, app_h,
                     C_APP_BG, C_APP_STR,
                     label="Container App", font_size=13)

    # Local ACR
    lacr_x, lacr_y = rx + 20, ry + 360
    lacr_w, lacr_h = REGION_W - 40, 80
    elements += rect(f"lacr_{reg['name']}", lacr_x, lacr_y, lacr_w, lacr_h,
                     C_LACR_BG, C_LACR_STR,
                     label="ACR Replica", font_size=13)

# Shared services
shared_coords = {}
for j, svc in enumerate(SHARED):
    sx = SHARED_START_X + j * (SHARED_W + SHARED_GAP)
    shared_coords[svc["name"]] = {"x": sx, "y": SHARED_Y, "w": SHARED_W, "h": SHARED_H}
    elements += rect(f"svc_{svc['name']}", sx, SHARED_Y, SHARED_W, SHARED_H,
                     svc["bg"], svc["stroke"],
                     label=svc["label"], font_size=13)

# ---------- Arrows ----------

# Front Door -> each region (to top-center of region box)
afd_cx = AFD_X + AFD_W // 2
afd_bot = AFD_Y + AFD_H

for reg in REGIONS:
    rc = region_coords[reg["name"]]
    reg_cx = rc["x"] + rc["w"] // 2
    reg_top = rc["y"]
    elements.append(arrow(f"arr_afd_{reg['name']}", afd_cx, afd_bot, reg_cx, reg_top, C_AFD_STR))

# Each Container App -> each shared service (bottom of app to top of service)
for reg in REGIONS:
    rc = region_coords[reg["name"]]
    app_cx = rc["x"] + REGION_W // 2
    app_bot = rc["y"] + REGION_H

    for svc in SHARED:
        sc = shared_coords[svc["name"]]
        svc_cx = sc["x"] + sc["w"] // 2
        svc_top = sc["y"]
        elements.append(arrow(
            f"arr_{reg['name']}_{svc['name']}",
            app_cx, app_bot, svc_cx, svc_top, svc["stroke"]
        ))

# ---------- Assemble & write ----------

diagram = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://excalidraw.com",
    "elements": elements,
    "appState": {
        "gridSize": None,
        "viewBackgroundColor": "#ffffff"
    },
    "files": {}
}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azure-multi-region.excalidraw")
with open(out_path, "w") as f:
    json.dump(diagram, f, indent=2)

print(f"Created {out_path} ({len(elements)} elements)")

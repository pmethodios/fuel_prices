import os
import pandas as pd
import datawrapper as dw
import json
from pathlib import Path
import math
import numpy as np

# -----------------------
# GET DATAWRAPPER API KEY
# -----------------------
API_KEY = os.environ.get("DATAWRAPPER_API") or os.environ.get("DATAWRAPPER_API")
if API_KEY is None:
    raise ValueError(
        "DATAWRAPPER_API environment variable not set! "
        "Set it in GitHub Actions secrets as DATAWRAPPER_API or locally for testing."
    )

os.environ["DATAWRAPPER_ACCESS_TOKEN"] = API_KEY

# -----------------------
# CONFIG
# -----------------------
TARGET_PREF = "ΝΟΜΟΣ ΚΕΡΚΥΡΑΣ"
CSV_URL = "https://raw.githubusercontent.com/pmethodios/fuel_prices/main/master_pref_upd.csv"

# Map each fuel type to a color
FUEL_COLORS = {
    "Αμόλυβδη 95": "#08A021",
    "Αμόλυβδη 100": "#FFCB6F",
    "Diesel Κίνησης": "#15607a",
    "Autogas": "#F54927"
}

CHART_CONFIG_FILE = "ids/chart_config.json"
Path(CHART_CONFIG_FILE).parent.mkdir(parents=True, exist_ok=True)

# -----------------------
# LOAD CSV
# -----------------------
df = pd.read_csv(CSV_URL)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df[(df['prefecture'] == TARGET_PREF) & (df['date'] >= '2026-01-01')]

# Make sure all fuel columns are numeric
for fuel_type in FUEL_COLORS.keys():
    df[fuel_type] = pd.to_numeric(df[fuel_type], errors='coerce')

# Compute per-fuel min value rounded down to nearest 0.15 below the value
fuel_min_values = {}
for fuel_type in FUEL_COLORS.keys():
    min_val = df[fuel_type].min(skipna=True)
    if pd.isna(min_val):
        continue
    rounded_min = math.floor(min_val / 0.15) * 0.15
    fuel_min_values[fuel_type] = rounded_min

# -----------------------
# LOAD EXISTING CONFIG JSON IF EXISTS
# -----------------------
config_list = []
if Path(CHART_CONFIG_FILE).exists():
    with open(CHART_CONFIG_FILE, "r", encoding="utf-8") as f:
        config_list = json.load(f)

# -----------------------
# LOOP THROUGH FUEL TYPES
# -----------------------
for fuel_type, color in FUEL_COLORS.items():
    df_chart = df[["date", fuel_type]].dropna()

    if df_chart.empty:
        print(f"No data for {fuel_type} in {TARGET_PREF}, skipping...")
        continue

    # -----------------------
    # CREATE LINE CHART
    # -----------------------
    lower_y = fuel_min_values.get(fuel_type, None)
    chart = dw.LineChart(
        source_name="Υπουργείο Ανάπτυξης",
        source_url="https://github.com/pmethodios/fuel_prices",
        data=df_chart,
        x_column="date",
        y_grid_format="0.00",
        custom_ticks_y=[1.0, 1.25, 1.5, 1.75, 2.0],  # can adjust per-fuel if needed
        custom_range_y=[lower_y, None],
        tooltip_x_format="DD-MM-YYYY",
        show_tooltips=True,
        dark_mode_invert=True,
        label_colors=True,
        color_category={fuel_type: color},
        x_grid="off",
        x_grid_format="DD/MM",
        custom_ticks_x=["2026-02-28"]
    )

    # -----------------------
    # ADD WIDE LINE
    # -----------------------
    chart.lines.append(
        dw.Line(
            column=fuel_type,
            width=dw.LineWidth.THICK,
            interpolation=dw.LineInterpolation.CURVED,
            show_first_value_label=True,
            show_last_value_label=True,
            show_symbols=True,
            line_symbol="circle"
        )
    )

    # -----------------------
    # CREATE CHART ON DATAWRAPPER
    # -----------------------
    result = chart.create()
    chart_id = result.chart_id
    print(f"Chart created! {fuel_type} ID: {chart_id}")
    print(f"https://datawrapper.dwcdn.net/{chart_id}/")

    # -----------------------
    # SAVE JSON CONFIG AS LIST
    # -----------------------
    config_list.append({
        "chart_id": chart_id,
        "prefecture": TARGET_PREF,
        "fuel_type": fuel_type
    })

# -----------------------
# SAVE UPDATED CONFIG LIST
# -----------------------
with open(CHART_CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(config_list, f, ensure_ascii=False, indent=2)

print(f"All chart info saved to {CHART_CONFIG_FILE}")
import os
import pandas as pd
import datawrapper as dw
import json
from pathlib import Path


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

TARGET_PREF = "ΝΟΜΟΣ ΚΕΡΚΥΡΑΣ"
CSV_URL = "https://raw.githubusercontent.com/pmethodios/fuel_prices/main/master_pref_upd.csv"

FUEL_COLORS = {
    "Αμόλυβδη 95": "#08A021",
}
CHART_CONFIG_FILE = "datawrapper_api/chart_config.json"

# -----------------------
# LOAD & FILTER DATA
# -----------------------
df = pd.read_csv(CSV_URL)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df[(df['prefecture'] == TARGET_PREF) & (df['date'] >= '2026-01-01')]
df = df[["date"] + list(FUEL_COLORS.keys())]

# -----------------------
# CREATE LINE CHART
# -----------------------
chart = dw.LineChart(
    source_name="Υπουργείο Ανάπτυξης",
    source_url="https://github.com/pmethodios/fuel_prices",
    data=df,
    x_column="date",
    y_grid_format="0.00",
    custom_ticks_y=[1.0, 1.25, 1.5, 1.75, 2.0],
    custom_range_y=[1.4, None],
    tooltip_x_format="DD-MM-YYYY",
    show_tooltips=True,
    dark_mode_invert=True,
    label_colors=True,
    color_category=FUEL_COLORS,
    x_grid="off",
    x_grid_format="DD/MM",
    custom_ticks_x=["2026-02-28"]
)

# -----------------------
# ADD WIDE LINE
# -----------------------
chart.lines.append(
    dw.Line(
        column="Αμόλυβδη 95",
        width=dw.LineWidth.THICK,
        interpolation=dw.LineInterpolation.CURVED
    )
)
# -----------------------
# CREATE CHART ON DATAWRAPPER
# -----------------------
result = chart.create()
print("Chart created!")

# -----------------
# Save the id of the chart
# -----------------

chart_id = result.chart_id

print(f"Chart created! ID: {chart_id}")
print(f"https://datawrapper.dwcdn.net/{chart_id}/")

# -----------------------
# SAVE JSON CONFIG AS LIST
# -----------------------
# Check if JSON exists; if not, start a new list
CHART_CONFIG_FILE = "ids/chart_config.json"

# Ensure the parent folder exists
Path(CHART_CONFIG_FILE).parent.mkdir(parents=True, exist_ok=True)

# Check if JSON exists; if not, start a new list
config_list = []
if Path(CHART_CONFIG_FILE).exists():
    with open(CHART_CONFIG_FILE, "r", encoding="utf-8") as f:
        config_list = json.load(f)

# Append new chart info
config_list.append({
    "chart_id": chart_id,
    "prefecture": TARGET_PREF,
    "fuel_type": list(FUEL_COLORS.keys())[0]  # only one here
})

# Save back
with open(CHART_CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(config_list, f, ensure_ascii=False, indent=2)

print(f"Chart info saved to {CHART_CONFIG_FILE}")
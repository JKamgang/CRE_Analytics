import pandas as pd
import plotly.express as px

# 1. HARD-CODED DATASET (EXTRACTED FROM YOUR PDF PAGE 3)
# This ensures the script works even without a live API connection.
data = [
    # COMPLETED 2024
    {"Name": "Upton Place", "Lat": 38.944, "Lon": -77.075, "Units": 689, "Year": 2024, "Status": "Completed", "Value": 290},
    {"Name": "Annex on 10th", "Lat": 38.883, "Lon": -77.025, "Units": 562, "Year": 2024, "Status": "Completed", "Value": 100},
    {"Name": "Vermeer", "Lat": 38.868, "Lon": -77.012, "Units": 501, "Year": 2024, "Status": "Completed", "Value": 259},
    {"Name": "The Westerly", "Lat": 38.880, "Lon": -77.018, "Units": 449, "Year": 2024, "Status": "Completed", "Value": 179},
    {"Name": "The Lis", "Lat": 38.913, "Lon": -77.030, "Units": 430, "Year": 2024, "Status": "Completed", "Value": 130},
    # UNDER CONSTRUCTION 2025-2026
    {"Name": "The Stacks Ph1", "Lat": 38.865, "Lon": -77.013, "Units": 1100, "Year": 2025, "Status": "Under Construction", "Value": 650},
    {"Name": "Wardman Park", "Lat": 38.925, "Lon": -77.052, "Units": 900, "Year": 2025, "Status": "Under Construction", "Value": 500},
    {"Name": "The Bridge Ph1", "Lat": 38.862, "Lon": -76.995, "Units": 757, "Year": 2025, "Status": "Under Construction", "Value": 350},
    {"Name": "Reservoir District", "Lat": 38.922, "Lon": -77.015, "Units": 730, "Year": 2026, "Status": "Under Construction", "Value": 720},
    # PIPELINE 2027-2033
    {"Name": "Reservation 13", "Lat": 38.885, "Lon": -76.975, "Units": 1000, "Year": 2033, "Status": "Pipeline", "Value": 700},
    {"Name": "Fletcher Johnson", "Lat": 38.882, "Lon": -76.935, "Units": 879, "Year": 2028, "Status": "Pipeline", "Value": 400},
    {"Name": "East River Park", "Lat": 38.895, "Lon": -76.955, "Units": 855, "Year": 2027, "Status": "Pipeline", "Value": 325},
    {"Name": "Martin's View", "Lat": 38.850, "Lon": -76.995, "Units": 821, "Year": 2030, "Status": "Pipeline", "Value": 200},
    {"Name": "2 Patterson St", "Lat": 38.905, "Lon": -77.005, "Units": 660, "Year": 2028, "Status": "Pipeline", "Value": 150},
    {"Name": "1001 6th St", "Lat": 38.903, "Lon": -77.020, "Units": 539, "Year": 2028, "Status": "Pipeline", "Value": 180},
    {"Name": "850 S Capitol", "Lat": 38.878, "Lon": -77.008, "Units": 520, "Year": 2030, "Status": "Pipeline", "Value": 260},
]

df = pd.DataFrame(data)

# 2. TIME SERIES PREP
# We ensure every year between 2024 and 2033 is represented so the animation is smooth
all_years = pd.DataFrame({'Year': range(df['Year'].min(), df['Year'].max() + 1)})
# To show growth, we want projects to "stay" on the map once they appear
# This creates a cumulative 'Flood' effect
frames = []
for year in all_years['Year']:
    temp_df = df[df['Year'] <= year].copy()
    temp_df['Display_Year'] = year
    frames.append(temp_df)

plot_df = pd.concat(frames)

# 3. GEO-INTELLIGENCE VISUALIZATION
fig = px.scatter_mapbox(
    plot_df,
    lat="Lat",
    lon="Lon",
    size="Units",          # The "Depth" of the flood
    color="Status",         # Project status
    hover_name="Name",
    hover_data=["Year", "Value", "Units"],
    animation_frame="Display_Year", # THE TIME SERIES TRIGGER
    title="DC CRE 'Flood Map': Interactive Pipeline Analysis 2024-2033",
    mapbox_style="carto-positron",
    zoom=11.5,
    center={"lat": 38.895, "lon": -77.01}, # Center on DC
    height=700,
    color_discrete_map={
        "Completed": "#2ecc71",         # Green
        "Under Construction": "#f1c40f", # Yellow
        "Pipeline": "#3498db"           # Blue
    }
)

fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
fig.show()
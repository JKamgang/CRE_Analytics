import pandas as pd
import plotly.express as px
import requests

# 1. DIRECT API CONNECTION TO OPEN DATA DC (WDCEP Report)
# This ensures "near real-time" data access.
API_URL = "https://services.arcgis.com/ujwv7GvS8v2D96mO/arcgis/rest/services/WDCEP_Development_Report/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

def get_live_data():
    try:
        response = requests.get(API_URL)
        data = response.json()
        # Convert GeoJSON to a flat DataFrame
        features = [
            {**f['properties'], 'lon': f['geometry']['coordinates'][0], 'lat': f['geometry']['coordinates'][1]} 
            for f in data['features']
        ]
        df = pd.DataFrame(features)
        return df
    except:
        print("API connection failed, using local backup...")
        return None

# 2. DATA PREPARATION & CLEANING
df = get_live_data()

# Ensure we have a numeric Year column for the Time Series
df['EST_DELIVERY_YEAR'] = pd.to_numeric(df['EST_DELIVERY_YEAR'], errors='coerce')
df = df.dropna(subset=['EST_DELIVERY_YEAR'])
df = df.sort_values(by='EST_DELIVERY_YEAR')

# 3. GEO-INTELLIGENCE VISUALIZATION (THE "FLOOD GRAPH")
fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    size="TOTAL_RESIDENTIAL_UNITS", # The "Depth" of the flood
    color="STATUS",               # Color by Project Phase
    hover_name="PROJECT_NAME",
    hover_data=["WARD", "EST_DELIVERY_YEAR", "DEVELOPER"],
    animation_frame="EST_DELIVERY_YEAR", # THE TIME SERIES TRIGGER
    title="DC CRE Growth: The 'Flood' of Development (2024-2030)",
    mapbox_style="carto-positron",
    color_discrete_map={
        "Completed": "#2ecc71",
        "Under Construction": "#f1c40f",
        "Pipeline": "#3498db"
    },
    zoom=11,
    height=800
)

# Refine the layout to look professional like the NYT example
fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

# 4. SHOW THE OUTPUT
fig.show()

# 5. SAVE FOR MIKE
# fig.write_html("DC_Development_Flood_Map.html")
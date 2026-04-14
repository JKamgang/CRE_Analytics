# CRE Flood Graph Dashboard - Setup Instructions

## Quick Start

### Step 1: Place CSV Files
Copy all 4 CSV files from the `data/` folder to this location on your computer:
```
C:\Users\jkamg\OneDrive\Data\Kamgang\Personal\Business\Alile Properties LLC\2025\Trainings\To Read\Real Estate\Project REAP\Mentorship - Mike Bush\Analysis - Report\Abacus\
```

The required files are:
- `combined_pipeline.csv` (999 projects with lat/long coordinates)
- `sector_lookup.csv` (sector color mapping)
- `city_lookup.csv` (city/region lookup)
- `time_dimension.csv` (year/quarter dimension)

### Step 2: Open the Dashboard
1. Double-click `CRE_Flood_Graph_Dashboard_Working.pbix`
2. Power BI Desktop will open and attempt to load data
3. If prompted about data source privacy, select "Ignore Privacy Levels" or set all to "Organizational"
4. Click "Refresh" in the Home ribbon to load all data

### Step 3: If Data Source Path Needs Updating
If the CSV files are in a different location:
1. Go to **Home → Transform data → Data source settings**
2. Click on each source and select **Change Source**
3. Browse to the folder containing your CSV files
4. Click **Close & Apply**

## Dashboard Structure

### Page 1: Executive Overview
- **KPI Cards**: Total Projects, Total SF, Active Cities, Total Est Value, Growth Rate
- **Map**: Geographic distribution with bubble sizes by square footage
- **Flood Chart**: Stacked area chart showing cumulative SF by sector over time
- **Donut Chart**: Pipeline breakdown by sector
- **Slicers**: Filter by Sector, City, and Status

### Page 2: Multifamily Deep-Dive
- **MF KPI Cards**: MF Projects, Units, Avg Density, Completion Rate, Pipeline Units
- **Map**: Multifamily-filtered geographic view
- **Line Chart**: Multifamily units by delivery year
- **Detail Table**: Full project listing for multifamily sector

### Page 3: Time Series Analysis
- **Clustered Column**: Annual SF delivery by sector
- **Cumulative Growth**: Line chart showing cumulative SF and project count
- **Growth Rate**: Year-over-year growth rate trend
- **Status by Year**: Projects by year broken down by status

## DAX Measures Included
- Total Projects, Total SF, Total SF (M), Total Units, Total Est Value
- Active Cities, Active Sectors, Avg Project Size
- Cumulative SF, Cumulative SF by Sector, Cumulative Projects
- Growth Rate YoY, Bubble Size, Project Density
- MF Total Units, MF Total Projects, MF Avg Unit Density
- MF Completion Rate, MF Pipeline Units

## Data Model
- **combined_pipeline** (fact table) → **sector_lookup** (via sector)
- **combined_pipeline** (fact table) → **city_lookup** (via city)
- **time_dimension** (standalone dimension)
- Latitude/Longitude columns marked with proper data categories for map visuals

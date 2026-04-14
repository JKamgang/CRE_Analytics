# CRE Flood Graph Dashboard — Fixed Package

## Problem
The original `CRE_Flood_Graph_Dashboard.pbix` file was corrupted — it was missing the required `DataMashup` binary component that Power BI Desktop needs to open the file.

## Solution — Multiple Deliverables

### 1. Interactive HTML Dashboard (RECOMMENDED — Works Immediately)

**`CRE_Flood_Graph_Dashboard_Standalone.html`** — Self-contained, open in any browser.

This is a fully interactive dashboard that replicates all Power BI functionality:
- **3 Pages**: Executive Overview, Multifamily Deep-Dive, Time Series Analysis
- **Interactive Slicers**: Filter by City, Sector, Status, Year Range
- **Map Visuals**: Leaflet maps with circle markers sized by SF, colored by sector
- **All Charts**: Donut, Stacked Bar, Cumulative Area, Line, Growth Rate
- **KPI Cards**: Total Projects, SF, Units, Cities, Sectors, Est. Value
- **999 CRE projects** with full data embedded

### 2. Power BI Template File (.pbit)

**`CRE_Flood_Graph_Dashboard_Fixed.pbit`**

Open this in Power BI Desktop on Windows. It will:
1. Prompt you to refresh data — point it to `combined_pipeline.csv`
2. Load the complete semantic model with all DAX measures
3. Display all 3 report pages with visuals

**To use:**
1. Copy `combined_pipeline.csv` to `C:\Users\Public\Documents\`
2. Open the `.pbit` file in Power BI Desktop
3. When prompted, update the file path to your CSV location
4. Click "Load" to import data

### 3. Fixed .pbix File

**`CRE_Flood_Graph_Dashboard_Fixed.pbix`**

This file has the correct structure with `DataMashup` included. However, since it was created on Linux (without the Analysis Services engine), it does not contain the `DataModel` binary (VertiPaq columnar store). Power BI Desktop will need to refresh the data on first open.

## Semantic Model (included in .pbit/.pbix)

### Table: combined_pipeline (999 rows)
- project_name, city, ward, neighborhood, developer, architect
- sector, status, sqft, units, est_value_millions
- est_delivery, report_year, latitude, longitude
- delivery_year, delivery_quarter, delivery_date

### DAX Measures (19 measures)
- **Core KPIs**: Total Projects, Total SF, Total SF (M), Total Units, Total Est Value, Active Cities, Active Sectors, Avg Project Size
- **Cumulative/Growth**: Cumulative SF, Cumulative SF by Sector, Cumulative Projects, Growth Rate YoY
- **Multifamily**: MF Total Units, MF Total Projects, MF Avg Unit Density, MF Completion Rate, MF Pipeline Units
- **Map**: Bubble Size, Project Density

### Data Categories
- latitude → Latitude (for map visuals)
- longitude → Longitude (for map visuals)
- city → City
- sector → Category

## Dashboard Pages

### Page 1: Executive Overview
- 7 KPI cards (Total Projects, SF, Units, Cities, Sectors, Est Value, Avg Size)
- Interactive map with projects sized by SF, colored by sector
- Donut chart: SF by Sector
- Cumulative SF area chart (Flood Effect)
- Stacked bar: Projects by Sector & Year
- Slicers: City, Sector, Status, Year Range

### Page 2: Multifamily Deep-Dive
- 6 KPI cards (MF Projects, Units, SF, Avg Density, Completion Rate, Pipeline Units)
- Multifamily-only map
- Bar/Line combo: Projects & Units by Year
- Status distribution donut
- Top 25 MF projects table

### Page 3: Time Series Analysis
- Annual Project Count bar chart
- Annual SF Delivered bar chart
- Sectors Over Time stacked bar
- Cumulative Growth dual-axis line chart
- Year-over-Year Growth Rate bar chart (green/red)

## Theme
CRE Flood Graph Theme with sector colors:
- Office: #2196F3 (Blue)
- Multifamily: #FF9800 (Orange)
- Retail: #4CAF50 (Green)
- Hotel: #9C27B0 (Purple)
- Other: #F44336 (Red)
- Industrial: #00BCD4 (Cyan)
- Mixed-Use: #607D8B (Gray)

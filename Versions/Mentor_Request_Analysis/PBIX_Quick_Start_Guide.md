# CRE Flood Graph Dashboard — Power BI Quick Start Guide

## File: `CRE_Flood_Graph_Dashboard.pbix`

### What's Included
This .pbix file contains a **fully configured** Power BI report with:

- **3 Report Pages** with 37 total visuals pre-configured
- **19 DAX Measures** (Total SF, Cumulative SF, Growth Rate YoY, MF metrics, etc.)
- **Complete Data Model** (4 tables, 2 relationships)
- **Custom CRE Flood Theme** (sector color coding applied)
- **All visual configurations** (maps, charts, cards, slicers, tables)

---

### How to Open & Activate

1. **Open** `CRE_Flood_Graph_Dashboard.pbix` in Power BI Desktop (Windows)
2. **Import Data**: Go to **Home → Get Data → Text/CSV**
   - Navigate to `PowerBI_Dashboard_Package/data/combined_pipeline.csv`
   - Click **Load**
3. **Repeat** for `sector_lookup.csv`, `city_lookup.csv`, `time_dimension.csv`
4. **Set Data Types** in Power Query Editor:
   - `latitude` / `longitude` → Decimal Number
   - `sqft`, `units`, `est_value_millions` → Decimal Number
   - `delivery_year`, `report_year` → Whole Number
   - `delivery_date` → Date
5. **Create Relationships** in Model View:
   - `combined_pipeline[sector]` → `sector_lookup[sector]`
   - `combined_pipeline[city]` → `city_lookup[city]`
6. **Apply Theme**: View → Themes → Browse → Select `CRE_Flood_Theme.json`
7. **Create DAX Measures**: Copy from `DAX_Measures.dax` (Modeling → New Measure)

### Page Layout Summary

| Page | Visuals | Key Features |
|------|---------|-------------|
| Executive Overview | 16 | KPI cards, bubble map, flood area chart, donut, slicers |
| Multifamily Deep-Dive | 11 | MF-filtered map, line chart, data table, status bar chart |
| Time Series Analysis | 10 | Annual trends, sector comparison, cumulative growth |

### Sector Color Coding
- Office: Blue (#2196F3)
- Retail: Orange (#FF9800)
- Multifamily: Green (#4CAF50)
- Hotel: Purple (#9C27B0)
- Industrial: Red (#F44336)
- Mixed-Use: Teal (#00BCD4)

### Data: 999 projects across DC and Atlanta

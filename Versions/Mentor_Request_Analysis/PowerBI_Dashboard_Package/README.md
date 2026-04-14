# CRE Flood Graph - Power BI Dashboard Package

## Contents
- **data/** - CSV data files for import
  - combined_pipeline.csv - Main fact table (999 projects, DC + Atlanta)
  - sector_lookup.csv - Sector dimension table
  - city_lookup.csv - City dimension table
  - time_dimension.csv - Time dimension table
- **CRE_Flood_Theme.json** - Custom Power BI theme file
- **DAX_Measures.dax** - All DAX measures (copy into Power BI)
- **PowerQuery_M_Scripts.m** - Power Query M code for data import
- **README.md** - This file

## Quick Start
1. Open Power BI Desktop
2. Get Data → Text/CSV → Import each file from data/ folder
3. Apply theme: View → Themes → Browse → CRE_Flood_Theme.json
4. Create measures from DAX_Measures.dax
5. Follow Power_BI_Enhanced_Instructions.docx for visual creation

## Dashboard Pages
- Page 1: Executive Overview (KPIs, Flood Chart, Map)
- Page 2: Multifamily Deep-Dive
- Page 3: Time Series Analysis

# 🌊 CRE Flood Graph — Development Pipeline Visualizer

**Interactive Streamlit dashboard** that visualizes commercial real estate (CRE) development growth over time using a "flood rising" metaphor — development activity rises across the map like flood water, showing growth by sector, geography, and timeline.

Built for **Project REAP** by Jean Baptiste K. under mentorship of Mike Bush.

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **🌊 Animated Flood-Rising Map** | Choropleth scatter-map with animation slider — watch development "rise" year by year |
| **📍 Geointelligence Map** | Interactive map with zoom, pan, sector-colored bubbles, detailed tooltips |
| **📈 Time Series Trends** | Area charts, line charts, stacked bars showing development trends by sector |
| **🏢 Multifamily Deep-Dive** | Dedicated section with unit counts, density trends, top projects |
| **📋 Data Explorer** | Browse, filter, and export the full dataset as CSV |
| **🏙️ Multi-City Support** | Toggle between Washington DC and Atlanta data |
| **🔌 CoStar-Ready** | Modular data pipeline designed for future CoStar API integration |

---

## 📁 Project Structure

```
CRE_Flood_Graph_Python_Solution/
├── app.py                          # Main Streamlit dashboard
├── config.py                       # Configuration (API endpoints, settings)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── pipelines/                      # Data ingestion modules
│   ├── __init__.py
│   ├── dc_pipeline.py              # DC (Open Data DC / WDCEP) pipeline
│   ├── atlanta_pipeline.py         # Atlanta (building permits) pipeline
│   └── costar_pipeline.py          # CoStar placeholder (future)
│
├── utils/                          # Processing & analysis utilities
│   ├── __init__.py
│   └── data_processor.py           # Data loading, merging, analysis helpers
│
├── data/
│   ├── raw/                        # Raw API data (auto-generated)
│   └── processed/                  # Cleaned CSVs for Excel/Power BI
│
└── assets/                         # Static assets (logos, etc.)
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- pip

### 2. Install Dependencies
```bash
cd CRE_Flood_Graph_Python_Solution
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```
The app opens at **http://localhost:8501** by default.

### 4. Run Individual Pipelines (optional)
```bash
# Fetch DC data only
python -m pipelines.dc_pipeline

# Fetch Atlanta data only
python -m pipelines.atlanta_pipeline
```

---

## 📊 Data Sources

| Source | City | API Type | Notes |
|--------|------|----------|-------|
| **Open Data DC — WDCEP Development Report** | Washington, DC | ArcGIS FeatureServer | Major development & construction projects |
| **City of Atlanta — Building Permits** | Atlanta, GA | ArcGIS FeatureServer | Building permit records |
| **CoStar** (future) | Multi-market | REST API | Requires paid subscription |

### Canonical Data Schema

All data sources are normalized to this common schema:

| Column | Type | Description |
|--------|------|-------------|
| `project_name` | string | Name of the development project |
| `city` | string | City code (DC, ATL) |
| `ward` | string | Ward/district number |
| `neighborhood` | string | Location/neighborhood |
| `developer` | string | Developer name |
| `architect` | string | Architect name |
| `sector` | string | CRE sector (Office, Retail, Multifamily, etc.) |
| `status` | string | Project status |
| `sqft` | float | Square footage |
| `units` | float | Number of units (residential) |
| `est_value_millions` | float | Estimated value in millions |
| `est_delivery` | string | Estimated delivery date |
| `report_year` | int | Year of the report/permit |
| `latitude` | float | Latitude coordinate |
| `longitude` | float | Longitude coordinate |

---

## 🔌 CoStar Integration Guide

The application is designed with a **modular pipeline architecture** for easy CoStar integration:

1. **Open** `pipelines/costar_pipeline.py`
2. **Implement** the `run_costar_pipeline()` function following the DC/Atlanta pattern
3. **Set** `COSTAR_CONFIG["enabled"] = True` in `config.py`
4. **Add** your CoStar API key to environment: `export COSTAR_API_KEY=your_key`
5. The data processor will automatically pick up CoStar data

---

## 📤 Exporting Data

### For Excel
Use the **📋 Data Explorer** tab → click **"⬇️ Download Filtered Data as CSV"**

### For Power BI
1. Run the pipeline: `python -m pipelines.dc_pipeline`
2. Import the CSV from `data/processed/dc_pipeline_processed.csv`
3. Or connect Power BI directly to the Streamlit app's CSV export

---

## 🌐 Deployment

### Streamlit Community Cloud (free)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and deploy

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

### AWS / Azure / GCP
Deploy as a containerized web app on any cloud platform.

---

## 📝 License

Built for Project REAP educational purposes. Data sourced from public open data portals.

---

*© 2026 Jean Baptiste K. — Project REAP · Mentored by Mike Bush*

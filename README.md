# Alile CRE Growth Solution: Data Artery

This repository implements the 'Data Artery' for the Alile Commercial Real Estate (CRE) Growth solution using Feature-Sliced Design (FSD).
The solution prepares data for a 'Growth Flooding' visualizer by combining geospatial data, macro-economic indices, and AI-driven insights.

## Architecture: Feature-Sliced Design (FSD)

The codebase is organized into layers to maintain modularity and high cohesion:

1. **`app`**: Application entry points (`main.py`).
2. **`widgets`**: Composition layer (`pipeline_runner.py` combining features and entities).
3. **`features`**: Core business logic and calculations:
   - `flood_pressure`: Calculates semantic logic based on permit intensity, absorption, and momentum.
   - `cumulative_flood`: Time-series projection from 2010 to 2026.
   - `llm_cascade`: AI routing logic for explanations (Local -> API -> Gemini 1.5 Pro).
4. **`entities`**: Data models and API fetchers for domain objects (`Permit`, `DevelopmentProject`, `CREMIIndex`).
5. **`shared`**: Utilities, config, and base API clients (ArcGIS, standard HTTP).

## Data Pipelines and Flow

The pipeline executes the following flow:
1. **Fetch:** Pulls recent building permits (Atlanta) and active development projects (Wash DC) via ArcGIS endpoints. It also retrieves macroeconomic momentum data (simulating Atlanta Fed CREMI).
2. **Calculate:** Computes the current "Flood Pressure" score based on normalized estimated costs (Permits), square footage (Developments), and market momentum (CREMI).
3. **Project:** Simulates a time-series growth mapping (Cumulative Flood) tracking pressure compounding from 2010 to 2026.
4. **Explain:** Uses an LLM cascade to convert numerical data into human-readable insights for real estate developers and students.

## Data Sources: Commercial and Free

This solution comes preloaded with integrations for free municipal data, but is designed to integrate commercial APIs for production scale.

### Pre-loaded Free Data Sources
- **Atlanta City GIS / ARC Open Data Hub**: Provides municipal building permits indicating micro-level construction intensity.
  - *Pipeline:* Fetched via ArcGIS GeoService API from the Atlanta Regional Commission Open Data platform.
- **Washington DC WDCEP Development Report**: Tracks large-scale developments, properties, and absorption status.
  - *Pipeline:* Fetched via DC GIS Open Data ArcGIS endpoints.
- **Atlanta Fed CREMI Index (Macro)**: Serves as a baseline for momentum and risk.
  - *Pipeline:* Simulated in code (as real access often requires CSV ingestion or special Fed APIs).

### Commercial Paid Data Sources (Recommended Upgrades)
- **CoStar / LoopNet API**: Granular, comprehensive absorption, vacancy, and rent data.
- **Real Capital Analytics (RCA)**: Transaction history and deep capital flows.
- **Trepp**: CMBS loan data to understand specific asset distress or financial risk.
- **Placer.ai**: Human mobility data to track real-time foot traffic and utilization rates.

## The Role of AI in Learning and Insight Discovery

The 'Data Artery' doesn't just pass numbers; it explains them.
We utilize an **LLM Cascade Router** (with fallbacks ranging from local caching up to Google Gemini 1.5 Pro) to serve multiple purposes:

- **Insight Discovery**: Translates complex, combined metrics (like a "Flood Pressure of 0.42") into actionable statements (e.g., "High pressure in this corridor indicates rapid commercial absorption...").
- **Facilitating Learning**: Users (students, junior developers, analysts) can see the raw math and the AI's explanation side-by-side, teaching them how macroeconomic and micro-permit data correlate in real estate.
- **Robustness**: The 5-fallback routing ensures an explanation is always provided, saving API costs on repetitive queries while defaulting to advanced models for complex, novel scenarios.

## Quick Start

### 1. Prerequisites
- Python 3.10+
- (Optional) Gemini API Key for AI Insights

### 2. Installation
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key  # Optional
```

### 3. Launching the Web Application
To launch the interactive dashboard (Alile CRE Analytics):
```bash
streamlit run src/widgets/dashboard/app.py
```

### 4. Running the Data Pipeline (CLI)
To run the underlying data ingestion and analysis pipeline:
```bash
python3 -m src.app.main
```

## Branding & Mission
A product of **Alile Group** (alileva.com).
Contact: cs@alileva.com

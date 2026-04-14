# CRE Pipeline Dashboard — Data Download Guide

## 📁 Files Included

All 4 CSV data files are located in the `data/` folder:

| # | File | Size | Description |
|---|------|------|-------------|
| 1 | `combined_pipeline.csv` | 167 KB (999 rows) | Main dataset — all CRE pipeline projects with location, sector, status, sqft, units, and delivery dates |
| 2 | `sector_lookup.csv` | 157 B (7 rows) | Lookup table — sector names, color codes, and sort order |
| 3 | `city_lookup.csv` | 99 B (2 rows) | Lookup table — city abbreviations, full names, state, and region |
| 4 | `time_dimension.csv` | 1.5 KB (48 rows) | Date dimension — year/quarter combos from 2017–2029 with forecast flag |

---

## ⬇️ How to Download

1. Look at the **top-right corner** of the DeepAgent chat interface.
2. Click the **"Files"** button (folder icon).
3. You will see all files created during this session.
4. Navigate to **`CRE_Dashboard_Delivery/data/`** and download all 4 CSV files.
5. Alternatively, download the entire `CRE_Dashboard_Delivery` folder.

---

## 🖥️ Folder Structure for Your Windows Machine

After downloading, place the files so they match this exact structure:

```
C:\Users\YourName\Documents\CRE_Dashboard\
└── data\
    ├── combined_pipeline.csv
    ├── sector_lookup.csv
    ├── city_lookup.csv
    └── time_dimension.csv
```

> **Important:** The Power BI report (.pbix file) expects the data files to be in a `data\` subfolder relative to where you save the report. Keep the folder structure intact.

---

## 🔗 Connecting in Power BI Desktop

1. Open the `.pbix` file in **Power BI Desktop**.
2. Go to **Home → Transform Data → Data Source Settings**.
3. Update the file paths to point to your local `data\` folder (e.g., `C:\Users\YourName\Documents\CRE_Dashboard\data\combined_pipeline.csv`).
4. Click **Close & Apply** to refresh.

---

## 📋 File Paths on the DeepAgent VM

For reference, the exact paths on this machine are:

```
/home/ubuntu/CRE_Dashboard_Delivery/data/combined_pipeline.csv
/home/ubuntu/CRE_Dashboard_Delivery/data/sector_lookup.csv
/home/ubuntu/CRE_Dashboard_Delivery/data/city_lookup.csv
/home/ubuntu/CRE_Dashboard_Delivery/data/time_dimension.csv
```

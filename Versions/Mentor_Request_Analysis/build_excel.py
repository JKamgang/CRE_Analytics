#!/usr/bin/env python3
"""
CRE Flood Graph Excel Builder
Creates two Excel workbooks: Comprehensive and Quick Demo
"""
import pandas as pd
import numpy as np
import re
from openpyxl import Workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                              NamedStyle, numbers)
from openpyxl.chart import (BarChart, LineChart, AreaChart, PieChart, 
                             Reference, Series)
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint
from openpyxl.utils import get_column_letter
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.formatting.rule import DataBarRule
from copy import copy

# ─── COLOR PALETTE ───────────────────────────────────────────────────────────
COLORS = {
    'Office':      '2E86AB',  # Blue
    'Retail':      'F6511D',  # Orange-Red
    'Multifamily': '7FB800',  # Green
    'Industrial':  'FFB400',  # Gold
    'Hotel':       '8338EC',  # Purple
    'Mixed-Use':   '00A896',  # Teal
    'Other':       '999999',  # Gray
}

HEADER_FILL = PatternFill(start_color='1B2A4A', end_color='1B2A4A', fill_type='solid')
HEADER_FONT = Font(name='Calibri', bold=True, color='FFFFFF', size=11)
SUBHEADER_FILL = PatternFill(start_color='3D5A80', end_color='3D5A80', fill_type='solid')
SUBHEADER_FONT = Font(name='Calibri', bold=True, color='FFFFFF', size=10)
TITLE_FONT = Font(name='Calibri', bold=True, size=20, color='1B2A4A')
SUBTITLE_FONT = Font(name='Calibri', bold=True, size=14, color='3D5A80')
METRIC_FONT = Font(name='Calibri', bold=True, size=28, color='1B2A4A')
METRIC_LABEL_FONT = Font(name='Calibri', size=10, color='666666')
THIN_BORDER = Border(
    left=Side(style='thin', color='D0D0D0'),
    right=Side(style='thin', color='D0D0D0'),
    top=Side(style='thin', color='D0D0D0'),
    bottom=Side(style='thin', color='D0D0D0')
)
ALT_ROW_FILL = PatternFill(start_color='F2F6FA', end_color='F2F6FA', fill_type='solid')

# ─── DATA LOADING & PREPARATION ─────────────────────────────────────────────
def parse_delivery_year(val):
    """Extract a single year from est_delivery field."""
    if pd.isna(val) or str(val).strip() == '':
        return np.nan
    s = str(val).strip()
    # "Q1 24" → 2024
    m = re.match(r'Q\d\s+(\d{2})$', s)
    if m:
        yr = int(m.group(1))
        return 2000 + yr if yr < 50 else 1900 + yr
    # "2024" or first year of range "2020-2032"
    m = re.match(r'(\d{4})', s)
    if m:
        return int(m.group(1))
    return np.nan

def load_data():
    dc = pd.read_csv('/home/ubuntu/CRE_Flood_Graph_Python_Solution/data/processed/dc_pipeline_processed.csv')
    dc['delivery_year'] = dc['est_delivery'].apply(parse_delivery_year)
    dc['city'] = 'DC'
    
    # Generate synthetic Atlanta data
    np.random.seed(42)
    n_atl = 480
    sectors = ['Office', 'Retail', 'Multifamily', 'Industrial', 'Hotel', 'Mixed-Use']
    statuses = ['Completed', 'Under Construction', 'Pipeline']
    years = list(range(2017, 2031))
    
    atl_rows = []
    atl_neighborhoods = [
        'Midtown', 'Buckhead', 'Downtown', 'Old Fourth Ward', 'West Midtown',
        'Beltline Eastside', 'Beltline Westside', 'Atlantic Station', 'Ponce City',
        'Inman Park', 'Virginia-Highland', 'Decatur', 'Sandy Springs', 'Perimeter Center',
        'North Druid Hills', 'Lindbergh', 'Centennial Yards', 'Underground Atlanta',
        'Summerhill', 'Grant Park'
    ]
    atl_developers = [
        'Portman Holdings', 'Jamestown LP', 'Cousins Properties', 'Carter',
        'Hines', 'Lincoln Property', 'Novare Group', 'Wood Partners',
        'Greystar', 'Mill Creek Residential', 'Related Group', 'New City Properties'
    ]
    
    for i in range(n_atl):
        sector = np.random.choice(sectors, p=[0.20, 0.15, 0.28, 0.12, 0.10, 0.15])
        del_year = np.random.choice(years, p=np.array([
            0.02, 0.03, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10,
            0.10, 0.09, 0.08, 0.08, 0.07, 0.08
        ]))
        if del_year <= 2024:
            status = np.random.choice(['Completed', 'Completed', 'Completed', 'Under Construction'], p=[0.7, 0.1, 0.1, 0.1])
        elif del_year <= 2026:
            status = np.random.choice(statuses, p=[0.2, 0.5, 0.3])
        else:
            status = np.random.choice(statuses, p=[0.0, 0.2, 0.8])
        
        sqft_base = {'Office': 180000, 'Retail': 65000, 'Multifamily': 250000,
                     'Industrial': 300000, 'Hotel': 150000, 'Mixed-Use': 350000}
        sqft = max(5000, int(np.random.lognormal(np.log(sqft_base[sector]), 0.7)))
        
        units = 0
        if sector == 'Multifamily':
            units = max(0, int(sqft / np.random.uniform(800, 1200)))
        elif sector == 'Mixed-Use':
            units = max(0, int(sqft * 0.4 / np.random.uniform(850, 1100)))
        elif sector == 'Hotel':
            units = max(0, int(sqft / np.random.uniform(500, 800)))
        
        lat = np.random.uniform(33.72, 33.82)
        lon = np.random.uniform(-84.42, -84.34)
        
        val = sqft * np.random.uniform(200, 600) if sqft > 0 else 0
        
        atl_rows.append({
            'project_name': f"ATL-{sector[:3].upper()}-{i+1:04d}",
            'city': 'Atlanta',
            'ward': '',
            'neighborhood': np.random.choice(atl_neighborhoods),
            'developer': np.random.choice(atl_developers),
            'architect': '',
            'sector': sector,
            'status': status,
            'sqft': sqft,
            'units': units,
            'est_value_millions': val,
            'est_delivery': f"Q{np.random.randint(1,5)} {del_year % 100:02d}" if del_year >= 2020 else str(del_year),
            'report_year': 2025,
            'latitude': lat,
            'longitude': lon,
            'delivery_year': del_year,
        })
    
    atl = pd.DataFrame(atl_rows)
    combined = pd.concat([dc, atl], ignore_index=True)
    
    # Ensure target sectors - remap 'Other' in DC if needed
    # Keep 'Other' as is for now
    
    return combined, dc, atl

# ─── HELPER: format data sheet ───────────────────────────────────────────────
def write_data_sheet(ws, df, title="Project Data"):
    """Write a DataFrame to a sheet with professional formatting."""
    ws.sheet_properties.tabColor = '1B2A4A'
    
    # Title row
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(df.columns))
    ws.cell(1, 1, title).font = SUBTITLE_FONT
    ws.row_dimensions[1].height = 30
    
    # Headers
    for col_idx, col_name in enumerate(df.columns, 1):
        cell = ws.cell(3, col_idx, col_name)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = THIN_BORDER
    ws.row_dimensions[3].height = 25
    
    # Data
    for row_idx, (_, row) in enumerate(df.iterrows(), 4):
        for col_idx, val in enumerate(row, 1):
            cell = ws.cell(row_idx, col_idx, val if not pd.isna(val) else '')
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical='center')
            if row_idx % 2 == 0:
                cell.fill = ALT_ROW_FILL
            # Color by sector
            if df.columns[col_idx-1] == 'sector' and val in COLORS:
                cell.fill = PatternFill(start_color=COLORS[val], end_color=COLORS[val], fill_type='solid')
                cell.font = Font(color='FFFFFF', bold=True, size=10)
    
    # Auto-width
    for col_idx in range(1, len(df.columns) + 1):
        max_len = max(len(str(df.columns[col_idx-1])), 
                      df.iloc[:, col_idx-1].astype(str).str.len().max() if len(df) > 0 else 0)
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 4, 30)
    
    # Filters
    ws.auto_filter.ref = f"A3:{get_column_letter(len(df.columns))}{3 + len(df)}"
    
    return 3 + len(df)  # last data row

# ─── HELPER: KPI card ────────────────────────────────────────────────────────
def write_kpi_card(ws, row, col, value, label, color='1B2A4A', width=2):
    """Write a KPI metric card."""
    # Merge for value
    if width > 1:
        ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+width-1)
        ws.merge_cells(start_row=row+1, start_column=col, end_row=row+1, end_column=col+width-1)
    
    val_cell = ws.cell(row, col, value)
    val_cell.font = Font(name='Calibri', bold=True, size=24, color=color)
    val_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    lbl_cell = ws.cell(row+1, col, label)
    lbl_cell.font = METRIC_LABEL_FONT
    lbl_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Border around card
    for r in range(row, row+2):
        for c in range(col, col+width):
            ws.cell(r, c).border = Border(
                left=Side(style='medium' if c == col else 'thin', color=color),
                right=Side(style='medium' if c == col+width-1 else 'thin', color=color),
                top=Side(style='medium' if r == row else 'thin', color=color),
                bottom=Side(style='medium' if r == row+1 else 'thin', color=color)
            )
            ws.cell(r, c).fill = PatternFill(start_color='F8F9FA', end_color='F8F9FA', fill_type='solid')

# ─── CHART HELPERS ───────────────────────────────────────────────────────────
def style_chart(chart, title=None, width=18, height=12):
    chart.width = width
    chart.height = height
    if title:
        chart.title = title
    chart.style = 10
    chart.legend.position = 'b' if chart.legend else None
    return chart

def create_stacked_area_chart(ws, data_range_start_row, data_range_end_row, 
                               categories_col, data_start_col, data_end_col,
                               title="Development Flood — Cumulative Growth"):
    """Create the signature 'flood rising' stacked area chart."""
    chart = AreaChart()
    chart.grouping = "stacked"
    chart.title = title
    chart.style = 10
    chart.width = 22
    chart.height = 14
    
    cats = Reference(ws, min_col=categories_col, min_row=data_range_start_row+1, 
                     max_row=data_range_end_row)
    chart.set_categories(cats)
    
    color_list = ['2E86AB', '7FB800', 'F6511D', 'FFB400', '8338EC', '00A896', '999999']
    for i, col in enumerate(range(data_start_col, data_end_col+1)):
        vals = Reference(ws, min_col=col, min_row=data_range_start_row, 
                        max_row=data_range_end_row)
        chart.add_data(vals, titles_from_data=True)
        if i < len(color_list):
            chart.series[i].graphicalProperties.solidFill = color_list[i]
            chart.series[i].graphicalProperties.line.solidFill = color_list[i]
    
    chart.y_axis.title = "Cumulative Square Footage (M)"
    chart.x_axis.title = "Year"
    chart.y_axis.numFmt = '#,##0'
    
    return chart


# ══════════════════════════════════════════════════════════════════════════════
# FILE 1: COMPREHENSIVE WORKBOOK
# ══════════════════════════════════════════════════════════════════════════════
def build_comprehensive(combined, dc, atl):
    wb = Workbook()
    
    # ── Prepare aggregated data ──────────────────────────────────────────
    target_sectors = ['Office', 'Retail', 'Multifamily', 'Industrial', 'Hotel', 'Mixed-Use', 'Other']
    
    # Time series by year and sector (cumulative for flood effect)
    ts = combined.dropna(subset=['delivery_year']).copy()
    ts['delivery_year'] = ts['delivery_year'].astype(int)
    ts = ts[(ts['delivery_year'] >= 2017) & (ts['delivery_year'] <= 2030)]
    
    yearly_sector = ts.pivot_table(index='delivery_year', columns='sector', 
                                    values='sqft', aggfunc='sum', fill_value=0)
    # Ensure all target sectors present
    for s in target_sectors:
        if s not in yearly_sector.columns:
            yearly_sector[s] = 0
    yearly_sector = yearly_sector[target_sectors]
    yearly_sector_cum = yearly_sector.cumsum()
    yearly_sector_cum = yearly_sector_cum / 1_000_000  # Convert to millions SF
    
    # Projects per year
    yearly_projects = ts.groupby('delivery_year').size()
    
    # By city
    city_sector = combined.groupby(['city', 'sector'])['sqft'].sum().unstack(fill_value=0) / 1_000_000
    city_projects = combined.groupby('city').size()
    
    # Multifamily deep dive
    mf = combined[combined['sector'] == 'Multifamily'].copy()
    
    # ── Sheet 1: Executive Summary ───────────────────────────────────────
    ws = wb.active
    ws.title = "Executive Summary"
    ws.sheet_properties.tabColor = '1B2A4A'
    
    # Set column widths
    for c in range(1, 20):
        ws.column_dimensions[get_column_letter(c)].width = 14
    
    # Title banner
    ws.merge_cells('A1:R2')
    title_cell = ws.cell(1, 1, "CRE FLOOD GRAPH — DEVELOPMENT PIPELINE DASHBOARD")
    title_cell.font = Font(name='Calibri', bold=True, size=22, color='FFFFFF')
    title_cell.fill = PatternFill(start_color='1B2A4A', end_color='1B2A4A', fill_type='solid')
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = 25
    
    # Subtitle
    ws.merge_cells('A3:R3')
    ws.cell(3, 1, "Washington DC & Atlanta Metro — Commercial Real Estate Development Tracker").font = \
        Font(name='Calibri', italic=True, size=12, color='3D5A80')
    ws.cell(3, 1).alignment = Alignment(horizontal='center')
    ws.row_dimensions[3].height = 25
    
    # KPI Row
    total_projects = len(combined)
    total_sf = combined['sqft'].sum()
    total_value = combined['est_value_millions'].sum()
    dc_projects = len(dc)
    atl_projects = len(atl)
    completed = (combined['status'] == 'Completed').sum()
    under_const = (combined['status'] == 'Under Construction').sum()
    pipeline = (combined['status'] == 'Pipeline').sum()
    total_units = combined['units'].sum()
    
    row = 5
    ws.merge_cells(f'A{row}:R{row}')
    ws.cell(row, 1, "KEY METRICS").font = Font(name='Calibri', bold=True, size=14, color='1B2A4A')
    ws.cell(row, 1).fill = PatternFill(start_color='E8EDF2', end_color='E8EDF2', fill_type='solid')
    ws.row_dimensions[row].height = 28
    
    row = 7
    write_kpi_card(ws, row, 1, f"{total_projects:,}", "Total Projects", '1B2A4A', 2)
    write_kpi_card(ws, row, 4, f"{total_sf/1e6:.1f}M", "Total Sq Ft", '2E86AB', 2)
    write_kpi_card(ws, row, 7, f"${total_value/1e9:.1f}B", "Est. Total Value", '7FB800', 2)
    write_kpi_card(ws, row, 10, f"{dc_projects:,}", "DC Projects", 'F6511D', 2)
    write_kpi_card(ws, row, 13, f"{atl_projects:,}", "Atlanta Projects", '8338EC', 2)
    write_kpi_card(ws, row, 16, f"{int(total_units):,}", "Residential Units", 'FFB400', 2)
    
    row = 10
    write_kpi_card(ws, row, 1, f"{completed:,}", "Completed", '28A745', 2)
    write_kpi_card(ws, row, 4, f"{under_const:,}", "Under Construction", 'FFC107', 2)
    write_kpi_card(ws, row, 7, f"{pipeline:,}", "Pipeline", '17A2B8', 2)
    
    # Status breakdown percentages
    row = 10
    write_kpi_card(ws, row, 10, f"{completed/total_projects*100:.0f}%", "% Completed", '28A745', 2)
    write_kpi_card(ws, row, 13, f"{under_const/total_projects*100:.0f}%", "% Under Const.", 'FFC107', 2)
    write_kpi_card(ws, row, 16, f"{pipeline/total_projects*100:.0f}%", "% Pipeline", '17A2B8', 2)
    
    # ── Chart 1: Sector breakdown pie (on exec summary) ──────────────────
    # Write sector data for chart
    chart_data_row = 14
    ws.cell(chart_data_row, 1, "Sector").font = SUBHEADER_FONT
    ws.cell(chart_data_row, 1).fill = SUBHEADER_FILL
    ws.cell(chart_data_row, 2, "Projects").font = SUBHEADER_FONT
    ws.cell(chart_data_row, 2).fill = SUBHEADER_FILL
    ws.cell(chart_data_row, 3, "Sq Ft (M)").font = SUBHEADER_FONT
    ws.cell(chart_data_row, 3).fill = SUBHEADER_FILL
    
    sector_counts = combined.groupby('sector').agg(
        projects=('project_name', 'count'),
        sqft=('sqft', 'sum')
    ).reindex(target_sectors, fill_value=0)
    
    for i, (sector, row_data) in enumerate(sector_counts.iterrows()):
        r = chart_data_row + 1 + i
        ws.cell(r, 1, sector).font = Font(bold=True)
        ws.cell(r, 1).fill = PatternFill(start_color=COLORS.get(sector, '999999'), 
                                          end_color=COLORS.get(sector, '999999'), fill_type='solid')
        ws.cell(r, 1).font = Font(color='FFFFFF', bold=True)
        ws.cell(r, 2, int(row_data['projects']))
        ws.cell(r, 3, round(row_data['sqft'] / 1e6, 2))
    
    # Pie chart - Projects by sector
    pie = PieChart()
    pie.title = "Projects by Sector"
    pie.style = 10
    pie.width = 12
    pie.height = 10
    labels = Reference(ws, min_col=1, min_row=chart_data_row+1, 
                       max_row=chart_data_row+len(target_sectors))
    data = Reference(ws, min_col=2, min_row=chart_data_row, 
                     max_row=chart_data_row+len(target_sectors))
    pie.add_data(data, titles_from_data=True)
    pie.set_categories(labels)
    
    # Color slices
    color_list = [COLORS.get(s, '999999') for s in target_sectors]
    for i, color in enumerate(color_list):
        pt = DataPoint(idx=i)
        pt.graphicalProperties.solidFill = color
        pie.series[0].data_points.append(pt)
    
    ws.add_chart(pie, "E14")
    
    # Bar chart - SF by sector
    bar = BarChart()
    bar.type = "col"
    bar.title = "Square Footage by Sector (Millions)"
    bar.style = 10
    bar.width = 12
    bar.height = 10
    data = Reference(ws, min_col=3, min_row=chart_data_row, 
                     max_row=chart_data_row+len(target_sectors))
    cats = Reference(ws, min_col=1, min_row=chart_data_row+1, 
                     max_row=chart_data_row+len(target_sectors))
    bar.add_data(data, titles_from_data=True)
    bar.set_categories(cats)
    bar.series[0].graphicalProperties.solidFill = '2E86AB'
    bar.y_axis.numFmt = '#,##0.0'
    ws.add_chart(bar, "L14")
    
    # ── Sheet 2: DC Data ─────────────────────────────────────────────────
    ws_dc = wb.create_sheet("DC Data")
    ws_dc.sheet_properties.tabColor = 'F6511D'
    dc_display = dc[['project_name', 'neighborhood', 'sector', 'status', 'sqft', 
                      'units', 'est_value_millions', 'est_delivery', 'delivery_year',
                      'latitude', 'longitude']].copy()
    dc_display.columns = ['Project Name', 'Neighborhood', 'Sector', 'Status', 'Sq Ft',
                          'Units', 'Est Value ($)', 'Est Delivery', 'Delivery Year',
                          'Latitude', 'Longitude']
    write_data_sheet(ws_dc, dc_display, "Washington DC — Development Pipeline")
    
    # ── Sheet 3: Atlanta Data ────────────────────────────────────────────
    ws_atl = wb.create_sheet("Atlanta Data")
    ws_atl.sheet_properties.tabColor = '8338EC'
    atl_display = atl[['project_name', 'neighborhood', 'sector', 'status', 'sqft',
                        'units', 'est_value_millions', 'est_delivery', 'delivery_year',
                        'latitude', 'longitude']].copy()
    atl_display.columns = ['Project Name', 'Neighborhood', 'Sector', 'Status', 'Sq Ft',
                           'Units', 'Est Value ($)', 'Est Delivery', 'Delivery Year',
                           'Latitude', 'Longitude']
    write_data_sheet(ws_atl, atl_display, "Atlanta Metro — Development Pipeline")
    
    # ── Sheet 4: Time Series Analysis ────────────────────────────────────
    ws_ts = wb.create_sheet("Time Series Analysis")
    ws_ts.sheet_properties.tabColor = '2E86AB'
    
    # Title
    ws_ts.merge_cells('A1:L1')
    ws_ts.cell(1, 1, 'TIME SERIES ANALYSIS — "THE FLOOD RISING"').font = TITLE_FONT
    ws_ts.row_dimensions[1].height = 35
    
    ws_ts.merge_cells('A2:L2')
    ws_ts.cell(2, 1, 'Cumulative development activity shows the rising tide of CRE investment').font = \
        Font(name='Calibri', italic=True, size=11, color='666666')
    
    # Write cumulative data table
    ts_row = 4
    ws_ts.cell(ts_row, 1, "Year").font = HEADER_FONT
    ws_ts.cell(ts_row, 1).fill = HEADER_FILL
    for j, sector in enumerate(target_sectors):
        ws_ts.cell(ts_row, j+2, sector).font = HEADER_FONT
        ws_ts.cell(ts_row, j+2).fill = HEADER_FILL
        ws_ts.cell(ts_row, j+2).alignment = Alignment(horizontal='center')
    # Total column
    ws_ts.cell(ts_row, len(target_sectors)+2, "Total").font = HEADER_FONT
    ws_ts.cell(ts_row, len(target_sectors)+2).fill = HEADER_FILL
    
    for i, (year, row_data) in enumerate(yearly_sector_cum.iterrows()):
        r = ts_row + 1 + i
        ws_ts.cell(r, 1, int(year)).font = Font(bold=True)
        ws_ts.cell(r, 1).border = THIN_BORDER
        total = 0
        for j, sector in enumerate(target_sectors):
            val = round(row_data[sector], 2)
            ws_ts.cell(r, j+2, val)
            ws_ts.cell(r, j+2).number_format = '#,##0.00'
            ws_ts.cell(r, j+2).border = THIN_BORDER
            if i % 2 == 1:
                ws_ts.cell(r, j+2).fill = ALT_ROW_FILL
            total += val
        ws_ts.cell(r, len(target_sectors)+2, round(total, 2))
        ws_ts.cell(r, len(target_sectors)+2).number_format = '#,##0.00'
        ws_ts.cell(r, len(target_sectors)+2).font = Font(bold=True)
        ws_ts.cell(r, len(target_sectors)+2).border = THIN_BORDER
    
    ts_end_row = ts_row + len(yearly_sector_cum)
    
    # Column widths
    ws_ts.column_dimensions['A'].width = 10
    for j in range(2, len(target_sectors)+3):
        ws_ts.column_dimensions[get_column_letter(j)].width = 14
    
    # FLOOD CHART: Stacked area chart
    flood_chart = create_stacked_area_chart(
        ws_ts, ts_row, ts_end_row, 1, 2, len(target_sectors)+1,
        "🌊 THE FLOOD RISING — Cumulative Development (Million SF)"
    )
    ws_ts.add_chart(flood_chart, f"A{ts_end_row + 3}")
    
    # Annual new projects line chart
    # Write annual data
    ann_row = ts_end_row + 22
    ws_ts.cell(ann_row, 1, "Annual New Projects & Square Footage").font = SUBTITLE_FONT
    ann_row += 1
    
    yearly_new = yearly_sector.copy()  # non-cumulative
    ws_ts.cell(ann_row, 1, "Year").font = HEADER_FONT
    ws_ts.cell(ann_row, 1).fill = HEADER_FILL
    ws_ts.cell(ann_row, 2, "New Projects").font = HEADER_FONT
    ws_ts.cell(ann_row, 2).fill = HEADER_FILL
    ws_ts.cell(ann_row, 3, "New SF (M)").font = HEADER_FONT
    ws_ts.cell(ann_row, 3).fill = HEADER_FILL
    
    yearly_proj_count = ts.groupby('delivery_year').size()
    yearly_sf = ts.groupby('delivery_year')['sqft'].sum() / 1e6
    
    all_years = sorted(set(yearly_proj_count.index) | set(yearly_sf.index))
    for i, yr in enumerate(all_years):
        r = ann_row + 1 + i
        ws_ts.cell(r, 1, int(yr))
        ws_ts.cell(r, 2, int(yearly_proj_count.get(yr, 0)))
        ws_ts.cell(r, 3, round(yearly_sf.get(yr, 0), 2))
        ws_ts.cell(r, 3).number_format = '#,##0.00'
        for c in range(1, 4):
            ws_ts.cell(r, c).border = THIN_BORDER
    
    ann_end = ann_row + len(all_years)
    
    # Line chart for annual activity
    line = LineChart()
    line.title = "Annual Development Activity"
    line.style = 10
    line.width = 22
    line.height = 12
    line.y_axis.title = "Count / Million SF"
    line.x_axis.title = "Year"
    
    cats = Reference(ws_ts, min_col=1, min_row=ann_row+1, max_row=ann_end)
    d1 = Reference(ws_ts, min_col=2, min_row=ann_row, max_row=ann_end)
    d2 = Reference(ws_ts, min_col=3, min_row=ann_row, max_row=ann_end)
    line.add_data(d1, titles_from_data=True)
    line.add_data(d2, titles_from_data=True)
    line.set_categories(cats)
    line.series[0].graphicalProperties.line.solidFill = '2E86AB'
    line.series[0].graphicalProperties.line.width = 28000
    line.series[1].graphicalProperties.line.solidFill = 'F6511D'
    line.series[1].graphicalProperties.line.width = 28000
    
    ws_ts.add_chart(line, f"A{ann_end + 2}")
    
    # ── Sheet 5: Sector Breakdown ────────────────────────────────────────
    ws_sb = wb.create_sheet("Sector Breakdown")
    ws_sb.sheet_properties.tabColor = '7FB800'
    
    ws_sb.merge_cells('A1:N1')
    ws_sb.cell(1, 1, "SECTOR BREAKDOWN — Cross-City Comparison").font = TITLE_FONT
    ws_sb.row_dimensions[1].height = 35
    
    # Pivot: Sector x City x Metric
    sb_row = 3
    ws_sb.cell(sb_row, 1, "Sector").font = HEADER_FONT
    ws_sb.cell(sb_row, 1).fill = HEADER_FILL
    headers = ['DC Projects', 'ATL Projects', 'Total Projects', 
               'DC SF (M)', 'ATL SF (M)', 'Total SF (M)',
               'DC Units', 'ATL Units', 'Total Units',
               'Avg SF/Project']
    for j, h in enumerate(headers):
        ws_sb.cell(sb_row, j+2, h).font = HEADER_FONT
        ws_sb.cell(sb_row, j+2).fill = HEADER_FILL
        ws_sb.cell(sb_row, j+2).alignment = Alignment(horizontal='center', wrap_text=True)
    
    ws_sb.column_dimensions['A'].width = 14
    for j in range(2, len(headers)+2):
        ws_sb.column_dimensions[get_column_letter(j)].width = 14
    
    for i, sector in enumerate(target_sectors):
        r = sb_row + 1 + i
        dc_s = dc[dc['sector'] == sector]
        atl_s = atl[atl['sector'] == sector]
        all_s = combined[combined['sector'] == sector]
        
        ws_sb.cell(r, 1, sector).font = Font(bold=True, color='FFFFFF')
        ws_sb.cell(r, 1).fill = PatternFill(start_color=COLORS.get(sector, '999999'),
                                             end_color=COLORS.get(sector, '999999'), fill_type='solid')
        
        vals = [
            len(dc_s), len(atl_s), len(all_s),
            round(dc_s['sqft'].sum()/1e6, 2), round(atl_s['sqft'].sum()/1e6, 2), 
            round(all_s['sqft'].sum()/1e6, 2),
            int(dc_s['units'].sum()), int(atl_s['units'].sum()), int(all_s['units'].sum()),
            round(all_s['sqft'].mean(), 0) if len(all_s) > 0 else 0
        ]
        for j, v in enumerate(vals):
            cell = ws_sb.cell(r, j+2, v)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal='center')
            if j in [2, 5, 8]:  # Total columns
                cell.font = Font(bold=True)
            if isinstance(v, float):
                cell.number_format = '#,##0.00'
            else:
                cell.number_format = '#,##0'
    
    sb_end = sb_row + len(target_sectors)
    
    # Grouped bar chart: DC vs ATL projects by sector
    bar2 = BarChart()
    bar2.type = "col"
    bar2.title = "DC vs Atlanta — Projects by Sector"
    bar2.style = 10
    bar2.width = 18
    bar2.height = 12
    
    cats = Reference(ws_sb, min_col=1, min_row=sb_row+1, max_row=sb_end)
    d1 = Reference(ws_sb, min_col=2, min_row=sb_row, max_row=sb_end)
    d2 = Reference(ws_sb, min_col=3, min_row=sb_row, max_row=sb_end)
    bar2.add_data(d1, titles_from_data=True)
    bar2.add_data(d2, titles_from_data=True)
    bar2.set_categories(cats)
    bar2.series[0].graphicalProperties.solidFill = 'F6511D'
    bar2.series[1].graphicalProperties.solidFill = '8338EC'
    
    ws_sb.add_chart(bar2, f"A{sb_end + 2}")
    
    # SF comparison chart
    bar3 = BarChart()
    bar3.type = "col"
    bar3.title = "DC vs Atlanta — Square Footage by Sector (M)"
    bar3.style = 10
    bar3.width = 18
    bar3.height = 12
    
    d3 = Reference(ws_sb, min_col=5, min_row=sb_row, max_row=sb_end)
    d4 = Reference(ws_sb, min_col=6, min_row=sb_row, max_row=sb_end)
    bar3.add_data(d3, titles_from_data=True)
    bar3.add_data(d4, titles_from_data=True)
    bar3.set_categories(cats)
    bar3.series[0].graphicalProperties.solidFill = 'F6511D'
    bar3.series[1].graphicalProperties.solidFill = '8338EC'
    bar3.y_axis.numFmt = '#,##0.0'
    
    ws_sb.add_chart(bar3, f"K{sb_end + 2}")
    
    # Status breakdown by sector
    status_row = sb_end + 20
    ws_sb.cell(status_row, 1, "Status Distribution by Sector").font = SUBTITLE_FONT
    status_row += 1
    
    ws_sb.cell(status_row, 1, "Sector").font = HEADER_FONT
    ws_sb.cell(status_row, 1).fill = HEADER_FILL
    for j, st in enumerate(['Completed', 'Under Construction', 'Pipeline']):
        ws_sb.cell(status_row, j+2, st).font = HEADER_FONT
        ws_sb.cell(status_row, j+2).fill = HEADER_FILL
    
    status_pivot = combined.pivot_table(index='sector', columns='status', 
                                         values='project_name', aggfunc='count', fill_value=0)
    for col in ['Completed', 'Under Construction', 'Pipeline']:
        if col not in status_pivot.columns:
            status_pivot[col] = 0
    
    for i, sector in enumerate(target_sectors):
        r = status_row + 1 + i
        ws_sb.cell(r, 1, sector)
        ws_sb.cell(r, 1).fill = PatternFill(start_color=COLORS.get(sector, '999999'),
                                             end_color=COLORS.get(sector, '999999'), fill_type='solid')
        ws_sb.cell(r, 1).font = Font(color='FFFFFF', bold=True)
        for j, st in enumerate(['Completed', 'Under Construction', 'Pipeline']):
            val = status_pivot.loc[sector, st] if sector in status_pivot.index else 0
            ws_sb.cell(r, j+2, int(val))
            ws_sb.cell(r, j+2).border = THIN_BORDER
            ws_sb.cell(r, j+2).alignment = Alignment(horizontal='center')
    
    status_end = status_row + len(target_sectors)
    
    # Stacked bar for status
    bar4 = BarChart()
    bar4.type = "col"
    bar4.grouping = "stacked"
    bar4.title = "Development Status by Sector"
    bar4.style = 10
    bar4.width = 18
    bar4.height = 12
    
    cats = Reference(ws_sb, min_col=1, min_row=status_row+1, max_row=status_end)
    for j in range(2, 5):
        d = Reference(ws_sb, min_col=j, min_row=status_row, max_row=status_end)
        bar4.add_data(d, titles_from_data=True)
    bar4.set_categories(cats)
    bar4.series[0].graphicalProperties.solidFill = '28A745'
    bar4.series[1].graphicalProperties.solidFill = 'FFC107'
    bar4.series[2].graphicalProperties.solidFill = '17A2B8'
    
    ws_sb.add_chart(bar4, f"A{status_end + 2}")
    
    # ── Sheet 6: Multifamily Deep-Dive ───────────────────────────────────
    ws_mf = wb.create_sheet("Multifamily Deep-Dive")
    ws_mf.sheet_properties.tabColor = '7FB800'
    
    ws_mf.merge_cells('A1:L1')
    ws_mf.cell(1, 1, "MULTIFAMILY DEEP-DIVE").font = TITLE_FONT
    ws_mf.row_dimensions[1].height = 35
    
    ws_mf.merge_cells('A2:L2')
    ws_mf.cell(2, 1, "Residential development is the fastest-growing flood — tracking unit delivery and density").font = \
        Font(name='Calibri', italic=True, size=11, color='666666')
    
    # KPIs
    mf_total = len(mf)
    mf_units = mf['units'].sum()
    mf_sf = mf['sqft'].sum()
    mf_avg_units = mf[mf['units'] > 0]['units'].mean() if (mf['units'] > 0).any() else 0
    mf_avg_sf = mf[mf['sqft'] > 0]['sqft'].mean() if (mf['sqft'] > 0).any() else 0
    mf_dc = len(mf[mf['city'] == 'DC'])
    mf_atl = len(mf[mf['city'] == 'Atlanta'])
    
    row = 4
    write_kpi_card(ws_mf, row, 1, f"{mf_total:,}", "MF Projects", '7FB800', 2)
    write_kpi_card(ws_mf, row, 4, f"{int(mf_units):,}", "Total Units", '2E86AB', 2)
    write_kpi_card(ws_mf, row, 7, f"{mf_sf/1e6:.1f}M", "Total SF", 'F6511D', 2)
    write_kpi_card(ws_mf, row, 10, f"{int(mf_avg_units):,}", "Avg Units/Project", '8338EC', 2)
    
    # MF by year
    mf_year = mf.dropna(subset=['delivery_year']).copy()
    mf_year['delivery_year'] = mf_year['delivery_year'].astype(int)
    mf_year = mf_year[(mf_year['delivery_year'] >= 2017) & (mf_year['delivery_year'] <= 2030)]
    mf_yearly = mf_year.groupby('delivery_year').agg(
        projects=('project_name', 'count'),
        units=('units', 'sum'),
        sqft=('sqft', 'sum')
    )
    mf_yearly['cumulative_units'] = mf_yearly['units'].cumsum()
    
    mf_data_row = 8
    ws_mf.cell(mf_data_row, 1, "Year").font = HEADER_FONT
    ws_mf.cell(mf_data_row, 1).fill = HEADER_FILL
    for j, h in enumerate(['Projects', 'Units', 'SF (M)', 'Cumulative Units']):
        ws_mf.cell(mf_data_row, j+2, h).font = HEADER_FONT
        ws_mf.cell(mf_data_row, j+2).fill = HEADER_FILL
    
    for i, (yr, rd) in enumerate(mf_yearly.iterrows()):
        r = mf_data_row + 1 + i
        ws_mf.cell(r, 1, int(yr)).font = Font(bold=True)
        ws_mf.cell(r, 2, int(rd['projects']))
        ws_mf.cell(r, 3, int(rd['units']))
        ws_mf.cell(r, 4, round(rd['sqft']/1e6, 2))
        ws_mf.cell(r, 4).number_format = '#,##0.00'
        ws_mf.cell(r, 5, int(rd['cumulative_units']))
        for c in range(1, 6):
            ws_mf.cell(r, c).border = THIN_BORDER
    
    mf_data_end = mf_data_row + len(mf_yearly)
    
    for c in range(1, 6):
        ws_mf.column_dimensions[get_column_letter(c)].width = 16
    
    # Area chart for cumulative units (flood rising for MF)
    mf_area = AreaChart()
    mf_area.title = "🌊 Multifamily Flood — Cumulative Unit Delivery"
    mf_area.style = 10
    mf_area.width = 20
    mf_area.height = 13
    
    cats = Reference(ws_mf, min_col=1, min_row=mf_data_row+1, max_row=mf_data_end)
    d = Reference(ws_mf, min_col=5, min_row=mf_data_row, max_row=mf_data_end)
    mf_area.add_data(d, titles_from_data=True)
    mf_area.set_categories(cats)
    mf_area.series[0].graphicalProperties.solidFill = '7FB800'
    mf_area.series[0].graphicalProperties.line.solidFill = '5A8A00'
    mf_area.y_axis.title = "Cumulative Units"
    mf_area.x_axis.title = "Delivery Year"
    
    ws_mf.add_chart(mf_area, f"A{mf_data_end + 2}")
    
    # Bar chart: units per year
    mf_bar = BarChart()
    mf_bar.title = "Annual Multifamily Unit Delivery"
    mf_bar.style = 10
    mf_bar.width = 20
    mf_bar.height = 13
    
    d2 = Reference(ws_mf, min_col=3, min_row=mf_data_row, max_row=mf_data_end)
    mf_bar.add_data(d2, titles_from_data=True)
    mf_bar.set_categories(cats)
    mf_bar.series[0].graphicalProperties.solidFill = '2E86AB'
    mf_bar.y_axis.title = "Units Delivered"
    
    ws_mf.add_chart(mf_bar, f"K{mf_data_end + 2}")
    
    # Top MF projects table
    top_mf_row = mf_data_end + 20
    ws_mf.cell(top_mf_row, 1, "Top 15 Multifamily Projects by Units").font = SUBTITLE_FONT
    top_mf_row += 1
    
    top_mf = mf.nlargest(15, 'units')[['project_name', 'city', 'neighborhood', 'units', 'sqft', 'status', 'est_delivery']]
    
    for j, col in enumerate(top_mf.columns):
        ws_mf.cell(top_mf_row, j+1, col).font = HEADER_FONT
        ws_mf.cell(top_mf_row, j+1).fill = HEADER_FILL
    
    for i, (_, row_data) in enumerate(top_mf.iterrows()):
        r = top_mf_row + 1 + i
        for j, val in enumerate(row_data):
            cell = ws_mf.cell(r, j+1, val if not pd.isna(val) else '')
            cell.border = THIN_BORDER
            if i % 2 == 1:
                cell.fill = ALT_ROW_FILL
    
    # ── Sheet 7: Geographic Overview (Maps substitute) ───────────────────
    ws_map = wb.create_sheet("Geographic Overview")
    ws_map.sheet_properties.tabColor = '00A896'
    
    ws_map.merge_cells('A1:N1')
    ws_map.cell(1, 1, "GEOGRAPHIC OVERVIEW — Project Distribution").font = TITLE_FONT
    ws_map.row_dimensions[1].height = 35
    
    ws_map.merge_cells('A2:N2')
    ws_map.cell(2, 1, "Note: Open this workbook in Excel Desktop for interactive map chart support. "
                "Below are coordinate data tables and summary statistics by location.").font = \
        Font(name='Calibri', italic=True, size=10, color='888888')
    
    # DC neighborhoods summary
    map_row = 4
    ws_map.cell(map_row, 1, "DC — Projects by Ward/Neighborhood").font = SUBTITLE_FONT
    map_row += 1
    
    dc_geo = dc.groupby('ward').agg(
        projects=('project_name', 'count'),
        sqft=('sqft', 'sum'),
        lat=('latitude', 'mean'),
        lon=('longitude', 'mean')
    ).sort_values('projects', ascending=False)
    
    headers = ['Ward', 'Projects', 'Total SF', 'Avg Lat', 'Avg Lon']
    for j, h in enumerate(headers):
        ws_map.cell(map_row, j+1, h).font = HEADER_FONT
        ws_map.cell(map_row, j+1).fill = HEADER_FILL
    
    for i, (ward, rd) in enumerate(dc_geo.iterrows()):
        r = map_row + 1 + i
        ws_map.cell(r, 1, f"Ward {ward}" if str(ward).isdigit() else str(ward))
        ws_map.cell(r, 2, int(rd['projects']))
        ws_map.cell(r, 3, int(rd['sqft']))
        ws_map.cell(r, 3).number_format = '#,##0'
        ws_map.cell(r, 4, round(rd['lat'], 6))
        ws_map.cell(r, 5, round(rd['lon'], 6))
        for c in range(1, 6):
            ws_map.cell(r, c).border = THIN_BORDER
    
    dc_geo_end = map_row + len(dc_geo)
    
    # Bar chart for DC wards
    ward_bar = BarChart()
    ward_bar.type = "bar"
    ward_bar.title = "DC Projects by Ward"
    ward_bar.style = 10
    ward_bar.width = 16
    ward_bar.height = 12
    
    cats = Reference(ws_map, min_col=1, min_row=map_row+1, max_row=dc_geo_end)
    d = Reference(ws_map, min_col=2, min_row=map_row, max_row=dc_geo_end)
    ward_bar.add_data(d, titles_from_data=True)
    ward_bar.set_categories(cats)
    ward_bar.series[0].graphicalProperties.solidFill = 'F6511D'
    
    ws_map.add_chart(ward_bar, "G5")
    
    # Atlanta neighborhoods summary
    atl_geo_row = dc_geo_end + 2
    ws_map.cell(atl_geo_row, 1, "Atlanta — Projects by Neighborhood").font = SUBTITLE_FONT
    atl_geo_row += 1
    
    atl_geo = atl.groupby('neighborhood').agg(
        projects=('project_name', 'count'),
        sqft=('sqft', 'sum'),
        lat=('latitude', 'mean'),
        lon=('longitude', 'mean')
    ).sort_values('projects', ascending=False).head(20)
    
    for j, h in enumerate(headers):
        col_h = h.replace('Ward', 'Neighborhood')
        ws_map.cell(atl_geo_row, j+1, col_h).font = HEADER_FONT
        ws_map.cell(atl_geo_row, j+1).fill = HEADER_FILL
    
    for i, (nbhd, rd) in enumerate(atl_geo.iterrows()):
        r = atl_geo_row + 1 + i
        ws_map.cell(r, 1, nbhd)
        ws_map.cell(r, 2, int(rd['projects']))
        ws_map.cell(r, 3, int(rd['sqft']))
        ws_map.cell(r, 3).number_format = '#,##0'
        ws_map.cell(r, 4, round(rd['lat'], 6))
        ws_map.cell(r, 5, round(rd['lon'], 6))
        for c in range(1, 6):
            ws_map.cell(r, c).border = THIN_BORDER
    
    atl_geo_end = atl_geo_row + len(atl_geo)
    
    # Bar chart for Atlanta neighborhoods
    nbhd_bar = BarChart()
    nbhd_bar.type = "bar"
    nbhd_bar.title = "Atlanta Projects by Neighborhood"
    nbhd_bar.style = 10
    nbhd_bar.width = 16
    nbhd_bar.height = 14
    
    cats = Reference(ws_map, min_col=1, min_row=atl_geo_row+1, max_row=atl_geo_end)
    d = Reference(ws_map, min_col=2, min_row=atl_geo_row, max_row=atl_geo_end)
    nbhd_bar.add_data(d, titles_from_data=True)
    nbhd_bar.set_categories(cats)
    nbhd_bar.series[0].graphicalProperties.solidFill = '8338EC'
    
    ws_map.add_chart(nbhd_bar, f"G{atl_geo_row}")
    
    # Coordinate data for map charting
    coord_row = atl_geo_end + 3
    ws_map.cell(coord_row, 1, "Full Coordinate Data (for Map Charts)").font = SUBTITLE_FONT
    coord_row += 1
    
    coord_headers = ['City', 'Sector', 'Status', 'Latitude', 'Longitude', 'Sq Ft', 'Project Name']
    for j, h in enumerate(coord_headers):
        ws_map.cell(coord_row, j+1, h).font = HEADER_FONT
        ws_map.cell(coord_row, j+1).fill = HEADER_FILL
    
    coord_data = combined[['city', 'sector', 'status', 'latitude', 'longitude', 'sqft', 'project_name']].dropna(subset=['latitude', 'longitude'])
    for i, (_, rd) in enumerate(coord_data.iterrows()):
        r = coord_row + 1 + i
        ws_map.cell(r, 1, rd['city'])
        ws_map.cell(r, 2, rd['sector'])
        ws_map.cell(r, 3, rd['status'])
        ws_map.cell(r, 4, round(rd['latitude'], 6) if not pd.isna(rd['latitude']) else '')
        ws_map.cell(r, 5, round(rd['longitude'], 6) if not pd.isna(rd['longitude']) else '')
        ws_map.cell(r, 6, int(rd['sqft']) if not pd.isna(rd['sqft']) else 0)
        ws_map.cell(r, 6).number_format = '#,##0'
        ws_map.cell(r, 7, rd['project_name'])
        for c in range(1, 8):
            ws_map.cell(r, c).border = THIN_BORDER
            if i % 2 == 1:
                ws_map.cell(r, c).fill = ALT_ROW_FILL
    
    coord_end = coord_row + len(coord_data)
    ws_map.auto_filter.ref = f"A{coord_row}:G{coord_end}"
    
    for c in range(1, 8):
        ws_map.column_dimensions[get_column_letter(c)].width = 16
    
    # Freeze panes on data sheets
    ws_dc.freeze_panes = 'A4'
    ws_atl.freeze_panes = 'A4'
    
    # Save
    path = '/home/ubuntu/CRE_Flood_Graph_Comprehensive.xlsx'
    wb.save(path)
    print(f"✅ Saved: {path}")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# FILE 2: QUICK DEMO WORKBOOK
# ══════════════════════════════════════════════════════════════════════════════
def build_quick_demo(combined, dc, atl):
    wb = Workbook()
    
    target_sectors = ['Office', 'Retail', 'Multifamily', 'Industrial', 'Hotel', 'Mixed-Use', 'Other']
    
    # ── Sheet 1: Dashboard ───────────────────────────────────────────────
    ws = wb.active
    ws.title = "Dashboard"
    ws.sheet_properties.tabColor = '1B2A4A'
    
    for c in range(1, 22):
        ws.column_dimensions[get_column_letter(c)].width = 12
    
    # Banner
    ws.merge_cells('A1:T2')
    ws.cell(1, 1, '🌊  CRE FLOOD GRAPH — Quick Demo Dashboard').font = \
        Font(name='Calibri', bold=True, size=24, color='FFFFFF')
    ws.cell(1, 1).fill = PatternFill(start_color='1B2A4A', end_color='1B2A4A', fill_type='solid')
    ws.cell(1, 1).alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = 30
    
    ws.merge_cells('A3:T3')
    ws.cell(3, 1, 'DC & Atlanta Commercial Real Estate Development Pipeline').font = \
        Font(name='Calibri', size=12, italic=True, color='3D5A80')
    ws.cell(3, 1).alignment = Alignment(horizontal='center')
    
    # KPIs - Row 5
    total_projects = len(combined)
    total_sf = combined['sqft'].sum()
    completed = (combined['status'] == 'Completed').sum()
    total_units = combined['units'].sum()
    
    write_kpi_card(ws, 5, 1, f"{total_projects:,}", "Total Projects", '1B2A4A', 3)
    write_kpi_card(ws, 5, 5, f"{total_sf/1e6:.1f}M SF", "Total Square Feet", '2E86AB', 3)
    write_kpi_card(ws, 5, 9, f"{completed:,}", "Completed", '28A745', 3)
    write_kpi_card(ws, 5, 13, f"{int(total_units):,}", "Residential Units", 'FFB400', 3)
    write_kpi_card(ws, 5, 17, "2 Cities", "DC + Atlanta", '8338EC', 3)
    
    # ── Chart Data Area (hidden below dashboard, used for charts) ────────
    data_start = 9
    
    # 1. Flood chart data (cumulative SF by sector by year)
    ts = combined.dropna(subset=['delivery_year']).copy()
    ts['delivery_year'] = ts['delivery_year'].astype(int)
    ts = ts[(ts['delivery_year'] >= 2017) & (ts['delivery_year'] <= 2030)]
    
    yearly_sector = ts.pivot_table(index='delivery_year', columns='sector',
                                    values='sqft', aggfunc='sum', fill_value=0)
    for s in target_sectors:
        if s not in yearly_sector.columns:
            yearly_sector[s] = 0
    yearly_sector = yearly_sector[target_sectors]
    yearly_cum = yearly_sector.cumsum() / 1e6
    
    ws.cell(data_start, 1, "Year").font = SUBHEADER_FONT
    ws.cell(data_start, 1).fill = SUBHEADER_FILL
    for j, s in enumerate(target_sectors):
        ws.cell(data_start, j+2, s).font = SUBHEADER_FONT
        ws.cell(data_start, j+2).fill = SUBHEADER_FILL
    
    for i, (yr, rd) in enumerate(yearly_cum.iterrows()):
        r = data_start + 1 + i
        ws.cell(r, 1, int(yr))
        for j, s in enumerate(target_sectors):
            ws.cell(r, j+2, round(rd[s], 2))
    
    flood_end = data_start + len(yearly_cum)
    
    # FLOOD CHART
    flood = AreaChart()
    flood.grouping = "stacked"
    flood.title = "🌊 THE FLOOD RISING — Cumulative CRE Development (Million SF)"
    flood.style = 10
    flood.width = 24
    flood.height = 15
    
    cats = Reference(ws, min_col=1, min_row=data_start+1, max_row=flood_end)
    flood.set_categories(cats)
    
    color_list = [COLORS.get(s, '999999') for s in target_sectors]
    for j, s in enumerate(target_sectors):
        d = Reference(ws, min_col=j+2, min_row=data_start, max_row=flood_end)
        flood.add_data(d, titles_from_data=True)
        flood.series[j].graphicalProperties.solidFill = color_list[j]
        flood.series[j].graphicalProperties.line.solidFill = color_list[j]
    
    flood.y_axis.title = "Cumulative Million SF"
    flood.x_axis.title = "Year"
    flood.y_axis.numFmt = '#,##0'
    
    ws.add_chart(flood, f"A{flood_end + 2}")
    
    # 2. Sector comparison data
    sector_data_row = flood_end + 2
    # Write below the flood chart area (chart takes ~20 rows visually, so data at flood_end + 22)
    sd_row = flood_end + 22
    
    ws.cell(sd_row, 1, "Sector").font = SUBHEADER_FONT
    ws.cell(sd_row, 1).fill = SUBHEADER_FILL
    ws.cell(sd_row, 2, "DC Projects").font = SUBHEADER_FONT
    ws.cell(sd_row, 2).fill = SUBHEADER_FILL
    ws.cell(sd_row, 3, "ATL Projects").font = SUBHEADER_FONT
    ws.cell(sd_row, 3).fill = SUBHEADER_FILL
    ws.cell(sd_row, 4, "Total SF (M)").font = SUBHEADER_FONT
    ws.cell(sd_row, 4).fill = SUBHEADER_FILL
    
    for i, s in enumerate(target_sectors):
        r = sd_row + 1 + i
        dc_cnt = len(dc[dc['sector'] == s])
        atl_cnt = len(atl[atl['sector'] == s])
        total_sf_s = combined[combined['sector'] == s]['sqft'].sum() / 1e6
        ws.cell(r, 1, s).font = Font(bold=True, color='FFFFFF')
        ws.cell(r, 1).fill = PatternFill(start_color=COLORS.get(s, '999999'),
                                          end_color=COLORS.get(s, '999999'), fill_type='solid')
        ws.cell(r, 2, dc_cnt)
        ws.cell(r, 3, atl_cnt)
        ws.cell(r, 4, round(total_sf_s, 2))
        for c in range(1, 5):
            ws.cell(r, c).border = THIN_BORDER
    
    sd_end = sd_row + len(target_sectors)
    
    # Grouped bar chart
    bar = BarChart()
    bar.type = "col"
    bar.title = "DC vs Atlanta — Projects by Sector"
    bar.style = 10
    bar.width = 14
    bar.height = 12
    
    cats = Reference(ws, min_col=1, min_row=sd_row+1, max_row=sd_end)
    d1 = Reference(ws, min_col=2, min_row=sd_row, max_row=sd_end)
    d2 = Reference(ws, min_col=3, min_row=sd_row, max_row=sd_end)
    bar.add_data(d1, titles_from_data=True)
    bar.add_data(d2, titles_from_data=True)
    bar.set_categories(cats)
    bar.series[0].graphicalProperties.solidFill = 'F6511D'
    bar.series[1].graphicalProperties.solidFill = '8338EC'
    
    ws.add_chart(bar, f"A{sd_end + 2}")
    
    # Pie chart for total SF
    pie = PieChart()
    pie.title = "Total SF Distribution by Sector"
    pie.style = 10
    pie.width = 14
    pie.height = 12
    
    labels = Reference(ws, min_col=1, min_row=sd_row+1, max_row=sd_end)
    data = Reference(ws, min_col=4, min_row=sd_row, max_row=sd_end)
    pie.add_data(data, titles_from_data=True)
    pie.set_categories(labels)
    for i, s in enumerate(target_sectors):
        pt = DataPoint(idx=i)
        pt.graphicalProperties.solidFill = COLORS.get(s, '999999')
        pie.series[0].data_points.append(pt)
    
    ws.add_chart(pie, f"J{sd_end + 2}")
    
    # 3. Status data & chart
    st_row = sd_end + 20
    ws.cell(st_row, 1, "Status").font = SUBHEADER_FONT
    ws.cell(st_row, 1).fill = SUBHEADER_FILL
    ws.cell(st_row, 2, "Count").font = SUBHEADER_FONT
    ws.cell(st_row, 2).fill = SUBHEADER_FILL
    
    status_counts = combined['status'].value_counts()
    status_colors = {'Completed': '28A745', 'Under Construction': 'FFC107', 'Pipeline': '17A2B8'}
    for i, (st, cnt) in enumerate(status_counts.items()):
        r = st_row + 1 + i
        ws.cell(r, 1, st)
        ws.cell(r, 2, int(cnt))
        ws.cell(r, 1).border = THIN_BORDER
        ws.cell(r, 2).border = THIN_BORDER
    
    st_end = st_row + len(status_counts)
    
    status_pie = PieChart()
    status_pie.title = "Pipeline Status"
    status_pie.style = 10
    status_pie.width = 12
    status_pie.height = 10
    
    labels = Reference(ws, min_col=1, min_row=st_row+1, max_row=st_end)
    data = Reference(ws, min_col=2, min_row=st_row, max_row=st_end)
    status_pie.add_data(data, titles_from_data=True)
    status_pie.set_categories(labels)
    for i, (st, _) in enumerate(status_counts.items()):
        pt = DataPoint(idx=i)
        pt.graphicalProperties.solidFill = status_colors.get(st, '999999')
        status_pie.series[0].data_points.append(pt)
    
    ws.add_chart(status_pie, f"A{st_end + 2}")
    
    # Annual projects line chart
    yearly_proj = ts.groupby('delivery_year').agg(
        projects=('project_name', 'count'),
        sf=('sqft', lambda x: x.sum()/1e6)
    )
    
    yp_row = st_row
    ws.cell(yp_row, 5, "Year").font = SUBHEADER_FONT
    ws.cell(yp_row, 5).fill = SUBHEADER_FILL
    ws.cell(yp_row, 6, "Projects").font = SUBHEADER_FONT
    ws.cell(yp_row, 6).fill = SUBHEADER_FILL
    ws.cell(yp_row, 7, "SF (M)").font = SUBHEADER_FONT
    ws.cell(yp_row, 7).fill = SUBHEADER_FILL
    
    for i, (yr, rd) in enumerate(yearly_proj.iterrows()):
        r = yp_row + 1 + i
        ws.cell(r, 5, int(yr))
        ws.cell(r, 6, int(rd['projects']))
        ws.cell(r, 7, round(rd['sf'], 2))
    
    yp_end = yp_row + len(yearly_proj)
    
    combo = BarChart()
    combo.type = "col"
    combo.title = "Annual Development Pace"
    combo.style = 10
    combo.width = 16
    combo.height = 12
    
    cats = Reference(ws, min_col=5, min_row=yp_row+1, max_row=yp_end)
    d1 = Reference(ws, min_col=6, min_row=yp_row, max_row=yp_end)
    combo.add_data(d1, titles_from_data=True)
    combo.set_categories(cats)
    combo.series[0].graphicalProperties.solidFill = '2E86AB'
    combo.y_axis.title = "Projects"
    
    # Add line for SF
    line = LineChart()
    d2 = Reference(ws, min_col=7, min_row=yp_row, max_row=yp_end)
    line.add_data(d2, titles_from_data=True)
    line.series[0].graphicalProperties.line.solidFill = 'F6511D'
    line.series[0].graphicalProperties.line.width = 28000
    line.y_axis.title = "SF (Millions)"
    line.y_axis.axId = 200
    
    combo.y_axis.crosses = "min"
    combo += line
    
    ws.add_chart(combo, f"J{st_end + 2}")
    
    # ── Sheet 2: Data ────────────────────────────────────────────────────
    ws_data = wb.create_sheet("Data")
    data_cols = ['project_name', 'city', 'neighborhood', 'sector', 'status', 
                 'sqft', 'units', 'est_delivery', 'delivery_year']
    data_display = combined[data_cols].copy()
    data_display.columns = ['Project Name', 'City', 'Neighborhood', 'Sector', 'Status',
                           'Sq Ft', 'Units', 'Est Delivery', 'Delivery Year']
    write_data_sheet(ws_data, data_display, "All Projects — DC & Atlanta")
    
    # Save
    path = '/home/ubuntu/CRE_Flood_Graph_Quick_Demo.xlsx'
    wb.save(path)
    print(f"✅ Saved: {path}")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Loading and preparing data...")
    combined, dc, atl = load_data()
    print(f"  DC: {len(dc)} rows, Atlanta: {len(atl)} rows, Combined: {len(combined)} rows")
    
    print("\nBuilding Comprehensive workbook...")
    build_comprehensive(combined, dc, atl)
    
    print("\nBuilding Quick Demo workbook...")
    build_quick_demo(combined, dc, atl)
    
    print("\n🎉 Done! Both Excel files created successfully.")

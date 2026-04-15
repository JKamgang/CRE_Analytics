import pandas as pd
import os
from src.features.growth_status.calculator import GrowthStatusCalculator

class ExcelGrowthGenerator:
    """
    Fixed: Generates PivotTables using XlsxWriter engine with professional formatting.
    """
    def __init__(self, output_path="Alile_Growth_Dynamics_Pro.xlsx"):
        self.output_path = output_path
        self.calc = GrowthStatusCalculator()

    def generate(self, df: pd.DataFrame):
        if df.empty:
            return None

        # Apply Enrichment
        df = self.calc.calculate_growth_metrics(df)

        with pd.ExcelWriter(self.output_path, engine='xlsxwriter') as writer:
            # 1. Raw Data Sheet
            df.to_excel(writer, sheet_name='Growth Data', index=False)

            workbook = writer.book
            worksheet = writer.sheets['Growth Data']
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # 2. Pivot Table Summary
            if 'growth_status' in df.columns:
                pivot = pd.pivot_table(df, values='project_name', index='city',
                                     columns='growth_status', aggfunc='count', fill_value=0)
                pivot.to_excel(writer, sheet_name='Summary Pivot')

                sheet = writer.sheets['Summary Pivot']
                chart = workbook.add_chart({'type': 'column'})
                chart.add_series({
                    'name':       ['Summary Pivot', 0, 1],
                    'categories': ['Summary Pivot', 1, 0, len(pivot), 0],
                    'values':     ['Summary Pivot', 1, 1, len(pivot), len(pivot.columns)],
                })
                sheet.insert_chart('G2', chart)

        return self.output_path

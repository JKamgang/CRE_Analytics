import pandas as pd
import os
from src.features.growth_status.calculator import GrowthStatusCalculator

class ExcelGrowthGenerator:
    """
    Generates a 'Pro' MS Excel file with formatted PivotTables and Growth Dynamics analysis.
    Uses XlsxWriter for professional formatting.
    """

    def __init__(self, output_path="Alile_Growth_Dynamics_Pro.xlsx"):
        self.output_path = output_path
        self.calc = GrowthStatusCalculator()

    def generate(self, df: pd.DataFrame):
        if df.empty:
            print("Warning: DataFrame is empty. Export cancelled.")
            return None

        # 1. Apply Growth Status logic
        df = self.calc.calculate_growth_metrics(df)

        # 2. Export to Excel
        with pd.ExcelWriter(self.output_path, engine='xlsxwriter') as writer:
            # Main Data Sheet
            df.to_excel(writer, sheet_name='Growth Data', index=False)

            workbook = writer.book
            worksheet = writer.sheets['Growth Data']

            # Formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # 3. Pivot Table Sheet (Summary)
            if 'growth_status' in df.columns and 'city' in df.columns:
                pivot = pd.pivot_table(df,
                                     values='project_name',
                                     index='city',
                                     columns='growth_status',
                                     aggfunc='count',
                                     fill_value=0)
                pivot.to_excel(writer, sheet_name='Summary Pivot')

                summary_sheet = writer.sheets['Summary Pivot']
                summary_sheet.set_column('A:Z', 15)

                # Add a chart to the summary sheet
                chart = workbook.add_chart({'type': 'column'})
                chart.add_series({
                    'name':       ['Summary Pivot', 0, 1],
                    'categories': ['Summary Pivot', 1, 0, len(pivot), 0],
                    'values':     ['Summary Pivot', 1, 1, len(pivot), len(pivot.columns)],
                })
                chart.set_title({'name': 'Growth Status by City'})
                summary_sheet.insert_chart('G2', chart)

        print(f"Generated Pro Excel File: {self.output_path}")
        return self.output_path

class PowerBIGenerator:
    """
    Generates Power Query M scripts and DAX measures for users to copy/paste into Power BI.
    """

    def get_dax_measures(self) -> str:
        return """
// DAX Measure: Cumulative Growth
Cumulative_Growth =
VAR StartYear = 2010
VAR EndYear = 2030
VAR BasePressure = AVERAGE(GrowthData[Growth_Pressure])
RETURN
    SUMX(
        FILTER(
            ALL('Date'[Year]),
            'Date'[Year] >= StartYear && 'Date'[Year] <= EndYear
        ),
        (1.05 + (BasePressure * 0.02)) * 'Date'[Year] + MOD('Date'[Year], 5) * 0.3
    )

// DAX Measure: Year-Over-Year (YoY) Regional Permit Growth
YoY_Regional_Permit_Growth =
VAR CurrentYearPermits = CALCULATE(COUNTROWS(GrowthData), 'GrowthData'[City] = SELECTEDVALUE('GrowthData'[City]))
VAR PreviousYearPermits = CALCULATE(COUNTROWS(GrowthData), SAMEPERIODLASTYEAR('Date'[Date]), 'GrowthData'[City] = SELECTEDVALUE('GrowthData'[City]))
RETURN
    DIVIDE(CurrentYearPermits - PreviousYearPermits, PreviousYearPermits, 0)

// DAX Measure: Z-Score Normalized Development Value
Z_Score_Normalized_Value =
VAR CityAvg = CALCULATE(AVERAGE(GrowthData[Est_Value]), ALLEXCEPT(GrowthData, GrowthData[City]))
VAR CityStdDev = CALCULATE(STDEV.P(GrowthData[Est_Value]), ALLEXCEPT(GrowthData, GrowthData[City]))
RETURN
    DIVIDE(MAX(GrowthData[Est_Value]) - CityAvg, CityStdDev, 0)
        """

    def get_power_query_script(self) -> str:
        return """
// Power Query (M) script to merge Atlanta and DC data
let
    // Connect to Web API
    AtlantaSource = Web.Contents("https://services1.arcgis.com/..."),
    DCSource = Web.Contents("https://maps2.dcgis.dc.gov/..."),

    // Parse JSON
    AtlantaJson = Json.Document(AtlantaSource),
    DCJson = Json.Document(DCSource),

    // Normalization & Z-Score Transform logic here...
    CombinedTable = Table.Combine({AtlantaJson, DCJson})
in
    CombinedTable
        """

    def generate_instruction_file(self, path="PowerBI_Instructions.txt"):
        with open(path, "w") as f:
            f.write("=== Power BI Scaffolding for Alile CRE Analytics ===\n\n")
            f.write("1. DAX Measures:\n")
            f.write(self.get_dax_measures())
            f.write("\n\n2. Power Query M Script:\n")
            f.write(self.get_power_query_script())
            f.write("\n\nHint: You can also use a local LLM to refine these scripts.\n")
        print(f"Generated Power BI instructions: {path}")
        return path

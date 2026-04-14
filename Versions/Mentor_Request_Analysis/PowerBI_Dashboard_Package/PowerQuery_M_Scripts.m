
// ============================================
// POWER QUERY M SCRIPTS
// Use in Power Query Editor → Advanced Editor
// ============================================

// === combined_pipeline ===
let
    Source = Csv.Document(File.Contents("combined_pipeline.csv"), [Delimiter=",", Columns=18, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {
        {"project_name", type text},
        {"city", type text},
        {"ward", Int64.Type},
        {"neighborhood", type text},
        {"developer", type text},
        {"architect", type text},
        {"sector", type text},
        {"status", type text},
        {"sqft", type number},
        {"units", type number},
        {"est_value_millions", type number},
        {"est_delivery", type text},
        {"report_year", Int64.Type},
        {"latitude", type number},
        {"longitude", type number},
        {"delivery_year", Int64.Type},
        {"delivery_quarter", Int64.Type},
        {"delivery_date", type date}
    }),
    ReplacedNulls = Table.ReplaceValue(ChangedTypes, null, 0, Replacer.ReplaceValue, {"units", "est_value_millions"})
in
    ReplacedNulls

// === sector_lookup ===
let
    Source = Csv.Document(File.Contents("sector_lookup.csv"), [Delimiter=",", Columns=3, Encoding=65001]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {
        {"sector", type text},
        {"color_hex", type text},
        {"sort_order", Int64.Type}
    })
in
    ChangedTypes

// === city_lookup ===
let
    Source = Csv.Document(File.Contents("city_lookup.csv"), [Delimiter=",", Columns=4, Encoding=65001]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {
        {"city", type text},
        {"city_full", type text},
        {"state", type text},
        {"region", type text}
    })
in
    ChangedTypes

// === time_dimension ===
let
    Source = Csv.Document(File.Contents("time_dimension.csv"), [Delimiter=",", Columns=5, Encoding=65001]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {
        {"year", Int64.Type},
        {"quarter", Int64.Type},
        {"year_quarter", type text},
        {"date_key", type date},
        {"is_forecast", type logical}
    })
in
    ChangedTypes

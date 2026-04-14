import json
import zipfile
import os

# ============================================================
# BUILD COMPLETE POWER BI .PBIX FILE
# ============================================================

def make_visual_config(name, visual_type, single_visual_type=None):
    """Create a visual config JSON string."""
    cfg = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": 1280, "height": 720}}],
        "singleVisual": {
            "visualType": visual_type,
            "projections": {},
            "prototypeQuery": {},
            "drillFilterOtherVisuals": True
        }
    }
    if single_visual_type:
        cfg["singleVisual"]["visualType"] = single_visual_type
    return json.dumps(cfg)

def make_card_vc(name, x, y, w, h, measure_name, title_text):
    """Create a KPI card visual container."""
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": f"combined_pipeline.{measure_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                "Select": [
                    {
                        "Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": measure_name},
                        "Name": f"combined_pipeline.{measure_name}"
                    }
                ]
            },
            "objects": {
                "labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "28D"}}}, "color": {"solid": {"color": "#003366"}}}}],
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "fontSize": {"expr": {"Literal": {"Value": "10D"}}}}}]
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},"fontSize": {"expr": {"Literal": {"Value": "11D"}}}, "fontColor": {"solid": {"color": "#003366"}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#FFFFFF"}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#E0E0E0"}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps({
            "Commands": [{
                "SemanticQueryDataShapeCommand": {
                    "Query": {
                        "Version": 2,
                        "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                        "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": measure_name}, "Name": f"combined_pipeline.{measure_name}"}]
                    },
                    "Binding": {"Primary": {"Groupings": [{"Projections": [0]}]}, "Version": 1}
                }
            }]
        }),
        "dataTransforms": json.dumps({
            "objects": {},
            "projectionOrdering": {"Values": [0]},
            "projectionActiveItems": {"Values": [{"queryRef": f"combined_pipeline.{measure_name}", "active": True}]}
        })
    }

def make_slicer_vc(name, x, y, w, h, column_name, title_text):
    """Create a slicer visual container."""
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": f"combined_pipeline.{column_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                "Select": [
                    {
                        "Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": column_name},
                        "Name": f"combined_pipeline.{column_name}"
                    }
                ]
            },
            "objects": {
                "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Basic'"}}}}}],
                "selection": [{"properties": {"selectAllCheckboxEnabled": {"expr": {"Literal": {"Value": "true"}}}, "singleSelect": {"expr": {"Literal": {"Value": "false"}}}}}],
                "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "fontColor": {"solid": {"color": "#003366"}}, "textSize": {"expr": {"Literal": {"Value": "10D"}}}}}],
                "items": [{"properties": {"fontColor": {"solid": {"color": "#333333"}}, "textSize": {"expr": {"Literal": {"Value": "9D"}}}}}]
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#FFFFFF"}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#E0E0E0"}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps({
            "Commands": [{
                "SemanticQueryDataShapeCommand": {
                    "Query": {
                        "Version": 2,
                        "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                        "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": column_name}, "Name": f"combined_pipeline.{column_name}"}]
                    },
                    "Binding": {"Primary": {"Groupings": [{"Projections": [0]}]}, "Version": 1}
                }
            }]
        }),
        "dataTransforms": json.dumps({
            "projectionOrdering": {"Values": [0]},
            "projectionActiveItems": {"Values": [{"queryRef": f"combined_pipeline.{column_name}", "active": True}]}
        })
    }

def make_map_vc(name, x, y, w, h, title_text, filters_json="[]"):
    """Create a map visual container."""
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "map",
            "projections": {
                "Size": [{"queryRef": "combined_pipeline.Bubble Size"}],
                "Category": [{"queryRef": "combined_pipeline.latitude"}],
                "Series": [{"queryRef": "combined_pipeline.sector"}],
                "X": [{"queryRef": "combined_pipeline.longitude"}],
                "Y": [{"queryRef": "combined_pipeline.latitude"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "latitude"}, "Name": "combined_pipeline.latitude"},
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "longitude"}, "Name": "combined_pipeline.longitude"},
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "sector"}, "Name": "combined_pipeline.sector"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "Bubble Size"}, "Name": "combined_pipeline.Bubble Size"}
                ]
            },
            "objects": {
                "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "position": {"expr": {"Literal": {"Value": "'Bottom'"}}}}}],
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "bubbles": [{"properties": {"bubbleSize": {"expr": {"Literal": {"Value": "50D"}}}}}]
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},"fontColor": {"solid": {"color": "#003366"}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#FFFFFF"}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#E0E0E0"}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": filters_json,
        "query": json.dumps({
            "Commands": [{
                "SemanticQueryDataShapeCommand": {
                    "Query": {
                        "Version": 2,
                        "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                        "Select": [
                            {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "latitude"}, "Name": "combined_pipeline.latitude"},
                            {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "longitude"}, "Name": "combined_pipeline.longitude"},
                            {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "sector"}, "Name": "combined_pipeline.sector"},
                            {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "Bubble Size"}, "Name": "combined_pipeline.Bubble Size"}
                        ]
                    },
                    "Binding": {
                        "Primary": {"Groupings": [{"Projections": [0, 1, 2]}]},
                        "DataReduction": {"DataVolume": 4, "Primary": {"Sample": {"Count": 1000}}},
                        "Version": 1
                    }
                }
            }]
        }),
        "dataTransforms": json.dumps({
            "projectionOrdering": {"Size": [3], "Category": [0], "Series": [2], "X": [1], "Y": [0]}
        })
    }

def make_area_chart_vc(name, x, y, w, h, title_text, x_col, y_measure, legend_col=None, chart_type="areaChart"):
    """Create an area/line chart visual container."""
    selects = [
        {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": x_col}, "Name": f"combined_pipeline.{x_col}"},
        {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": y_measure}, "Name": f"combined_pipeline.{y_measure}"}
    ]
    projections = {
        "Category": [{"queryRef": f"combined_pipeline.{x_col}"}],
        "Y": [{"queryRef": f"combined_pipeline.{y_measure}"}]
    }
    if legend_col:
        selects.append({"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": legend_col}, "Name": f"combined_pipeline.{legend_col}"})
        projections["Series"] = [{"queryRef": f"combined_pipeline.{legend_col}"}]

    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": chart_type,
            "projections": projections,
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                "Select": selects
            },
            "objects": {
                "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "true" if legend_col else "false"}}}, "position": {"expr": {"Literal": {"Value": "'Bottom'"}}}}}],
                "categoryAxis": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "labelDisplayUnits": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "valueAxis": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "labelDisplayUnits": {"expr": {"Literal": {"Value": "1000000D"}}}, "gridlinesShow": {"expr": {"Literal": {"Value": "true"}}}}}]
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},"fontColor": {"solid": {"color": "#003366"}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#FFFFFF"}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#E0E0E0"}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    
    binding_groupings = [{"Projections": [0]}]
    if legend_col:
        binding_groupings.append({"Projections": [2]})
    
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps({
            "Commands": [{
                "SemanticQueryDataShapeCommand": {
                    "Query": {
                        "Version": 2,
                        "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                        "Select": selects
                    },
                    "Binding": {
                        "Primary": {"Groupings": [{"Projections": [0]}]},
                        "Secondary": {"Groupings": [{"Projections": [2]}]} if legend_col else None,
                        "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": 500}}},
                        "Version": 1
                    }
                }
            }]
        }),
        "dataTransforms": json.dumps({
            "projectionOrdering": {"Category": [0], "Y": [1], "Series": [2]} if legend_col else {"Category": [0], "Y": [1]}
        })
    }

def make_donut_vc(name, x, y, w, h, title_text, category_col, measure_name):
    """Create a donut chart visual container."""
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "donutChart",
            "projections": {
                "Category": [{"queryRef": f"combined_pipeline.{category_col}"}],
                "Y": [{"queryRef": f"combined_pipeline.{measure_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": category_col}, "Name": f"combined_pipeline.{category_col}"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": measure_name}, "Name": f"combined_pipeline.{measure_name}"}
                ]
            },
            "objects": {
                "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "position": {"expr": {"Literal": {"Value": "'Right'"}}}}}],
                "labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "labelStyle": {"expr": {"Literal": {"Value": "'Both'"}}}}}]
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},"fontColor": {"solid": {"color": "#003366"}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#FFFFFF"}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#E0E0E0"}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps({
            "Commands": [{
                "SemanticQueryDataShapeCommand": {
                    "Query": {
                        "Version": 2,
                        "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                        "Select": [
                            {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": category_col}, "Name": f"combined_pipeline.{category_col}"},
                            {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": measure_name}, "Name": f"combined_pipeline.{measure_name}"}
                        ]
                    },
                    "Binding": {
                        "Primary": {"Groupings": [{"Projections": [0]}]},
                        "DataReduction": {"DataVolume": 4, "Primary": {"Top": {"Count": 20}}},
                        "Version": 1
                    }
                }
            }]
        }),
        "dataTransforms": json.dumps({
            "projectionOrdering": {"Category": [0], "Y": [1]}
        })
    }

def make_bar_chart_vc(name, x, y, w, h, title_text, category_col, measure_name, chart_type="barChart"):
    """Create a bar chart visual container."""
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": chart_type,
            "projections": {
                "Category": [{"queryRef": f"combined_pipeline.{category_col}"}],
                "Y": [{"queryRef": f"combined_pipeline.{measure_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": category_col}, "Name": f"combined_pipeline.{category_col}"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": measure_name}, "Name": f"combined_pipeline.{measure_name}"}
                ]
            },
            "objects": {
                "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "categoryAxis": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}],
                "valueAxis": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},"fontColor": {"solid": {"color": "#003366"}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#FFFFFF"}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#E0E0E0"}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
        "query": json.dumps({
            "Commands": [{
                "SemanticQueryDataShapeCommand": {
                    "Query": {
                        "Version": 2,
                        "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                        "Select": [
                            {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": category_col}, "Name": f"combined_pipeline.{category_col}"},
                            {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": measure_name}, "Name": f"combined_pipeline.{measure_name}"}
                        ]
                    },
                    "Binding": {
                        "Primary": {"Groupings": [{"Projections": [0]}]},
                        "DataReduction": {"DataVolume": 4, "Primary": {"Top": {"Count": 30}}},
                        "Version": 1
                    }
                }
            }]
        }),
        "dataTransforms": json.dumps({
            "projectionOrdering": {"Category": [0], "Y": [1]}
        })
    }

def make_table_vc(name, x, y, w, h, title_text, columns, filters_json="[]"):
    """Create a table visual container."""
    selects = []
    projections = {"Values": []}
    for i, col in enumerate(columns):
        if col.get("type") == "measure":
            selects.append({"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": col["name"]}, "Name": f"combined_pipeline.{col['name']}"})
        else:
            selects.append({"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": col["name"]}, "Name": f"combined_pipeline.{col['name']}"})
        projections["Values"].append({"queryRef": f"combined_pipeline.{col['name']}"})
    
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": projections,
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                "Select": selects
            },
            "objects": {
                "grid": [{"properties": {"gridVertical": {"expr": {"Literal": {"Value": "true"}}}, "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}}, "rowPadding": {"expr": {"Literal": {"Value": "3D"}}}}}],
                "columnHeaders": [{"properties": {"fontColor": {"solid": {"color": "#FFFFFF"}}, "backColor": {"solid": {"color": "#003366"}}, "fontSize": {"expr": {"Literal": {"Value": "10D"}}}}}],
                "values": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "9D"}}}}}]
            },
            "vcObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},"fontColor": {"solid": {"color": "#003366"}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#FFFFFF"}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": "#E0E0E0"}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    return {
        "x": x, "y": y, "z": 0, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": filters_json,
        "query": json.dumps({
            "Commands": [{
                "SemanticQueryDataShapeCommand": {
                    "Query": {
                        "Version": 2,
                        "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
                        "Select": selects
                    },
                    "Binding": {
                        "Primary": {"Groupings": [{"Projections": list(range(len(columns)))}]},
                        "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": 500}}},
                        "Version": 1
                    }
                }
            }]
        }),
        "dataTransforms": json.dumps({
            "projectionOrdering": {"Values": list(range(len(columns)))}
        })
    }

def make_textbox_vc(name, x, y, w, h, text, font_size=20, color="#003366", bold=True):
    """Create a text box visual container for titles."""
    config = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": text,
                                "textStyle": {
                                    "fontFamily": "Segoe UI Semibold",
                                    "fontSize": f"{font_size}px",
                                    "fontWeight": "bold" if bold else "normal",
                                    "color": color
                                }
                            }]
                        }]
                    }
                }]
            },
            "vcObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 10, "width": w, "height": h,
        "config": json.dumps(config),
        "filters": "[]",
        "query": "",
        "dataTransforms": ""
    }

# Multifamily filter JSON
mf_filter = json.dumps([{
    "name": "MF_Filter",
    "expression": {
        "Column": {"Expression": {"SourceRef": {"Entity": "combined_pipeline"}}, "Property": "sector"}
    },
    "filter": {
        "Version": 2,
        "From": [{"Name": "c", "Entity": "combined_pipeline", "Type": 0}],
        "Where": [{
            "Condition": {
                "In": {
                    "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "sector"}}],
                    "Values": [[{"Literal": {"Value": "'Multifamily'"}}]]
                }
            }
        }]
    },
    "type": "Categorical",
    "howCreated": 0
}])

# ============================================================
# PAGE 1: EXECUTIVE OVERVIEW
# ============================================================
page1_visuals = []

# Title
page1_visuals.append(make_textbox_vc("p1_title", 10, 5, 900, 40, "CRE Flood Graph — Executive Overview", 22, "#003366"))
page1_visuals.append(make_textbox_vc("p1_subtitle", 10, 40, 900, 25, "DC & Atlanta Commercial Real Estate Pipeline Analysis", 12, "#666666", False))

# KPI Cards (top row)
card_y = 70
card_h = 85
card_w = 200
page1_visuals.append(make_card_vc("p1_card1", 220, card_y, card_w, card_h, "Total Projects", "Total Projects"))
page1_visuals.append(make_card_vc("p1_card2", 430, card_y, card_w, card_h, "Total SF", "Total SF (M)"))
page1_visuals.append(make_card_vc("p1_card3", 640, card_y, card_w, card_h, "Active Cities", "Active Cities"))
page1_visuals.append(make_card_vc("p1_card4", 850, card_y, card_w, card_h, "Growth Rate YoY", "Growth Rate YoY"))
page1_visuals.append(make_card_vc("p1_card5", 1060, card_y, card_w, card_h, "Total Est. Value ($M)", "Total Est Value"))

# Slicers (left sidebar)
slicer_x = 10
slicer_w = 195
page1_visuals.append(make_slicer_vc("p1_slicer_city", slicer_x, card_y, slicer_w, 80, "city", "City"))
page1_visuals.append(make_slicer_vc("p1_slicer_sector", slicer_x, card_y + 85, slicer_w, 120, "sector", "Sector"))
page1_visuals.append(make_slicer_vc("p1_slicer_status", slicer_x, card_y + 210, slicer_w, 120, "status", "Project Status"))
page1_visuals.append(make_slicer_vc("p1_slicer_year", slicer_x, card_y + 335, slicer_w, 80, "delivery_year", "Delivery Year"))

# Map Visual (center-left)
page1_visuals.append(make_map_vc("p1_map", 220, 165, 520, 310, "Project Locations — Size by SF, Color by Sector"))

# Stacked Area Chart - Flood Rising (center-right)
page1_visuals.append(make_area_chart_vc("p1_flood_chart", 750, 165, 520, 310, 
    "Cumulative SF Over Time — The Flood Rising", "delivery_year", "Cumulative SF by Sector", "sector", "areaChart"))

# Donut Chart (bottom-left)
page1_visuals.append(make_donut_vc("p1_donut", 220, 485, 400, 225, "Sector Distribution by Total SF", "sector", "Total SF"))

# Bar Chart - Projects by Status (bottom-right)
page1_visuals.append(make_bar_chart_vc("p1_bar_status", 630, 485, 310, 225, "Projects by Status", "status", "Total Projects", "barChart"))

# Bar Chart - Top Developers (far bottom-right)
page1_visuals.append(make_bar_chart_vc("p1_bar_dev", 950, 485, 320, 225, "Top Developers by SF", "developer", "Total SF", "barChart"))


# ============================================================
# PAGE 2: MULTIFAMILY DEEP-DIVE
# ============================================================
page2_visuals = []

# Title
page2_visuals.append(make_textbox_vc("p2_title", 10, 5, 900, 40, "Multifamily Deep-Dive", 22, "#003366"))
page2_visuals.append(make_textbox_vc("p2_subtitle", 10, 40, 900, 25, "Residential Pipeline Analysis — Units, Density & Delivery Trends", 12, "#666666", False))

# KPI Cards
card_y2 = 70
page2_visuals.append(make_card_vc("p2_card1", 10, card_y2, 250, 85, "MF Total Projects", "MF Total Projects"))
page2_visuals.append(make_card_vc("p2_card2", 270, card_y2, 250, 85, "MF Total Units", "MF Total Units"))
page2_visuals.append(make_card_vc("p2_card3", 530, card_y2, 250, 85, "MF Avg Unit Density", "MF Avg Unit Density"))
page2_visuals.append(make_card_vc("p2_card4", 790, card_y2, 250, 85, "MF Completion Rate", "MF Completion Rate"))
page2_visuals.append(make_card_vc("p2_card5", 1050, card_y2, 220, 85, "MF Pipeline Units", "MF Pipeline Units"))

# Map - Multifamily only
page2_visuals.append(make_map_vc("p2_map", 10, 165, 620, 280, "Multifamily Project Locations", mf_filter))

# Line Chart - MF deliveries over time
page2_visuals.append(make_area_chart_vc("p2_line_deliveries", 640, 165, 630, 280,
    "Multifamily Deliveries Over Time", "delivery_year", "MF Total Units", None, "lineChart"))

# Table - Top MF projects
page2_visuals.append(make_table_vc("p2_table", 10, 455, 750, 255,
    "Top Multifamily Projects by Unit Count",
    [
        {"name": "project_name", "type": "column"},
        {"name": "city", "type": "column"},
        {"name": "neighborhood", "type": "column"},
        {"name": "units", "type": "column"},
        {"name": "sqft", "type": "column"},
        {"name": "status", "type": "column"},
        {"name": "delivery_year", "type": "column"}
    ],
    mf_filter
))

# Bar Chart - MF by status
page2_visuals.append(make_bar_chart_vc("p2_bar_status", 770, 455, 500, 255, 
    "Multifamily Projects by Status", "status", "MF Total Projects", "barChart"))


# ============================================================
# PAGE 3: TIME SERIES ANALYSIS
# ============================================================
page3_visuals = []

# Title
page3_visuals.append(make_textbox_vc("p3_title", 10, 5, 900, 40, "Time Series Analysis", 22, "#003366"))
page3_visuals.append(make_textbox_vc("p3_subtitle", 10, 40, 900, 25, "Annual Trends, Growth Rates & Sector Comparisons", 12, "#666666", False))

# KPI Cards
page3_visuals.append(make_card_vc("p3_card1", 10, 70, 300, 85, "Growth Rate YoY", "Growth Rate YoY"))
page3_visuals.append(make_card_vc("p3_card2", 320, 70, 300, 85, "Total Projects", "Total Projects"))
page3_visuals.append(make_card_vc("p3_card3", 630, 70, 300, 85, "Total SF (M)", "Total SF (M)"))
page3_visuals.append(make_card_vc("p3_card4", 940, 70, 330, 85, "Avg Project Size", "Avg Project Size"))

# Line Chart - Annual project count
page3_visuals.append(make_area_chart_vc("p3_line_projects", 10, 165, 620, 260,
    "Annual Project Count Over Time", "delivery_year", "Total Projects", None, "lineChart"))

# Line Chart - Annual SF delivered
page3_visuals.append(make_area_chart_vc("p3_line_sf", 640, 165, 630, 260,
    "Annual Square Footage Delivered", "delivery_year", "Total SF", None, "lineChart"))

# Stacked Bar - Sectors over time
page3_visuals.append(make_area_chart_vc("p3_stacked_bar", 10, 435, 620, 275,
    "Sector Comparison Over Time", "delivery_year", "Total SF", "sector", "clusteredBarChart"))

# Area Chart - Cumulative growth
page3_visuals.append(make_area_chart_vc("p3_cumulative", 640, 435, 630, 275,
    "Cumulative Growth Trends", "delivery_year", "Cumulative SF", "sector", "areaChart"))


# ============================================================
# BUILD THE COMPLETE REPORT LAYOUT
# ============================================================

# Load the theme
with open("/home/ubuntu/PowerBI_Dashboard_Package/CRE_Flood_Theme.json", "r") as f:
    theme = json.load(f)

report_layout = {
    "id": 0,
    "resourcePackages": [{
        "resourcePackage": {
            "name": "SharedResources",
            "type": 2,
            "items": [{
                "type": 202,
                "path": "BaseThemes/CRE_Flood_Theme.json",
                "name": "CRE_Flood_Theme"
            }],
            "disabled": False
        }
    }],
    "sections": [
        {
            "id": 0,
            "name": "Executive_Overview",
            "displayName": "Executive Overview",
            "filters": "[]",
            "ordinal": 0,
            "visualContainers": page1_visuals,
            "config": json.dumps({
                "name": "Executive_Overview",
                "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": 1280, "height": 720}}],
                "objects": {
                    "background": [{"properties": {"color": {"solid": {"color": "#F5F5F5"}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]
                }
            }),
            "displayOption": 1,
            "width": 1280,
            "height": 720
        },
        {
            "id": 1,
            "name": "Multifamily_DeepDive",
            "displayName": "Multifamily Deep-Dive",
            "filters": "[]",
            "ordinal": 1,
            "visualContainers": page2_visuals,
            "config": json.dumps({
                "name": "Multifamily_DeepDive",
                "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": 1280, "height": 720}}],
                "objects": {
                    "background": [{"properties": {"color": {"solid": {"color": "#F5F5F5"}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]
                }
            }),
            "displayOption": 1,
            "width": 1280,
            "height": 720
        },
        {
            "id": 2,
            "name": "Time_Series_Analysis",
            "displayName": "Time Series Analysis",
            "filters": "[]",
            "ordinal": 2,
            "visualContainers": page3_visuals,
            "config": json.dumps({
                "name": "Time_Series_Analysis",
                "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "width": 1280, "height": 720}}],
                "objects": {
                    "background": [{"properties": {"color": {"solid": {"color": "#F5F5F5"}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]
                }
            }),
            "displayOption": 1,
            "width": 1280,
            "height": 720
        }
    ],
    "config": json.dumps({
        "version": "5.50",
        "themeCollection": {
            "baseTheme": {
                "name": "CRE Flood Graph Theme",
                "reportVersionAtImport": "5.50",
                "type": 2
            }
        },
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True,
        "linguisticSchemaSyncVersion": 2,
        "settings": {
            "useStylableVisualContainerHeader": True,
            "exportDataMode": 1,
            "useDefaultAggregateDisplayName": True
        }
    }),
    "layoutOptimization": 0
}

# ============================================================
# BUILD THE DATA MODEL SCHEMA (BIM)
# ============================================================
with open("/home/ubuntu/PowerBI_Dashboard_Package/CRE_Flood_Model.bim", "r") as f:
    bim_model = json.load(f)

# ============================================================
# BUILD SETTINGS
# ============================================================
settings = {
    "Version": 4,
    "QueriesSettings": {
        "Version": 2,
        "TypeDetectionEnabled": True,
        "RelationshipImportEnabled": True
    }
}

# ============================================================
# BUILD DIAGRAM LAYOUT
# ============================================================
diagram_layout = {
    "version": "1.0",
    "diagrams": [{
        "ordinal": 0,
        "nodes": [
            {"name": "combined_pipeline", "nodeIndex": 0, "x": 100, "y": 100, "isExpanded": True},
            {"name": "sector_lookup", "nodeIndex": 1, "x": 500, "y": 100, "isExpanded": True},
            {"name": "city_lookup", "nodeIndex": 2, "x": 500, "y": 300, "isExpanded": True},
            {"name": "time_dimension", "nodeIndex": 3, "x": 100, "y": 400, "isExpanded": True}
        ],
        "scrollPosition": {"x": 0, "y": 0}
    }]
}

# ============================================================
# WRITE THE .PBIX FILE
# ============================================================
output_path = "/home/ubuntu/CRE_Flood_Graph_Dashboard.pbix"

with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    # Version
    zf.writestr("Version", "2.0")
    
    # Content Types
    content_types = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' \
        '<Default Extension="json" ContentType="application/json"/>' \
        '<Default Extension="xml" ContentType="application/xml"/>' \
        '</Types>'
    zf.writestr("[Content_Types].xml", content_types)
    
    # Report Layout (the main visual definition)
    layout_json = json.dumps(report_layout, indent=None, ensure_ascii=False)
    zf.writestr("Report/Layout", layout_json)
    
    # Data Model Schema
    zf.writestr("DataModelSchema", json.dumps(bim_model, indent=2))
    
    # Metadata
    metadata = {
        "version": "1.0",
        "createdFrom": "CRE_Flood_Graph_Dashboard_Package",
        "createdDate": "2026-03-30T00:00:00Z"
    }
    zf.writestr("Metadata", json.dumps(metadata))
    
    # Settings
    zf.writestr("Settings", json.dumps(settings))
    
    # Diagram Layout
    zf.writestr("DiagramLayout", json.dumps(diagram_layout))
    
    # Embed the theme
    zf.writestr("Report/StaticResources/SharedResources/BaseThemes/CRE_Flood_Theme.json", 
                json.dumps(theme, indent=2))
    
    # Connections - point to CSV data source
    connections = {
        "Version": 1,
        "Connections": [{
            "Name": "combined_pipeline",
            "ConnectionString": "Provider=Microsoft.Mashup.OleDb.1;Data Source=$Embedded$;Location=combined_pipeline",
            "PbiServiceModelId": None
        }]
    }
    zf.writestr("Connections", json.dumps(connections))

print(f"✅ PBIX file created: {output_path}")
print(f"   File size: {os.path.getsize(output_path):,} bytes")

# Verify contents
with zipfile.ZipFile(output_path, 'r') as zf:
    print("\n📦 Contents:")
    for f in zf.namelist():
        info = zf.getinfo(f)
        print(f"   {f} ({info.file_size:,} bytes)")


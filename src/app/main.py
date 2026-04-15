"""
Alile CRE Analytics — Main Entry Point
======================================
Run with: streamlit run src/app/main.py
"""

import sys
import os
import streamlit as st

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the dashboard widget as the main application
from src.widgets.dashboard.app import main as run_dashboard

if __name__ == "__main__":
    # If run via 'python src/app/main.py', it can still run the CLI pipeline
    # but if run via 'streamlit run', it will execute the dashboard.
    # We can detect if we are in streamlit.
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx():
            run_dashboard()
        else:
            # CLI Fallback
            from src.widgets.pipeline_runner import DataArteryPipeline
            import json
            pipeline = DataArteryPipeline()
            result = pipeline.run_pipeline()
            print("\n--- Pipeline Execution Complete (CLI) ---")
            print(json.dumps(result, indent=2))
    except ImportError:
        # CLI Fallback
        from src.widgets.pipeline_runner import DataArteryPipeline
        import json
        pipeline = DataArteryPipeline()
        result = pipeline.run_pipeline()
        print("\n--- Pipeline Execution Complete (CLI) ---")
        print(json.dumps(result, indent=2))

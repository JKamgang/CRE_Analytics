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
    run_dashboard()

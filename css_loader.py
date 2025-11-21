# css_loader.py
import streamlit as st
import os

def load_css(css_file="styles.css"):
    """Load CSS from external file"""
    try:
        with open(css_file, "r") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file '{css_file}' not found. Using default styles.")
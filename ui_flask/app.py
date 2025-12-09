import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="PropBot - Real Estate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Read files
def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

# Load HTML, CSS, and JS
html_content = read_file('templates/index.html')
css_content = read_file('static/css/styles.css')
js_content = read_file('static/js/main.js')

# Inject CSS and JS into HTML
full_html = html_content.replace('<!-- CSS_PLACEHOLDER -->', f'<style>{css_content}</style>')
full_html = full_html.replace('<!-- JS_PLACEHOLDER -->', f'<script>{js_content}</script>')

# Render
# Render with full width and height
# Render
components.html(full_html, height=900, scrolling=False, width=None )

st.markdown("""
<style>
    .main > div { padding: 0 !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

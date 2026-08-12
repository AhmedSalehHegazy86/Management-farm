import datetime
import io
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. إعدادات الصفحة (تم تغيير initial_sidebar_state إلى collapsed)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Broiler Farm Manager - Secure Auth",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="collapsed", # تم تعديل هذا الخيار ليظهر كأيقونة
)

st.markdown(
    """
    <style>
    /* نقل الشريط الجانبي إلى اليمين */
    [data-testid="stSidebar"] {
        direction: rtl !important;
        right: 0 !important;
        left: auto !important;
        background-color: #0f172a !important;
        border-left: 2px solid #38bdf8 !important;
    }
    
    /* تأكد من أن القائمة الجانبية (Hamburger Menu) تظهر في المكان الصحيح */
    [data-testid="stSidebar"][aria-expanded="false"] {
        right: -300px !important; /* إخفاء عند الإغلاق */
    }

    /* خلفية التطبيق العامة بلون أزرق متدرج وداكن أنيق */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        direction: rtl !important;
        text-align: right !important;
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%) !important; 
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] * {
        direction: rtl !important;
        text-align: right !important;
        color: #f8fafc !important;
    }

    /* باقي التنسيقات كما هي... */
    .stMarkdown, .stText, p, span, label, div {
        direction: rtl !important;
        text-align: right !important;
        color: #f8fafc !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    h1, h2, h3 {
        color: #e0f2fe !important;
        font-weight: 800 !important;
        text-align: right !important;
    }

    .stMetric, div[data-testid="stForm"] { 
        background: #ffffff !important; 
        padding: 20px !important; 
        border-radius: 12px !important; 
        border: 2px solid #38bdf8 !important;
        border-right: 8px solid #0284c7 !important; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
        text-align: right !important;
    }
    
    .stMetric *, div[data-testid="stForm"] * {
        color: #000000 !important;
        text-align: right !important;
    }

    [data-testid="stMetricValue"] {
        color: #0369a1 !important;
        font-weight: 900 !important;
        font-size: 2rem !important;
        text-align: right !important;
    }
    [data-testid="stMetricLabel"] {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        text-align: right !important;
    }

    input, select, textarea, [data-baseweb="select"] {
        direction: rtl !important;
        text-align: right !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #0284c7 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        direction: rtl !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border: 1px solid #38bdf8;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #e0f2fe;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: white !important;
    }

    .stButton>button {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 8px;
        border: 2px solid #38bdf8;
        font-weight: 900 !important;
        padding: 0.6rem 1.2rem;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0369a1 !important;
    }

    [data-testid="stDataFrame"] {
        background-color: #ffffff;
        border-radius: 10px;
        border: 2px solid #38bdf8;
        direction: rtl !important;
        text-align: right !important;
    }

    @media print {
        header, [data-testid="stSidebar"], .stTabs [role="tablist"], button { 
            display: none !important; 
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ... (باقي الكود يظل كما هو دون تغيير)

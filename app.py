import datetime
import io
import sqlite3
import hashlib

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# 1. إعداد الصفحة (الشريط الجانبي مغلق افتراضياً لضمان العمل السليم)
# =========================================================

st.set_page_config(
    page_title="Broiler Farm Manager V11 - Dynamic Sidebar",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="collapsed", # تم التعديل هنا ليفتح مغلقاً
)


# =========================================================
# 2. التصميم الاحترافي (تم تحديث كود الشريط الجانبي)
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GENERAL APP (RTL)
       ===================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        direction: rtl !important;
        text-align: right !important;
    }

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background:
            radial-gradient(
                circle at top right,
                #1d4ed8 0%,
                #0f172a 45%,
                #020617 100%
            ) !important;

        color: #ffffff !important;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding-top: 2rem !important;
        padding-right: 2rem !important;
        padding-left: 2rem !important;
    }


    /* =====================================================
       SIDEBAR — DYNAMIC OVERLAY PANEL (تم التعديل)
       ===================================================== */

    [data-testid="stSidebar"] {
        direction: rtl !important;
        position: fixed !important;
        top: 0 !important;
        right: 0 !important;
        left: auto !important;
        bottom: 0 !important;
        background:
            linear-gradient(
                180deg,
                #020617 0%,
                #0f172a 45%,
                #172554 100%
            ) !important;
        border-left: 2px solid #38bdf8 !important;
        box-shadow: -10px 0 35px rgba(0, 0, 0, 0.55) !important;
        z-index: 999999 !important;
        overflow-y: auto !important;
        transition: width 0.3s ease !important; /* حركة انسيابية */
    }

    /* عندما يكون الشريط مغلقاً */
    [data-testid="stSidebar"][data-collapsed="true"] {
        width: 0px !important;
        min-width: 0px !important;
        overflow: hidden !important;
    }

    /* عندما يكون الشريط مفتوحاً */
    [data-testid="stSidebar"]:not([data-collapsed="true"]) {
        width: 350px !important;
        min-width: 350px !important;
    }


    /* =====================================================
       SIDEBAR CONTENT & BUTTONS
       ===================================================== */

    [data-testid="stSidebarContent"] {
        direction: rtl !important;
        padding: 1.5rem 1rem 2rem 1rem !important;
        width: 350px !important; /* ثابت للمحتوى */
    }

    [data-testid="stSidebar"] * {
        direction: rtl !important;
        text-align: right !important;
        color: #f8fafc !important;
    }

    /* زر إظهار/إخفاء الشريط الجانبي */
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important;
        top: 12px !important;
        right: 12px !important;
        width: 48px !important;
        height: 48px !important;
        z-index: 1000000 !important;
        background: linear-gradient(135deg, #0284c7, #0369a1) !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 14px !important;
        box-shadow: 0 6px 22px rgba(0, 0, 0, 0.40) !important;
    }

    [data-testid="stSidebarCollapsedControl"] button {
        width: 48px !important;
        height: 48px !important;
        background: transparent !important;
        border: none !important;
        color: white !important;
    }


    /* =====================================================
       TITLES & METRICS & INPUTS (نفس إعداداتك)
       ===================================================== */

    h1, h2, h3 { color: #e0f2fe !important; font-weight: 900 !important; }
    
    [data-testid="stMetric"] {
        background: #ffffff !important;
        padding: 18px !important;
        border-radius: 14px !important;
        border: 2px solid #38bdf8 !important;
        border-right: 8px solid #0284c7 !important;
    }
    
    [data-testid="stMetricValue"] { color: #0369a1 !important; font-size: 2rem !important; font-weight: 900 !important; }

    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #0284c7, #0369a1) !important;
        color: #ffffff !important;
        border-radius: 9px !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. المعايير القياسية
# =========================================================

STANDARD_BENCHMARKS = pd.DataFrame(
    [{"day": i, "std_weight": 45 + (i-1)*55, "std_fcr": 0.90 + (i*0.02)} for i in range(1, 41)]
)


# =========================================================
# 4. DATABASE
# =========================================================

DB_NAME = "farm_manager_v11.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)")
    
    # إضافة مدير افتراضي
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", hash_password("admin123"), "مدير"))
    
    c.execute("CREATE TABLE IF NOT EXISTS cycles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, chicks_count INTEGER, chick_price REAL, feed_price_ton REAL, sell_price_kg REAL, target_weight REAL, start_date TEXT, status TEXT DEFAULT 'نشطة')")
    c.execute("CREATE TABLE IF NOT EXISTS daily_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INTEGER, day INTEGER, feed_kg REAL, water_l REAL, mortality INTEGER, weight_g REAL, temp REAL, humidity REAL, ammonia REAL, notes TEXT, UNIQUE(cycle_id, day))")
    c.execute("CREATE TABLE IF NOT EXISTS inventory_purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, qty_added REAL, min_limit REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS vet_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INTEGER, date TEXT, age INTEGER, symptoms TEXT, diagnosis TEXT, treatment TEXT, withdrawal_days INTEGER)")
    
    conn.commit()
    return conn

init_db()
conn = get_connection()


# =========================================================
# 5. SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# =========================================================
# 6. LOGIN
# =========================================================

if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1>🐔 BFM</h1><p>نظام إدارة مزارع التسمين</p></div>", unsafe_allow_html=True)
    with st.form("login_form"):
        u_input = st.text_input("اسم المستخدم")
        p_input = st.text_input("الرقم السري", type="password")
        if st.form_submit_button("دخول"):
            user_row = pd.read_sql_query("SELECT * FROM users WHERE username = ? AND password = ?", conn, params=(u_input.strip(), hash_password(p_input)))
            if not user_row.empty:
                st.session_state.logged_in = True
                st.session_state.username = user_row.iloc[0]["username"]
                st.session_state.role = user_row.iloc[0]["role"]
                st.rerun()
            else:
                st.error("خطأ في البيانات!")
    st.stop()


# =========================================================
# 8. SIDEBAR CONTENT
# =========================================================

st.sidebar.markdown("## 👤 " + st.session_state.username)
if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

# [هنا تضع باقي أكوادك الخاصة بـ (إدارة المستخدمين، إضافة دورة، اختيار الدورة)]
# ... (يمكنك وضع باقي الأكواد من النسخة السابقة هنا) ...

st.sidebar.warning("⚠️ يرجى اختيار دورة من القائمة.")

# =========================================================
# 12. MAIN APPLICATION
# =========================================================

st.title("🐔 BFM — نظام إدارة مزارع التسمين")

# [هنا بقية محتوى الصفحة الرئيسية]
st.info("مرحباً بك في النظام. الشريط الجانبي الآن يعمل بكفاءة ويختفي تماماً عند إغلاقه.")

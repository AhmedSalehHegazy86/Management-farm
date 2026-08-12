import datetime
import io
import sqlite3
import hashlib

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# 1. إعداد الصفحة
# =========================================================

st.set_page_config(
    page_title="Broiler Farm Manager V11 - Dynamic Sidebar",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="collapsed", # تم ضبطه ليفتح مغلقاً
)


# =========================================================
# 2. التصميم الاحترافي (تم دمج حل إخفاء الشريط الجانبي)
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
       SIDEBAR — DYNAMIC OVERLAY PANEL (تم تعديل هذا الجزء)
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

    /* عندما يكون الشريط مغلقاً - العرض صفر */
    [data-testid="stSidebar"][data-collapsed="true"] {
        width: 0px !important;
        min-width: 0px !important;
        overflow: hidden !important;
    }

    /* عندما يكون الشريط مفتوحاً - العرض 350 */
    [data-testid="stSidebar"]:not([data-collapsed="true"]) {
        width: 350px !important;
        min-width: 350px !important;
    }

    [data-testid="stSidebarContent"] {
        direction: rtl !important;
        padding: 1.5rem 1rem 2rem 1rem !important;
        width: 350px !important;
    }

    [data-testid="stSidebar"] * {
        direction: rtl !important;
        text-align: right !important;
        color: #f8fafc !important;
    }

    /* زر إظهار/إخفاء الشريط */
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
       TITLES & METRICS & FORMS
       ===================================================== */

    h1, h2, h3 { color: #e0f2fe !important; font-weight: 900 !important; }

    [data-testid="stMetric"] {
        background: #ffffff !important;
        padding: 18px !important;
        border-radius: 14px !important;
        border: 2px solid #38bdf8 !important;
        border-right: 8px solid #0284c7 !important;
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.25) !important;
    }

    [data-testid="stMetric"] * { color: #000000 !important; text-align: right !important; }
    [data-testid="stMetricValue"] { color: #0369a1 !important; font-size: 2rem !important; font-weight: 900 !important; }

    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.96) !important;
        padding: 20px !important;
        border-radius: 14px !important;
        border: 2px solid #38bdf8 !important;
        border-right: 8px solid #0284c7 !important;
        box-shadow: 0 5px 18px rgba(0,0,0,0.25) !important;
    }

    input, textarea, select {
        direction: rtl !important;
        text-align: right !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #0284c7 !important;
        border-radius: 7px !important;
        font-weight: 700 !important;
    }

    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #0284c7, #0369a1) !important;
        color: #ffffff !important;
        border-radius: 9px !important;
        font-weight: 900 !important;
    }

    /* Tabs & Dataframe */
    .stTabs [data-baseweb="tab"] { color: #e0f2fe !important; font-weight: 800 !important; }
    [data-testid="stDataFrame"] { background: #ffffff !important; border-radius: 12px !important; }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. المعايير القياسية
# =========================================================

STANDARD_BENCHMARKS = pd.DataFrame([{"day": i, "std_weight": 45 + (i-1)*50, "std_fcr": 0.9 + (i*0.02)} for i in range(1, 41)])


# =========================================================
# 4. DATABASE
# =========================================================

DB_NAME = "farm_manager_v11.db"

def get_connection(): return sqlite3.connect(DB_NAME, check_same_thread=False)
def hash_password(password): return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)")
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0: c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", hash_password("admin123"), "مدير"))
    c.execute("CREATE TABLE IF NOT EXISTS cycles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, chicks_count INTEGER, chick_price REAL, feed_price_ton REAL, sell_price_kg REAL, target_weight REAL, start_date TEXT, status TEXT DEFAULT 'نشطة')")
    c.execute("CREATE TABLE IF NOT EXISTS daily_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INTEGER, day INTEGER, feed_kg REAL, water_l REAL, mortality INTEGER, weight_g REAL, temp REAL, humidity REAL, ammonia REAL, notes TEXT, UNIQUE(cycle_id, day))")
    c.execute("CREATE TABLE IF NOT EXISTS inventory_purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, qty_added REAL, min_limit REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS vet_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INTEGER, date TEXT, age INTEGER, symptoms TEXT, diagnosis TEXT, treatment TEXT, withdrawal_days INTEGER)")
    conn.commit()
    return conn

init_db()
conn = get_connection()


# =========================================================
# 5. SESSION STATE & LOGIN
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1>🐔 BFM</h1><p>نظام إدارة مزارع التسمين</p></div>", unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة السر", type="password")
        if st.form_submit_button("دخول"):
            user = pd.read_sql("SELECT * FROM users WHERE username=? AND password=?", conn, params=(u.strip(), hash_password(p)))
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.username = user.iloc[0]["username"]
                st.session_state.role = user.iloc[0]["role"]
                st.rerun()
            else: st.error("خطأ!")
    st.stop()


# =========================================================
# 6. SIDEBAR
# =========================================================

st.sidebar.title(f"👤 {st.session_state.username}")
if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")

# [إدارة الدورات]
with st.sidebar.expander("➕ إضافة دورة"):
    with st.form("new_cycle"):
        n = st.text_input("اسم الدورة")
        if st.form_submit_button("حفظ"):
            c = conn.cursor()
            c.execute("INSERT INTO cycles (name, chicks_count, status) VALUES (?, 2000, 'نشطة')", (n,))
            conn.commit()
            st.rerun()

# [اختيار الدورة]
cycles = pd.read_sql("SELECT * FROM cycles WHERE status='نشطة'", conn)
selected_cycle_id = None
if not cycles.empty:
    choice = st.sidebar.selectbox("اختر الدورة", cycles["name"].tolist())
    selected_cycle_id = cycles[cycles["name"] == choice].iloc[0]["id"]
else:
    st.sidebar.warning("لا توجد دورة نشطة.")


# =========================================================
# 7. MAIN APP
# =========================================================

st.title("🐔 BFM — نظام إدارة مزارع التسمين")

if not selected_cycle_id:
    st.info("قم بإضافة واختيار دورة من الشريط الجانبي لبدء العمل.")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 لوحة التحكم", "📝 التسجيل اليومي", "📈 المعايير", "💰 التحليل المالي", "🖨️ التقارير"])

# لوحة التحكم
with tab1:
    st.subheader("إحصائيات الدورة")
    logs = pd.read_sql("SELECT * FROM daily_logs WHERE cycle_id=?", conn, params=(selected_cycle_id,))
    if not logs.empty:
        c1, c2 = st.columns(2)
        c1.metric("عدد الأيام", logs["day"].max())
        c2.metric("آخر وزن مسجل", f"{logs['weight_g'].iloc[-1]} جم")
    else:
        st.info("لا توجد بيانات.")

# التسجيل اليومي
with tab2:
    with st.form("daily_form"):
        c1, c2 = st.columns(2)
        day = c1.number_input("اليوم", 1, 40)
        w = c2.number_input("الوزن جم")
        if st.form_submit_button("حفظ"):
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO daily_logs (cycle_id, day, weight_g) VALUES (?, ?, ?)", (selected_cycle_id, day, w))
            conn.commit()
            st.rerun()

# معايير
with tab3:
    st.write("مقارنة الوزن الفعلي بالمعياري...")

# مالي
with tab4:
    st.write("تحليل الأرباح...")

# تقارير
with tab5:
    st.write("تحميل التقارير...")

st.markdown("<hr><div style='text-align:center;'>BFM Manager V11</div>", unsafe_allow_html=True)

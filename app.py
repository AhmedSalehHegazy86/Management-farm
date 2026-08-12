import streamlit as st
import pandas as pd
import sqlite3
import hashlib

# =========================================================
# 1. إعداد الصفحة
# =========================================================
st.set_page_config(
    page_title="Broiler Farm Manager",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# =========================================================
# 2. التنسيق (CSS آمن ومجرب)
# =========================================================
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        direction: rtl !important;
        text-align: right !important;
        background: radial-gradient(circle at top right, #1d4ed8 0%, #0f172a 45%, #020617 100%) !important;
    }
    h1, h2, h3, .stMarkdown { color: #ffffff !important; }
    .stButton > button {
        background: linear-gradient(135deg, #0284c7, #0369a1) !important;
        color: white !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 3. قواعد البيانات (هيكلية كاملة)
# =========================================================
def init_db():
    conn = sqlite3.connect("farm_manager_v11.db")
    c = conn.cursor()
    # المستخدمين
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)")
    # الدورات
    c.execute("CREATE TABLE IF NOT EXISTS cycles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, chicks_count INTEGER, status TEXT DEFAULT 'نشطة')")
    # السجلات اليومية
    c.execute("CREATE TABLE IF NOT EXISTS daily_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INTEGER, day INTEGER, feed_kg REAL, mortality INTEGER, weight_g REAL)")
    
    # إضافة مدير افتراضي
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?, ?)", ("admin", hashlib.sha256("admin123".encode()).hexdigest(), "مدير"))
    conn.commit()
    conn.close()

init_db()

# =========================================================
# 4. نظام تسجيل الدخول
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🐔 تسجيل الدخول")
    with st.form("login_form"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            conn = sqlite3.connect("farm_manager_v11.db")
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hashlib.sha256(p.encode()).hexdigest()))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("بيانات خاطئة")
    st.stop()

# =========================================================
# 5. التطبيق الرئيسي (بعد تسجيل الدخول)
# =========================================================
st.sidebar.title(f"مرحباً {st.session_state.user}")
if st.sidebar.button("تسجيل خروج"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🐔 نظام إدارة المزرعة")

# التبويبات الرئيسية
tab1, tab2, tab3 = st.tabs(["📊 لوحة التحكم", "➕ إضافة بيانات", "📋 السجلات"])

with tab1:
    st.subheader("مؤشرات الأداء")
    col1, col2 = st.columns(2)
    col1.metric("عدد الكتاكيت", "5000")
    col2.metric("الحالة", "نشطة")

with tab2:
    st.subheader("تسجيل بيانات يومية")
    with st.form("daily_data"):
        day = st.number_input("اليوم", min_value=1)
        feed = st.number_input("العلف (كجم)")
        mortality = st.number_input("النافِق", min_value=0)
        if st.form_submit_button("حفظ"):
            st.success(f"تم حفظ بيانات اليوم {day}")

with tab3:
    st.subheader("السجلات التاريخية")
    # هنا يتم عرض الداتا فريم من قاعدة البيانات
    st.write("لا توجد بيانات حالياً")


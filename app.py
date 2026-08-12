import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- 1. إعدادات الصفحة (يجب أن يكون أول أمر) ---
st.set_page_config(
    page_title="مدير مزارع التسمين",
    layout="wide",
    initial_sidebar_state="collapsed" # هذا الأمر يجبر الشريط على الانغلاق عند الفتح
)

# --- 2. التنسيق (CSS) ---
st.markdown("""
    <style>
    /* خلفية البرنامج (أفتح من الشريط) */
    .stApp {
        background-color: #f0f8ff !important; 
    }
    /* الشريط الجانبي (أزرق غامق) */
    [data-testid="stSidebar"] {
        background-color: #003366 !important;
    }
    /* نصوص الشريط الجانبي */
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. إدارة قاعدة البيانات ---
def get_connection():
    conn = sqlite3.connect("farm_manager_v9.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # إنشاء الجداول الأساسية
    c.execute("""CREATE TABLE IF NOT EXISTS cycles 
                 (id INTEGER PRIMARY KEY, name TEXT, chicks_count INT, start_date TEXT)""")
    conn.commit()
    conn.close()

init_db()

# --- 4. واجهة التطبيق ---
st.title("🐔 نظام إدارة مزارع التسمين")

# إضافة دورة (في الشريط الجانبي)
with st.sidebar:
    st.header("إضافة دورة جديدة")
    with st.form("add_cycle"):
        name = st.text_input("اسم الدورة")
        count = st.number_input("عدد الكتاكيت", value=1000)
        submit = st.form_submit_button("حفظ")
        if submit:
            conn = get_connection()
            conn.execute("INSERT INTO cycles (name, chicks_count, start_date) VALUES (?, ?, ?)", 
                         (name, count, str(datetime.date.today())))
            conn.commit()
            conn.close()
            st.success("تم الحفظ")
            st.rerun()

# عرض الدورات
conn = get_connection()
df = pd.read_sql("SELECT * FROM cycles", conn)
conn.close()

if not df.empty:
    st.subheader("الدورات الحالية")
    st.dataframe(df, use_container_width=True)
else:
    st.info("لا توجد دورات حالياً، استخدم الشريط الجانبي لإضافة دورة.")

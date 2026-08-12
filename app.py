import datetime
import io
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. إعدادات الصفحة (تم تعيين الحالة للإنغلاق)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Broiler Farm Manager V9",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="collapsed", # هنا يتم فرض غلق الشريط الجانبي عند البداية
)

st.markdown(
    """
    <style>
    /* جعل خلفية التطبيق فاتحة جداً (أفتح من الشريط الجانبي) */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        direction: rtl;
        background-color: #f4f9fd !important; 
    }
    
    /* الشريط الجانبي بلون أزرق داكن (عمق البحر) */
    [data-testid="stSidebar"] {
        right: 0 !important;
        left: auto !important;
        direction: rtl !important;
        text-align: right !important;
        background-color: #03045e !important;
        border-left: 3px solid #00b4d8;
    }

    /* تنسيق النصوص داخل الشريط الجانبي */
    [data-testid="stSidebar"] div, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        text-align: right !important;
        color: #ffffff !important;
        font-weight: 500;
    }

    /* عناوين الواجهة الرئيسية */
    h1, h2, h3 {
        color: #03045e;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* تنسيق مربعات الإحصائيات */
    .stMetric { 
        background: #ffffff; 
        padding: 15px; 
        border-radius: 12px; 
        border-right: 6px solid #0077b6; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 2. بقية الكود (العمليات والبيانات)
# ---------------------------------------------------------

# المعايير القياسية
STANDARD_BENCHMARKS = pd.DataFrame([{"day": i, "std_weight": 45 + (i*50), "std_fcr": 0.9 + (i*0.02)} for i in range(1, 41)])

# اتصال قاعدة البيانات
def get_connection():
    return sqlite3.connect("farm_manager_v9.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS cycles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, chicks_count INT, chick_price REAL, feed_price_ton REAL, sell_price_kg REAL, target_weight REAL, start_date TEXT, status TEXT DEFAULT 'نشطة')")
    c.execute("CREATE TABLE IF NOT EXISTS daily_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INT, day INT, feed_kg REAL, water_l REAL, mortality INT, weight_g REAL, temp REAL, humidity REAL, ammonia REAL, notes TEXT, UNIQUE(cycle_id, day) ON CONFLICT REPLACE)")
    c.execute("CREATE TABLE IF NOT EXISTS inventory_purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, qty_added REAL, min_limit REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS vet_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INT, date TEXT, age INT, symptoms TEXT, diagnosis TEXT, treatment TEXT, withdrawal_days INT)")
    conn.commit()

init_db()

# القائمة الجانبية (لإضافة الدورات)
st.sidebar.title("🐔 إدارة الدورات")
conn = get_connection()

with st.sidebar.expander("➕ إضافة دورة جديدة"):
    with st.form("add_new_cycle_form"):
        c_name = st.text_input("اسم الدورة", f"دورة {datetime.date.today()}")
        c_chicks = st.number_input("عدد الكتاكيت", value=2000)
        if st.form_submit_button("حفظ الدورة"):
            c = conn.cursor()
            c.execute("INSERT INTO cycles (name, chicks_count, chick_price, feed_price_ton, sell_price_kg, target_weight, start_date) VALUES (?, ?, ?, ?, ?, ?, ?)", (c_name, c_chicks, 35.0, 24000.0, 85.0, 2.2, str(datetime.date.today())))
            conn.commit()
            st.rerun()

# اختيار الدورة
cycles_df = pd.read_sql("SELECT * FROM cycles WHERE status='نشطة'", conn)
if not cycles_df.empty:
    cycle_dict = dict(zip(cycles_df["name"], cycles_df["id"]))
    selected_name = st.sidebar.selectbox("اختر الدورة", list(cycle_dict.keys()))
    selected_cycle_id = cycle_dict[selected_name]
    
    # واجهة التطبيق
    st.title(f"لوحة تحكم: {selected_name}")
    
    # تبويبات العمل
    tab1, tab2 = st.tabs(["📊 الإحصائيات", "📝 تسجيل البيانات"])
    
    with tab1:
        st.subheader("ملخص الدورة")
        logs_df = pd.read_sql(f"SELECT * FROM daily_logs WHERE cycle_id={selected_cycle_id}", conn)
        if not logs_df.empty:
            st.line_chart(logs_df.set_index("day")[["weight_g"]])
        else:
            st.info("لا توجد بيانات مسجلة بعد.")
            
    with tab2:
        with st.form("daily_entry"):
            day = st.number_input("اليوم", 1, 40)
            weight = st.number_input("الوزن (جم)", 0.0)
            if st.form_submit_button("حفظ"):
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO daily_logs (cycle_id, day, weight_g) VALUES (?, ?, ?)", (selected_cycle_id, day, weight))
                conn.commit()
                st.success("تم الحفظ")
else:
    st.warning("يرجى إضافة دورة من القائمة الجانبية للبدء.")

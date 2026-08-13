import datetime
import io
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. إعدادات الصفحة وتصميم الخلفية الزرقاء المتدرجة الداكنة
# ---------------------------------------------------------
st.set_page_config(
    page_title="Broiler Farm Manager - Secure Auth",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        direction:rt;
        right: auto !important;
        left: 0 !important;
        background-color: #0f172a !important;
        border-left: 0px solid #38bdf8 !important;
    }
 
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        text-align: right !important;
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%) !important; 
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] * {
        text-align: right !important;
        color: #f8fafc !important;
    }

    .stMarkdown, .stText, p, span, label, div {
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
        text-align: right !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #0284c7 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
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

# ---------------------------------------------------------
# 2. المعايير القياسية للسلالة (40 يوماً)
# ---------------------------------------------------------
STANDARD_BENCHMARKS = pd.DataFrame(
    [
        {"day": 1, "std_weight": 45, "std_fcr": 0.92},
        {"day": 2, "std_weight": 100, "std_fcr": 0.94},
        {"day": 3, "std_weight": 156, "std_fcr": 0.96},
        {"day": 4, "std_weight": 211, "std_fcr": 0.98},
        {"day": 5, "std_weight": 266, "std_fcr": 1.00},
        {"day": 6, "std_weight": 321, "std_fcr": 1.02},
        {"day": 7, "std_weight": 377, "std_fcr": 1.04},
        {"day": 8, "std_weight": 432, "std_fcr": 1.06},
        {"day": 9, "std_weight": 487, "std_fcr": 1.08},
        {"day": 10, "std_weight": 542, "std_fcr": 1.10},
        {"day": 11, "std_weight": 598, "std_fcr": 1.12},
        {"day": 12, "std_weight": 653, "std_fcr": 1.14},
        {"day": 13, "std_weight": 708, "std_fcr": 1.16},
        {"day": 14, "std_weight": 763, "std_fcr": 1.18},
        {"day": 15, "std_weight": 819, "std_fcr": 1.20},
        {"day": 16, "std_weight": 874, "std_fcr": 1.22},
        {"day": 17, "std_weight": 929, "std_fcr": 1.24},
        {"day": 18, "std_weight": 984, "std_fcr": 1.26},
        {"day": 19, "std_weight": 1040, "std_fcr": 1.28},
        {"day": 20, "std_weight": 1095, "std_fcr": 1.30},
        {"day": 21, "std_weight": 1150, "std_fcr": 1.32},
        {"day": 22, "std_weight": 1205, "std_fcr": 1.34},
        {"day": 23, "std_weight": 1261, "std_fcr": 1.36},
        {"day": 24, "std_weight": 1316, "std_fcr": 1.38},
        {"day": 25, "std_weight": 1371, "std_fcr": 1.40},
        {"day": 26, "std_weight": 1426, "std_fcr": 1.42},
        {"day": 27, "std_weight": 1482, "std_fcr": 1.44},
        {"day": 28, "std_weight": 1537, "std_fcr": 1.46},
        {"day": 29, "std_weight": 1592, "std_fcr": 1.48},
        {"day": 30, "std_weight": 1647, "std_fcr": 1.50},
        {"day": 31, "std_weight": 1703, "std_fcr": 1.52},
        {"day": 32, "std_weight": 1758, "std_fcr": 1.54},
        {"day": 33, "std_weight": 1813, "std_fcr": 1.56},
        {"day": 34, "std_weight": 1868, "std_fcr": 1.58},
        {"day": 35, "std_weight": 1924, "std_fcr": 1.60},
        {"day": 36, "std_weight": 1979, "std_fcr": 1.62},
        {"day": 37, "std_weight": 2034, "std_fcr": 1.64},
        {"day": 38, "std_weight": 2089, "std_fcr": 1.66},
        {"day": 39, "std_weight": 2145, "std_fcr": 1.68},
        {"day": 40, "std_weight": 2200, "std_fcr": 1.70},
    ]
)

# ---------------------------------------------------------
# 3. إدارة قاعدة البيانات وإنشاء الجداول
# ---------------------------------------------------------
def get_connection():
    return sqlite3.connect("farm_manager_v9.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "مدير"))

    c.execute("""CREATE TABLE IF NOT EXISTS cycles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, chicks_count INT, chick_price REAL, feed_price_ton REAL,
        sell_price_kg REAL, target_weight REAL, start_date TEXT, status TEXT DEFAULT 'نشطة'
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS daily_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INT, day INT,
        feed_kg REAL, water_l REAL, mortality INT, weight_g REAL,
        temp REAL, humidity REAL, ammonia REAL, notes TEXT,
        UNIQUE(cycle_id, day) ON CONFLICT REPLACE
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS inventory_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, qty_added REAL, min_limit REAL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS vet_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INT, date TEXT, age INT,
        symptoms TEXT, diagnosis TEXT, treatment TEXT, withdrawal_days INT
    )""")

    c.execute("SELECT COUNT(*) FROM inventory_purchases")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO inventory_purchases (item_name, qty_added, min_limit) VALUES (?, ?, ?)",
            [
                ("علف بادئ (كجم)", 2000.0, 500.0),
                ("علف نامي (كجم)", 3000.0, 700.0),
                ("علف ناهي (كجم)", 2500.0, 600.0),
                ("مطهر (لتر)", 20.0, 5.0),
            ],
        )
    conn.commit()

init_db()
conn = get_connection()

# ---------------------------------------------------------
# 4. نظام المصادقة وتسجيل الدخول (Authentication)
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول - نظام إدارة مزارع التسمين")
    with st.form("login_form"):
        u_input = st.text_input("اسم المستخدم")
        p_input = st.text_input("الرقم السري", type="password")
        submit_login = st.form_submit_button("دخول للنظام")

        if submit_login:
            user_row = pd.read_sql(f"SELECT * FROM users WHERE username='{u_input}' AND password='{p_input}'", conn)
            if not user_row.empty:
                st.session_state.logged_in = True
                st.session_state.username = user_row.iloc[0]["username"]
                st.session_state.role = user_row.iloc[0]["role"]
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو الرقم السري غير صحيح!")
    st.stop()

# ---------------------------------------------------------
# 5. الشريط الجانبي (Sidebar) للتحكم وإدارة الدورات والمستخدمين
# ---------------------------------------------------------
st.sidebar.title(f"👤 مرحبًا: {st.session_state.username}")
st.sidebar.markdown(f"**الصلاحية:** {st.session_state.role}")

if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.title("🐔 لوحة التحكم والإدارة")

if st.session_state.role == "مدير":
    with st.sidebar.expander("👥 إدارة المستخدمين (إضافة مستخدم)", expanded=False):
        with st.form("add_user_form"):
            new_user = st.text_input("اسم المستخدم الجديد")
            new_pass = st.text_input("الرقم السري", type="password")
            new_role = st.selectbox("الصلاحية", ["مستخدم عادي", "مدير"])
            if st.form_submit_button("إضافة المستخدم"):
                if new_user and new_pass:
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_user, new_pass, new_role))
                        conn.commit()
                        st.success(f"تم إضافة المستخدم {new_user} بنجاح!")
                    except sqlite3.IntegrityError:
                        st.error("اسم المستخدم موجود مسبقاً!")
                else:
                    st.warning("يرجى إدخال اسم المستخدم والرقم السري!")

with st.sidebar.expander("➕ إضافة دورة تسمين جديدة", expanded=False):
    with st.form("add_new_cycle_form_sidebar"):
        c_name = st.text_input("اسم الدورة الجديدة", f"دورة جديدة {datetime.date.today()}")
        c_chicks = st.number_input("عدد الكتاكيت الأولي", value=2000, step=100)
        c_chick_p = st.number_input("سعر الكتكوت (جنية)", value=35.0)
        c_feed_p = st.number_input("سعر طن العلف (جنية)", value=24000.0)
        c_sell_p = st.number_input("سعر بيع الكيلو (جنية)", value=85.0)
        c_target_w = st.number_input("الوزن المستهدف (كجم)", value=2.2)
        if st.form_submit_button("حفظ وتفعيل الدورة"):
            c = conn.cursor()
            c.execute(
                """INSERT INTO cycles (name, chicks_count, chick_price, feed_price_ton, sell_price_kg, target_weight, start_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (c_name, c_chicks, c_chick_p, c_feed_p, c_sell_p, c_target_w, str(datetime.date.today())),
            )
            conn.commit()
            st.success("تم إضافة الدورة بنجاح!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🔄 اختيار وتعديل الدورة النشطة")
cycles_df = pd.read_sql("SELECT * FROM cycles WHERE status='نشطة'", conn)

if cycles_df.empty:
    st.sidebar.warning("⚠️ لا توجد دورة نشطة حالياً. أضف دورة جديدة من الخيار أعلاه.")
    selected_cycle_id = None
else:
    cycle_dict = dict(zip(cycles_df["name"], cycles_df["id"]))
    selected_cycle_name = st.sidebar.selectbox("اختر الدورة النشطة للعمل عليها", list(cycle_dict.keys()))
    selected_cycle_id = cycle_dict[selected_cycle_name]
    curr_cycle = cycles_df[cycles_df["id"] == selected_cycle_id].iloc[0]

    st.sidebar.markdown(f"🗓️ **تاريخ البدء:** {curr_cycle['start_date']}")
    st.sidebar.markdown(f"🐤 **العدد الأولي:** {curr_cycle['chicks_count']:,} طائر")

    with st.sidebar.expander("⚙️ تعديل أسعار وإعدادات الدورة الحالية"):
        with st.form("edit_cycle_form_sidebar"):
            e_chick_p = st.number_input("تعديل سعر الكتكوت (جنية)", value=float(curr_cycle["chick_price"]))
            e_feed_p = st.number_input("تعديل سعر طن العلف (جنية)", value=float(curr_cycle["feed_price_ton"]))
            e_sell_p = st.number_input("تعديل سعر البيع/كجم (جنية)", value=float(curr_cycle["sell_price_kg"]))
            if st.form_submit_button("حفظ التحديثات"):
                c = conn.cursor()
                c.execute(
                    "UPDATE cycles SET chick_price=?, feed_price_ton=?, sell_price_kg=? WHERE id=?",
                    (e_chick_p, e_feed_p, e_sell_p, selected_cycle_id),
                )
                conn.commit()
                st.success("تم التحديث بنجاح!")
                st.rerun()

# ---------------------------------------------------------
# 6. واجهة التشغيل والعمليات الحسابية الرئيسية
# ---------------------------------------------------------
st.title("🐔 BFM - نظام إدارة مزارع التسمين")

if selected_cycle_id:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "📊 لوحة التحكم الأوتوماتيكية",
            "📝 التسجيل اليومي",
            "📈 المقارنة بالمعايير القياسية",
            "📦 إدارة المخزون",
            "💉 السجل البيطري",
            "💰 التحليل المالي وحساسية الأرباح",
            "🖨️ التقارير المطبوعة وتصدير Excel",
        ]
    )

    logs_df = pd.read_sql(
        f"SELECT * FROM daily_logs WHERE cycle_id={selected_cycle_id} ORDER BY day ASC",
        conn,
    )

    tot_chicks = int(curr_cycle["chicks_count"])
    tot_mortality = int(logs_df["mortality"].sum()) if not logs_df.empty else 0
    live_birds = tot_chicks - tot_mortality
    mortality_pct = (tot_mortality / tot_chicks) * 100.0 if tot_chicks > 0 else 0.0
    liveability = 100.0 - mortality_pct

    tot_feed_kg = float(logs_df["feed_kg"].sum()) if not logs_df.empty else 0.0
    tot_water_l = float(logs_df["water_l"].sum()) if not logs_df.empty else 0.0

    last_day = int(logs_df["day"].max()) if not logs_df.empty else 1
    last_weight_g = (
        float(logs_df[logs_df["weight_g"] > 0]["weight_g"].iloc[-1])
        if not logs_df[logs_df["weight_g"] > 0].empty
        else 45.0
    )

    tot_weight_kg = (live_birds * last_weight_g) / 1000.0
    fcr = (tot_feed_kg / tot_weight_kg) if tot_weight_kg > 0 else 0.0
    epef = (
        ((liveability * (last_weight_g / 1000.0)) / (last_day * fcr)) * 100.0
        if (fcr > 0 and last_day > 0)
        else 0.0
    )

    # --- Tab 1: لوحة التحكم ---
    with tab1:
        st.subheader(f"📌 ملخص أداء الدورة الحالية: ({curr_cycle['name']})")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("الطيور الحية الحالية", f"{live_birds:,} طائر")
        c2.metric("نسبة النفوق الإجمالية", f"{mortality_pct:.2f}%")
        c3.metric("إجمالي العلف المستهلك", f"{tot_feed_kg:,.1f} كجم")
        c4.metric("معدل التحويل (FCR)", f"{fcr:.2f}")
        c5.metric("معامل الكفاءة (EPEF)", f"{epef:.1f}")

        st.markdown("---")
        if mortality_pct > 5.0:
            st.error("🚨 تنبيه خطر: نسبة النفوق تتجاوز الحد الأقصى المقبول (5%)!")
        if fcr > 1.8 and fcr > 0:
            st.warning("⚠️ تنبيه: معدل التحويل الغذائي (FCR) أعلى من 1.8!")

        col_left, col_right = st.columns(2)
        with col_left:
            st.write("### 🌡️ درجة الحرارة والرطوبة اليومية")
            if not logs_df.empty:
                fig_env = go.Figure()
                fig_env.add_trace(go.Scatter(x=logs_df["day"], y=logs_df["temp"], name="الحرارة (°C)", line=dict(color="#ef4444", width=3)))
                fig_env.add_trace(go.Scatter(x=logs_df["day"], y=logs_df["humidity"], name="الرطوبة (%)", line=dict(color="#0284c7", width=3)))
                fig_env.update_layout(xaxis_title="اليوم", yaxis_title="القيمة", margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.9)')
                st.plotly_chart(fig_env, use_container_width=True)

        with col_right:
            st.write("### 💧 استهلاك العلف والمياه اليومي")
            if not logs_df.empty:
                fig_cons = go.Figure()
                fig_cons.add_trace(go.Bar(x=logs_df["day"], y=logs_df["feed_kg"], name="العلف (كجم)", marker_color="#f59e0b"))
                fig_cons.add_trace(go.Bar(x=logs_df["day"], y=logs_df["water_l"], name="المياه (لتر)", marker_color="#0284c7"))
                fig_cons.update_layout(barmode="group", xaxis_title="اليوم", yaxis_title="الكمية", margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.9)')
                st.plotly_chart(fig_cons, use_container_width=True)

    # --- Tab 2: التسجيل اليومي ---
    with tab2:
        st.subheader("📝 إدخال وتعديل البيانات اليومية للدورة")
        with st.form("daily_entry_form"):
            col1, col2, col3, col4, col5 = st.columns(5)
            next_day_val = int(last_day if logs_df.empty else min(last_day + 1, 40))
            in_day = col1.number_input("اليوم (1 - 40)", min_value=1, max_value=40, value=next_day_val)
            in_feed = col2.number_input("استهلاك العلف (كجم)", min_value=0.0, step=10.0)
            in_water = col3.number_input("استهلاك المياه (لتر)", min_value=0.0, step=10.0)
            in_mort = col4.number_input("النفوق اليومي (طائر)", min_value=0, step=1)
            in_weight = col5.number_input("متوسط الوزن الفعلي (جم)", min_value=0.0, step=10.0)

            col6, col7, col8, col9 = st.columns(4)
            in_temp = col6.number_input("الحرارة (°C)", value=30.0)
            in_hum = col7.number_input("الرطوبة (%)", value=60.0)
            in_amm = col8.number_input("الأمونيا (PPM)", value=10.0)
            in_notes = col9.text_input("ملاحظات اليوم")

            if st.form_submit_button("💾 حفظ بيانات اليوم"):
                c = conn.cursor()
                c.execute(
                    """INSERT OR REPLACE INTO daily_logs 
                    (cycle_id, day, feed_kg, water_l, mortality, weight_g, temp, humidity, ammonia, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (selected_cycle_id, in_day, in_feed, in_water, in_mort, in_weight, in_temp, in_hum, in_amm, in_notes),
                )
                conn.commit()
                st.success(f"تم حفظ بيانات اليوم {in_day} بنجاح!")
                st.rerun()

        st.markdown("---")
        st.write("### 📋 جدول السجلات اليومية المكتملة")
        if not logs_df.empty:
            calc_df = logs_df.copy()
            calc_df["feed_cum"] = calc_df["feed_kg"].cumsum()
            calc_df["mort_cum"] = calc_df["mortality"].cumsum()
            calc_df["live_birds_day"] = tot_chicks - calc_df["mort_cum"]
            calc_df["biomass_day_kg"] = (calc_df["live_birds_day"] * calc_df["weight_g"]) / 1000.0
            calc_df["fcr_cum"] = calc_df["feed_cum"] / calc_df["biomass_day_kg"]
            calc_df["fcr_cum"] = calc_df["fcr_cum"].round(2)

            display_cols = ["day", "feed_kg", "water_l", "mortality", "weight_g", "biomass_day_kg", "fcr_cum", "temp", "humidity", "ammonia", "notes"]
            renamed_cols = {
                "day": "اليوم", "feed_kg": "العلف (كجم)", "water_l": "المياه (لتر)",
                "mortality": "النفوق", "weight_g": "الوزن (جم)", "biomass_day_kg": "الكتلة الحية (كجم)",
                "fcr_cum": "FCR تراكمي", "temp": "الحرارة °C", "humidity": "الرطوبة %",
                "ammonia": "الأمونيا PPM", "notes": "ملاحظات",
            }
            st.dataframe(calc_df[display_cols].rename(columns=renamed_cols), use_container_width=True)

    # --- Tab 3: المقارنة بالمعايير القياسية ---
    with tab3:
        st.subheader("📈 مقارنة نمو الوزن الفعلي بجدول السلالة القياسي")
        merged_df = pd.merge(STANDARD_BENCHMARKS, logs_df[["day", "weight_g", "feed_kg"]], on="day", how="left")

        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(x=merged_df["day"], y=merged_df["std_weight"], name="الوزن القياسي (جم)", line=dict(color="#64748b", dash="dash", width=2)))
        fig_w.add_trace(go.Scatter(x=merged_df["day"], y=merged_df["weight_g"], name="الوزن الفعلي (جم)", line=dict(color="#0284c7", width=4)))
        fig_w.update_layout(title="منحنى النمو مقارنة بالمعايير القياسية", xaxis_title="اليوم", yaxis_title="متوسط الوزن (جم)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.9)')
        st.plotly_chart(fig_w, use_container_width=True)

    # --- Tab 4: إدارة المخزون الديناميكي ---
    with tab4:
        st.subheader("📦 رصيد المخزون الأوتوماتيكي وحالة التوريد")
        starter_used = logs_df[logs_df["day"] <= 10]["feed_kg"].sum() if not logs_df.empty else 0.0
        grower_used = logs_df[(logs_df["day"] > 10) & (logs_df["day"] <= 25)]["feed_kg"].sum() if not logs_df.empty else 0.0
        finisher_used = logs_df[logs_df["day"] > 25]["feed_kg"].sum() if not logs_df.empty else 0.0

        purchases_df = pd.read_sql("SELECT item_name, SUM(qty_added) as total_added, min_limit FROM inventory_purchases GROUP BY item_name", conn)

        inventory_status = []
        for _, row in purchases_df.iterrows():
            item = row["item_name"]
            added = float(row["total_added"])
            limit = float(row["min_limit"])
            used = starter_used if "بادئ" in item else grower_used if "نامي" in item else finisher_used if "ناهي" in item else 0.0
            avail = added - used
            status = "⚠️ إعادة طلب" if avail < limit else "✅ متوفر"
            inventory_status.append({"الصنف": item, "إجمالي المشتروات": added, "المستهلك للدورة": used, "الرصيد المتاح": avail, "حد الأمان": limit, "الحالة": status})

        inv_summary_df = pd.DataFrame(inventory_status)
        reorder = inv_summary_df[inv_summary_df["الرصيد المتاح"] < inv_summary_df["حد الأمان"]]
        if not reorder.empty:
            for _, r in reorder.iterrows():
                st.warning(f"⚠️ تنبيه إعادة طلب: صنف ({r['الصنف']}) انخفض رصيده إلى {r['الرصيد المتاح']:.1f} (حد الأمان: {r['حد الأمان']})")

        st.dataframe(inv_summary_df, use_container_width=True)

        with st.expander("➕ إضافة شحنة/توريد جديد للمخزون"):
            with st.form("add_stock_form"):
                st_item = st.selectbox("الصنف", inv_summary_df["الصنف"].tolist())
                st_qty = st.number_input("الكمية المضافة", min_value=0.0, step=100.0)
                if st.form_submit_button("حفظ التوريد"):
                    c = conn.cursor()
                    c.execute("INSERT INTO inventory_purchases (item_name, qty_added, min_limit) VALUES (?, ?, ?)", (st_item, st_qty, 500.0))
                    conn.commit()
                    st.success("تم إضافة الكمية للمخزون!")
                    st.rerun()

    # --- Tab 5: السجل البيطري ---
    with tab5:
        st.subheader("💉 السجل البيطري وفترات الأمان وسحب الدواء")
        with st.form("vet_entry"):
            c1, c2, c3, c4 = st.columns(4)
            v_date = c1.date_input("التاريخ", datetime.date.today())
            v_age = c2.number_input("العمر (أيام)", min_value=1, value=int(last_day))
            v_sym = c3.text_input("الأعراض المرضية")
            v_diag = c4.text_input("التشخيص البيطري")

            c5, c6 = st.columns(2)
            v_treat = c5.text_input("العلاج / التحصينة")
            v_withdraw = c6.number_input("فترة سحب الدواء (أيام)", min_value=0, value=3)

            if st.form_submit_button("💾 حفظ السجل البيطري"):
                c = conn.cursor()
                c.execute(
                    """INSERT INTO vet_logs (cycle_id, date, age, symptoms, diagnosis, treatment, withdrawal_days)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (selected_cycle_id, str(v_date), v_age, v_sym, v_diag, v_treat, v_withdraw),
                )
                conn.commit()
                st.success("تم تسجيل التشخيص والعلاج بنجاح!")
                st.rerun()

        vet_df = pd.read_sql(f"SELECT * FROM vet_logs WHERE cycle_id={selected_cycle_id}", conn)
        if not vet_df.empty:
            vet_df["انتهاء فترة السحب (عمر)"] = vet_df["age"] + vet_df["withdrawal_days"]
            renamed_vet = {"date": "التاريخ", "age": "العمر", "symptoms": "الأعراض", "diagnosis": "التشخيص", "treatment": "العلاج", "withdrawal_days": "فترة السحب (أيام)"}
            st.dataframe(vet_df.rename(columns=renamed_vet), use_container_width=True)

    # --- Tab 6: التحليل المالي وحساسية الأرباح ---
    with tab6:
        st.subheader("💰 التحليل المالي ونقطة التعادل للدورة")
        chick_cost = tot_chicks * float(curr_cycle["chick_price"])
        feed_cost = (tot_feed_kg / 1000.0) * float(curr_cycle["feed_price_ton"])
        total_costs = chick_cost + feed_cost

        est_revenue = tot_weight_kg * float(curr_cycle["sell_price_kg"])
        net_profit = est_revenue - total_costs
        breakeven_kg = total_costs / float(curr_cycle["sell_price_kg"]) if float(curr_cycle["sell_price_kg"]) > 0 else 0.0
        cost_per_chick = total_costs / tot_chicks if tot_chicks > 0 else 0.0
        cost_per_kg = total_costs / tot_weight_kg if tot_weight_kg > 0 else 0.0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("إجمالي التكاليف الفعلية", f"{total_costs:,.2f} ج.م")
        m2.metric("إجمالي قيمة الوزن الحقيقي", f"{est_revenue:,.2f} ج.م")
        m3.metric("صافي الربح الحقيقي حالياً", f"{net_profit:,.2f} ج.م")
        m4.metric("نقطة التعادل (كجم)", f"{breakeven_kg:,.1f} كجم")

        st.info(f"💡 **تكلفة الكتكوت الإجمالية:** {cost_per_chick:.2f} جنية | **تكلفة إنتاج كجم لحم:** {cost_per_kg:.2f} جنية")

        st.markdown("---")
        st.subheader("🎛️ تحليل الحساسية للربحية والسيناريوهات")
        col_s1, col_s2, col_s3 = st.columns(3)
        sim_feed_price = col_s1.slider("سعر طن العلف (جنية)", min_value=15000, max_value=35000, value=int(curr_cycle["feed_price_ton"]), step=500)
        sim_sell_price = col_s2.slider("سعر بيع الكيلو (جنية)", min_value=50, max_value=120, value=int(curr_cycle["sell_price_kg"]), step=1)
        sim_mortality = col_s3.slider("نسبة النفوق المتوقعة النهائي (%)", min_value=1.0, max_value=15.0, value=float(mortality_pct if mortality_pct > 0 else 3.0), step=0.5)

        sim_live_birds = tot_chicks * (1.0 - sim_mortality / 100.0)
        sim_tot_weight_kg = sim_live_birds * (float(curr_cycle["target_weight"]) if last_weight_g < 500 else (last_weight_g / 1000.0))
        sim_costs = chick_cost + ((sim_tot_weight_kg * 1.6) / 1000.0) * sim_feed_price
        sim_revenue = sim_tot_weight_kg * sim_sell_price
        sim_profit = sim_revenue - sim_costs

        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.metric("التكلفة التقديرية", f"{sim_costs:,.2f} ج.م")
        s_col2.metric("الإيراد التقديري", f"{sim_revenue:,.2f} ج.م")
        s_col3.metric("صافي الربح التقديري", f"{sim_profit:,.2f} ج.م", delta=f"{sim_profit - net_profit:,.2f} ج.م")

    # --- Tab 7: التقارير المطبوعة وتصدير Excel ---
    with tab7:
        st.subheader("📄 تصدير التقارير الرسمية والطباعة")

        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            st.write("### 📥 1. تصدير التقرير المالي والتشغيلي كملف Excel")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                summary_report = pd.DataFrame([
                    {"المؤشر": "اسم الدورة", "القيمة": str(curr_cycle["name"])},
                    {"المؤشر": "تاريخ البدء", "القيمة": str(curr_cycle["start_date"])},
                    {"المؤشر": "عدد الطيور الأولي", "القيمة": tot_chicks},
                    {"المؤشر": "الطيور الحية", "القيمة": live_birds},
                    {"المؤشر": "نسبة النفوق %", "القيمة": f"{mortality_pct:.2f}%"},
                    {"المؤشر": "إجمالي العلف (كجم)", "القيمة": tot_feed_kg},
                    {"المؤشر": "معدل التحويل (FCR)", "القيمة": round(fcr, 2)},
                    {"المؤشر": "معامل الكفاءة (EPEF)", "القيمة": round(epef, 1)},
                    {"المؤشر": "إجمالي التكاليف (ج.م)", "القيمة": total_costs},
                    {"المؤشر": "إجمالي الإيرادات (ج.م)", "القيمة": est_revenue},
                    {"المؤشر": "صافي الربح (ج.م)", "القيمة": net_profit},
                ])
                summary_report.to_excel(writer, sheet_name="ملخص_الدورة", index=False)
                if not logs_df.empty:
                    logs_df.to_excel(writer, sheet_name="التسجيل_اليومي", index=False)
                inv_summary_df.to_excel(writer, sheet_name="حالة_المخزون", index=False)
                vet_df = pd.read_sql(f"SELECT * FROM vet_logs WHERE cycle_id={selected_cycle_id}", conn)
                if not vet_df.empty:
                    vet_df.to_excel(writer, sheet_name="السجل_البيطري", index=False)

            buffer.seek(0)
            st.download_button(
                label="📥 تحميل التقرير الشامل (Excel Multi-Sheet)",
                data=buffer.getvalue(),
                file_name=f"Broiler_Manager_Report_{selected_cycle_name}.xlsx",
                mime="application/vnd.ms-excel",
            )

        with col_exp2:
            st.write("### 🖨️ 2. طباعة تقرير الدورة / حفظ كـ PDF")
            
            print_html = f"""
            <div style="direction: rtl; font-family: Arial, sans-serif; padding: 20px; border: 2px solid #0284c7; border-radius: 10px; background-color: #ffffff; color: #000000; text-align: right;">
                <h2 style="text-align: center; color: #0284c7;">🐔 تقرير أداء دورة التسمين</h2>
                <hr>
                <table style="width:100%; text-align:right; border-collapse: collapse;">
                    <tr><td><strong>اسم الدورة:</strong> {curr_cycle['name']}</td><td><strong>تاريخ البدء:</strong> {curr_cycle['start_date']}</td></tr>
                    <tr><td><strong>العدد الأولي:</strong> {tot_chicks:,} طائر</td><td><strong>الطيور الحية:</strong> {live_birds:,} طائر</td></tr>
                    <tr><td><strong>نسبة النفوق:</strong> {mortality_pct:.2f}%</td><td><strong>إجمالي العلف:</strong> {tot_feed_kg:,.1f} كجم</td></tr>
                    <tr><td><strong>FCR معدل التحويل:</strong> {fcr:.2f}</td><td><strong>EPEF معامل الكفاءة:</strong> {epef:.1f}</td></tr>
                </table>
                <hr>
                <h3 style="color: #000000; text-align: right;">💰 الملخص المالي</h3>
                <table style="width:100%; text-align:right; border: 1px solid #bae6fd; padding: 8px;">
                    <tr style="background-color: #e0f2fe;"><th style="color:#000000; padding: 6px; text-align: right;">البند</th><th style="color:#000000; padding: 6px; text-align: right;">القيمة (جنية)</th></tr>
                    <tr><td style="padding: 6px; text-align: right;">إجمالي التكاليف</td><td style="padding: 6px; text-align: right;">{total_costs:,.2f} ج.م</td></tr>
                    <tr><td style="padding: 6px; text-align: right;">إجمالي الإيرادات المتوقعة</td><td style="padding: 6px; text-align: right;">{est_revenue:,.2f} ج.م</td></tr>
                    <tr style="font-weight: bold; background-color: #bae6fd;"><td style="padding: 6px; text-align: right;">صافي الربح</td><td style="padding: 6px; text-align: right;">{net_profit:,.2f} ج.م</td></tr>
                </table>
            </div>
            """
            
            components.html(
                f"""
                {print_html}
                <div style="margin-top: 20px;">
                    <button onclick="window.print()" style="background-color: #0284c7; color: white; padding: 12px 24px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%; font-family: Arial, sans-serif; font-weight: bold;">
                        🖨️ اضغط هنا لطباعة التقرير / حفظ PDF
                    </button>
                </div>
                """,
                height=500,
                scrolling=True
            )

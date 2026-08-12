import datetime
import io
import sqlite3
import hashlib

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# 1. إعداد الصفحة (الشريط الجانبي يبدأ مفتوحاً hidden)
# =========================================================

st.set_page_config(
    page_title="Broiler Farm Manager V11 - Dynamic Sidebar",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="hidden", # يظهر الشريط الجانبي تلقائياً عند بدء التشغيل
)


# =========================================================
# 2. التصميم الاحترافي (تثبيت الشريط الجانبي من اليمين تماماً)
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
       SIDEBAR — RIGHT OVERLAY PANEL
       ===================================================== */

    [data-testid="stSidebar"] {
        direction: rtl !important;
        position: right !important;
        top: 0 !important;
        right: 0 !important;
        left: 0 !important;
        bottom: 0 !important;
        width: 350px !important;
        min-width: 350px !important;
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
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        margin-right: 0 !important;
        margin-left: 0 !important;
        width: 100% !important;
    }


    /* =====================================================
       SIDEBAR CONTENT & BUTTONS
       ===================================================== */

    [data-testid="stSidebarContent"] {
        direction: rtl !important;
        padding: 1.5rem 1rem 2rem 1rem !important;
    }

    [data-testid="stSidebar"] * {
        direction: rtl !important;
        text-align: right !important;
        color: #f8fafc !important;
    }

    /* زر إظهار/إخفاء الشريط الجانبي في أعلى اليمين */
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important;
        top: 12px !important;
        right: 12px !important;
        width: 48px !important;
        height: 48px !important;
        z-index: 1000000 !important;
        background:
            linear-gradient(
                135deg,
                #0284c7,
                #0369a1
            ) !important;
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

    [data-testid="stSidebarCollapsedControl"] svg {
        width: 27px !important;
        height: 27px !important;
        color: white !important;
    }


    /* =====================================================
       TITLES & HEADINGS
       ===================================================== */

    h1, h2, h3 {
        direction: rtl !important;
        text-align: right !important;
        color: #e0f2fe !important;
        font-weight: 900 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #bae6fd !important;
        font-weight: 900 !important;
    }


    /* =====================================================
       METRICS & FORMS
       ===================================================== */

    [data-testid="stMetric"] {
        background: #ffffff !important;
        padding: 18px !important;
        border-radius: 14px !important;
        border: 2px solid #38bdf8 !important;
        border-right: 8px solid #0284c7 !important;
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.25) !important;
    }

    [data-testid="stMetric"] * {
        color: #000000 !important;
        text-align: right !important;
    }

    [data-testid="stMetricValue"] {
        color: #0369a1 !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.96) !important;
        padding: 20px !important;
        border-radius: 14px !important;
        border: 2px solid #38bdf8 !important;
        border-right: 8px solid #0284c7 !important;
        box-shadow: 0 5px 18px rgba(0,0,0,0.25) !important;
    }

    div[data-testid="stForm"] * {
        color: #000000 !important;
        text-align: right !important;
    }


    /* =====================================================
       INPUTS & CONTROLS
       ===================================================== */

    input, textarea, select {
        direction: rtl !important;
        text-align: right !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #0284c7 !important;
        border-radius: 7px !important;
        font-weight: 700 !important;
    }

    [data-baseweb="select"] {
        direction: rtl !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 7px !important;
    }

    .stButton > button {
        width: 100% !important;
        background:
            linear-gradient(
                135deg,
                #0284c7,
                #0369a1
            ) !important;
        color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 9px !important;
        font-weight: 900 !important;
        min-height: 45px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background:
            linear-gradient(
                135deg,
                #0369a1,
                #075985
            ) !important;
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.25) !important;
    }


    /* =====================================================
       TABS & DATAFRAMES
       ===================================================== */

    .stTabs [data-baseweb="tab-list"] {
        gap: 7px;
        direction: rtl !important;
        background: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: #0f172a !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 9px 9px 0 0 !important;
        padding: 10px 16px !important;
        color: #e0f2fe !important;
        font-weight: 800 !important;
    }

    .stTabs [aria-selected="true"] {
        background: #0284c7 !important;
        color: #ffffff !important;
    }

    [data-testid="stDataFrame"] {
        background: #ffffff !important;
        border-radius: 12px !important;
        border: 2px solid #38bdf8 !important;
        direction: rtl !important;
    }


    /* =====================================================
       RESPONSIVE & PRINT
       ===================================================== */

    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            width: 86vw !important;
            min-width: 86vw !important;
        }
    }

    @media print {
        header,
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        .stTabs [role="tablist"],
        button {
            display: none !important;
        }
        .stApp {
            background: white !important;
            color: black !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. المعايير القياسية
# =========================================================

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


# =========================================================
# 4. DATABASE
# =========================================================

DB_NAME = "farm_manager_v11.db"


def get_connection():
    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
    )

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute(
            """
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
            """,
            ("admin", hash_password("admin123"), "مدير")
        )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            chicks_count INTEGER,
            chick_price REAL,
            feed_price_ton REAL,
            sell_price_kg REAL,
            target_weight REAL,
            start_date TEXT,
            status TEXT DEFAULT 'نشطة'
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cycle_id INTEGER,
            day INTEGER,
            feed_kg REAL,
            water_l REAL,
            mortality INTEGER,
            weight_g REAL,
            temp REAL,
            humidity REAL,
            ammonia REAL,
            notes TEXT,
            UNIQUE(cycle_id, day)
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            qty_added REAL,
            min_limit REAL
        )
        """
    )

    c.execute("SELECT COUNT(*) FROM inventory_purchases")
    if c.fetchone()[0] == 0:
        c.executemany(
            """
            INSERT INTO inventory_purchases (item_name, qty_added, min_limit)
            VALUES (?, ?, ?)
            """,
            [
                ("علف بادئ (كجم)", 2000, 500),
                ("علف نامي (كجم)", 3000, 700),
                ("علف ناهي (كجم)", 2500, 600),
                ("مطهر (لتر)", 20, 5),
            ]
        )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS vet_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cycle_id INTEGER,
            date TEXT,
            age INTEGER,
            symptoms TEXT,
            diagnosis TEXT,
            treatment TEXT,
            withdrawal_days INTEGER
        )
        """
    )

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

if "just_logged_in" not in st.session_state:
    st.session_state.just_logged_in = False


# =========================================================
# 6. LOGIN
# =========================================================

if not st.session_state.logged_in:
    st.markdown(
        """
        <div style="max-width:600px; margin:80px auto 20px auto; text-align:center;">
            <div style="font-size:70px; margin-bottom:10px;">🐔</div>
            <h1 style="text-align:center !important; color:#e0f2fe !important;">BFM</h1>
            <p style="text-align:center !important; font-size:20px; font-weight:700;">
                نظام إدارة مزارع التسمين
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        st.subheader("🔐 تسجيل الدخول")
        u_input = st.text_input("اسم المستخدم")
        p_input = st.text_input("الرقم السري", type="password")
        submit_login = st.form_submit_button("دخول للنظام")

        if submit_login:
            user_row = pd.read_sql_query(
                """
                SELECT * FROM users
                WHERE username = ? AND password = ?
                """,
                conn,
                params=(u_input.strip(), hash_password(p_input))
            )

            if not user_row.empty:
                st.session_state.logged_in = True
                st.session_state.username = user_row.iloc[0]["username"]
                st.session_state.role = user_row.iloc[0]["role"]
                st.session_state.just_logged_in = True  # لتفعيل إغلاق الشريط الجانبي بعد الدخول
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو الرقم السري غير صحيح!")

    st.info("الحساب الافتراضي الأول: admin / admin123")
    st.stop()


# =========================================================
# 7. SCRIPT TO AUTO-COLLAPSE SIDEBAR AFTER LOGIN
# =========================================================

if st.session_state.just_logged_in:
    st.session_state.just_logged_in = False
    components.html(
        """
        <script>
            setTimeout(function() {
                const doc = window.parent.document;
                const headerBtns = doc.querySelectorAll('header button');
                headerBtns.forEach(b => {
                    const label = b.getAttribute('aria-label') || '';
                    if (label.toLowerCase().includes('sidebar') || label.includes('القائمة')) {
                        b.click();
                    }
                });
            }, 300);
        </script>
        """,
        height=0
    )


# =========================================================
# 8. SIDEBAR (التحكم من اليمين)
# =========================================================

st.sidebar.markdown(
    """
    <div style="text-align:center; padding:10px; border-bottom:1px solid #38bdf8; margin-bottom:15px;">
        <div style="font-size:45px;">🐔</div>
        <div style="font-size:22px; font-weight:900; color:#bae6fd;">BFM Manager</div>
        <div style="font-size:12px; color:#94a3b8;">Broiler Farm Management</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title(f"👤 {st.session_state.username}")
st.sidebar.markdown(
    f"""
    <div style="background:#172554; padding:10px; border-radius:10px; border:1px solid #38bdf8; margin-bottom:15px;">
        <strong>الصلاحية:</strong> {st.session_state.role}
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("🚪 تسجيل الخروج", key="logout_button"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

st.sidebar.markdown("---")

# =========================================================
# 9. إدارة المستخدمين
# =========================================================

if st.session_state.role == "مدير":
    with st.sidebar.expander("👥 إدارة المستخدمين", expanded=False):
        with st.form("add_user_form"):
            new_user = st.text_input("اسم المستخدم الجديد")
            new_pass = st.text_input("الرقم السري", type="password")
            new_role = st.selectbox("الصلاحية", ["مستخدم عادي", "مدير"])

            if st.form_submit_button("إضافة المستخدم"):
                if new_user and new_pass:
                    try:
                        c = conn.cursor()
                        c.execute(
                            """
                            INSERT INTO users (username, password, role)
                            VALUES (?, ?, ?)
                            """,
                            (new_user.strip(), hash_password(new_pass), new_role)
                        )
                        conn.commit()
                        st.success(f"تم إضافة المستخدم {new_user}")
                    except sqlite3.IntegrityError:
                        st.error("اسم المستخدم موجود مسبقاً!")
                else:
                    st.warning("يرجى إدخال اسم المستخدم والرقم السري.")


# =========================================================
# 10. إضافة دورة
# =========================================================

with st.sidebar.expander("➕ إضافة دورة تسمين جديدة", expanded=False):
    with st.form("add_new_cycle_form"):
        c_name = st.text_input("اسم الدورة الجديدة", f"دورة {datetime.date.today()}")
        c_chicks = st.number_input("عدد الكتاكيت الأولي", min_value=1, value=2000, step=100)
        c_chick_p = st.number_input("سعر الكتكوت (جنية)", min_value=0.0, value=35.0)
        c_feed_p = st.number_input("سعر طن العلف (جنية)", min_value=0.0, value=24000.0)
        c_sell_p = st.number_input("سعر بيع الكيلو (جنية)", min_value=0.0, value=85.0)
        c_target_w = st.number_input("الوزن المستهدف (كجم)", min_value=0.1, value=2.2)

        if st.form_submit_button("💾 حفظ وتفعيل الدورة"):
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO cycles (
                    name, chicks_count, chick_price, feed_price_ton,
                    sell_price_kg, target_weight, start_date, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'نشطة')
                """,
                (
                    c_name, c_chicks, c_chick_p, c_feed_p,
                    c_sell_p, c_target_w, str(datetime.date.today())
                )
            )
            conn.commit()
            st.success("تم إضافة الدورة بنجاح!")
            st.rerun()


# =========================================================
# 11. اختيار الدورة
# =========================================================

st.sidebar.markdown("---")
st.sidebar.subheader("🔄 الدورة النشطة")

cycles_df = pd.read_sql_query(
    """
    SELECT * FROM cycles
    WHERE status = 'نشطة'
    ORDER BY id DESC
    """,
    conn
)

selected_cycle_id = None
curr_cycle = None

if cycles_df.empty:
    st.sidebar.warning("⚠️ لا توجد دورة نشطة حالياً.")
else:
    cycle_dict = dict(zip(cycles_df["name"], cycles_df["id"]))
    selected_cycle_name = st.sidebar.selectbox("اختر الدورة", list(cycle_dict.keys()))
    selected_cycle_id = cycle_dict[selected_cycle_name]
    curr_cycle = cycles_df[cycles_df["id"] == selected_cycle_id].iloc[0]

    st.sidebar.markdown(
        f"""
        <div style="background:#0f172a; padding:12px; border-radius:10px; border:1px solid #38bdf8; line-height:2;">
            🗓️ <strong>البداية:</strong> {curr_cycle['start_date']}<br>
            🐤 <strong>العدد:</strong> {int(curr_cycle['chicks_count']):,}<br>
            🎯 <strong>الهدف:</strong> {float(curr_cycle['target_weight']):.2f} كجم
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar.expander("⚙️ تعديل أسعار الدورة"):
        with st.form("edit_cycle_form"):
            e_chick_p = st.number_input("سعر الكتكوت", value=float(curr_cycle["chick_price"]))
            e_feed_p = st.number_input("سعر طن العلف", value=float(curr_cycle["feed_price_ton"]))
            e_sell_p = st.number_input("سعر البيع / كجم", value=float(curr_cycle["sell_price_kg"]))

            if st.form_submit_button("💾 حفظ التحديثات"):
                c = conn.cursor()
                c.execute(
                    """
                    UPDATE cycles
                    SET chick_price = ?, feed_price_ton = ?, sell_price_kg = ?
                    WHERE id = ?
                    """,
                    (e_chick_p, e_feed_p, e_sell_p, selected_cycle_id)
                )
                conn.commit()
                st.success("تم تحديث الأسعار.")
                st.rerun()


# =========================================================
# 12. MAIN APPLICATION
# =========================================================

st.title("🐔 BFM — نظام إدارة مزارع التسمين")
st.caption("Broiler Farm Manager • V11 Professional")

if selected_cycle_id is None:
    st.warning("⚠️ أضف دورة تسمين من القائمة الجانبية (أعلى اليمين) لبدء العمل.")
    st.stop()


# =========================================================
# 13. LOAD DAILY DATA
# =========================================================

logs_df = pd.read_sql_query(
    """
    SELECT * FROM daily_logs
    WHERE cycle_id = ?
    ORDER BY day ASC
    """,
    conn,
    params=(selected_cycle_id,)
)


# =========================================================
# 14. CORE CALCULATIONS
# =========================================================

tot_chicks = int(curr_cycle["chicks_count"])
tot_mortality = int(logs_df["mortality"].sum()) if not logs_df.empty else 0
live_birds = max(tot_chicks - tot_mortality, 0)
mortality_pct = (tot_mortality / tot_chicks * 100) if tot_chicks > 0 else 0
liveability = max(100 - mortality_pct, 0)

tot_feed_kg = float(logs_df["feed_kg"].sum()) if not logs_df.empty else 0
tot_water_l = float(logs_df["water_l"].sum()) if not logs_df.empty else 0
last_day = int(logs_df["day"].max()) if not logs_df.empty else 1

valid_weights = logs_df[logs_df["weight_g"] > 0] if not logs_df.empty else pd.DataFrame()
last_weight_g = float(valid_weights.iloc[-1]["weight_g"]) if not valid_weights.empty else 45

tot_weight_kg = (live_birds * last_weight_g) / 1000
fcr = (tot_feed_kg / tot_weight_kg) if tot_weight_kg > 0 else 0
epef = (((liveability * (last_weight_g / 1000)) / (last_day * fcr)) * 100) if fcr > 0 and last_day > 0 else 0


# =========================================================
# 15. TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "📊 لوحة التحكم",
        "📝 التسجيل اليومي",
        "📈 المعايير",
        "📦 المخزون",
        "💉 السجل البيطري",
        "💰 التحليل المالي",
        "🖨️ التقارير",
    ]
)


# =========================================================
# TAB 1 — DASHBOARD
# =========================================================

with tab1:
    st.subheader(f"📌 أداء الدورة: {curr_cycle['name']}")
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("🐔 الطيور الحية", f"{live_birds:,}")
    c2.metric("☠️ النفوق", f"{mortality_pct:.2f}%")
    c3.metric("🌾 العلف", f"{tot_feed_kg:,.1f} كجم")
    c4.metric("📊 FCR", f"{fcr:.2f}")
    c5.metric("🏆 EPEF", f"{epef:.1f}")

    if mortality_pct > 5:
        st.error("🚨 تنبيه: نسبة النفوق تجاوزت 5%.")
    if fcr > 1.8:
        st.warning("⚠️ تنبيه: FCR أعلى من 1.80.")

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.subheader("🌡️ البيئة اليومية")
        if not logs_df.empty:
            fig_env = go.Figure()
            fig_env.add_trace(go.Scatter(x=logs_df["day"], y=logs_df["temp"], name="الحرارة °C", line=dict(color="#ef4444", width=3)))
            fig_env.add_trace(go.Scatter(x=logs_df["day"], y=logs_df["humidity"], name="الرطوبة %", line=dict(color="#0284c7", width=3)))
            fig_env.update_layout(xaxis_title="اليوم", yaxis_title="القيمة", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.95)", margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_env, use_container_width=True)
        else:
            st.info("لا توجد بيانات بيئية بعد.")

    with right:
        st.subheader("🌾 استهلاك العلف والمياه")
        if not logs_df.empty:
            fig_cons = go.Figure()
            fig_cons.add_trace(go.Bar(x=logs_df["day"], y=logs_df["feed_kg"], name="العلف"))
            fig_cons.add_trace(go.Bar(x=logs_df["day"], y=logs_df["water_l"], name="المياه"))
            fig_cons.update_layout(barmode="group", xaxis_title="اليوم", yaxis_title="الكمية", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.95)")
            st.plotly_chart(fig_cons, use_container_width=True)
        else:
            st.info("لا توجد بيانات استهلاك بعد.")


# =========================================================
# TAB 2 — DAILY LOG
# =========================================================

with tab2:
    st.subheader("📝 التسجيل اليومي")
    next_day_val = min(last_day + 1, 40) if not logs_df.empty else 1

    with st.form("daily_entry_form"):
        c1, c2, c3, c4, c5 = st.columns(5)
        in_day = c1.number_input("اليوم", min_value=1, max_value=40, value=next_day_val)
        in_feed = c2.number_input("العلف كجم", min_value=0.0, step=10.0)
        in_water = c3.number_input("المياه لتر", min_value=0.0, step=10.0)
        in_mort = c4.number_input("النفوق", min_value=0, step=1)
        in_weight = c5.number_input("الوزن جم", min_value=0.0, step=10.0)

        c6, c7, c8, c9 = st.columns(4)
        in_temp = c6.number_input("الحرارة °C", value=30.0)
        in_hum = c7.number_input("الرطوبة %", value=60.0)
        in_amm = c8.number_input("الأمونيا PPM", value=10.0)
        in_notes = c9.text_input("ملاحظات")

        if st.form_submit_button("💾 حفظ بيانات اليوم"):
            if in_mort > tot_chicks:
                st.error("عدد النافق لا يمكن أن يتجاوز العدد الأولي.")
            else:
                c = conn.cursor()
                c.execute(
                    """
                    INSERT OR REPLACE INTO daily_logs (
                        cycle_id, day, feed_kg, water_l, mortality,
                        weight_g, temp, humidity, ammonia, notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        selected_cycle_id, in_day, in_feed, in_water, in_mort,
                        in_weight, in_temp, in_hum, in_amm, in_notes
                    )
                )
                conn.commit()
                st.success(f"تم حفظ بيانات اليوم {in_day}.")
                st.rerun()

    st.markdown("---")
    if not logs_df.empty:
        calc_df = logs_df.copy()
        calc_df["feed_cum"] = calc_df["feed_kg"].cumsum()
        calc_df["mort_cum"] = calc_df["mortality"].cumsum()
        calc_df["live_birds_day"] = tot_chicks - calc_df["mort_cum"]
        calc_df["biomass_day_kg"] = (calc_df["live_birds_day"] * calc_df["weight_g"]) / 1000
        calc_df["fcr_cum"] = calc_df["feed_cum"] / calc_df["biomass_day_kg"].replace(0, pd.NA)

        display_cols = [
            "day", "feed_kg", "water_l", "mortality", "weight_g",
            "biomass_day_kg", "fcr_cum", "temp", "humidity", "ammonia", "notes"
        ]
        renamed_cols = {
            "day": "اليوم", "feed_kg": "العلف كجم", "water_l": "المياه لتر",
            "mortality": "النفوق", "weight_g": "الوزن جم", "biomass_day_kg": "الكتلة الحية كجم",
            "fcr_cum": "FCR تراكمي", "temp": "الحرارة", "humidity": "الرطوبة",
            "ammonia": "الأمونيا", "notes": "ملاحظات"
        }
        st.dataframe(calc_df[display_cols].rename(columns=renamed_cols), use_container_width=True)
    else:
        st.info("لم يتم تسجيل بيانات يومية بعد.")


# =========================================================
# TAB 3 — BENCHMARK
# =========================================================

with tab3:
    st.subheader("📈 مقارنة النمو بالمعايير")
    merged_df = pd.merge(
        STANDARD_BENCHMARKS,
        logs_df[["day", "weight_g"]] if not logs_df.empty else pd.DataFrame(columns=["day", "weight_g"]),
        on="day",
        how="left"
    )

    fig_w = go.Figure()
    fig_w.add_trace(go.Scatter(x=merged_df["day"], y=merged_df["std_weight"], name="القياسي", line=dict(color="#64748b", dash="dash", width=2)))
    fig_w.add_trace(go.Scatter(x=merged_df["day"], y=merged_df["weight_g"], name="الفعلي", line=dict(color="#0284c7", width=4)))
    fig_w.update_layout(title="منحنى النمو", xaxis_title="اليوم", yaxis_title="الوزن جم", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.95)")
    st.plotly_chart(fig_w, use_container_width=True)


# =========================================================
# TAB 4 — INVENTORY
# =========================================================

with tab4:
    st.subheader("📦 إدارة المخزون")
    starter_used = logs_df[logs_df["day"] <= 10]["feed_kg"].sum() if not logs_df.empty else 0
    grower_used = logs_df[(logs_df["day"] > 10) & (logs_df["day"] <= 25)]["feed_kg"].sum() if not logs_df.empty else 0
    finisher_used = logs_df[logs_df["day"] > 25]["feed_kg"].sum() if not logs_df.empty else 0

    purchases_df = pd.read_sql_query(
        """
        SELECT item_name, SUM(qty_added) AS total_added, MAX(min_limit) AS min_limit
        FROM inventory_purchases
        GROUP BY item_name
        """,
        conn
    )

    inventory_status = []
    for _, row in purchases_df.iterrows():
        item = row["item_name"]
        added = float(row["total_added"])
        limit = float(row["min_limit"])

        if "بادئ" in item:
            used = starter_used
        elif "نامي" in item:
            used = grower_used
        elif "ناهي" in item:
            used = finisher_used
        else:
            used = 0

        available = added - used
        status = "⚠️ إعادة طلب" if available < limit else "✅ متوفر"

        inventory_status.append({
            "الصنف": item,
            "إجمالي المشتريات": added,
            "المستهلك": used,
            "الرصيد": available,
            "حد الأمان": limit,
            "الحالة": status,
        })

    inv_summary_df = pd.DataFrame(inventory_status)
    if not inv_summary_df.empty:
        st.dataframe(inv_summary_df, use_container_width=True)
        reorder = inv_summary_df[inv_summary_df["الرصيد"] < inv_summary_df["حد الأمان"]]
        for _, r in reorder.iterrows():
            st.warning(f"⚠️ إعادة طلب: {r['الصنف']} — الرصيد {r['الرصيد']:.1f}")

        with st.expander("➕ إضافة توريد جديد"):
            with st.form("add_stock_form"):
                st_item = st.selectbox("الصنف", inv_summary_df["الصنف"].tolist())
                st_qty = st.number_input("الكمية", min_value=0.0, step=100.0)

                if st.form_submit_button("💾 حفظ التوريد"):
                    c = conn.cursor()
                    c.execute(
                        """
                        INSERT INTO inventory_purchases (item_name, qty_added, min_limit)
                        VALUES (?, ?, ?)
                        """,
                        (st_item, st_qty, 500)
                    )
                    conn.commit()
                    st.success("تم إضافة التوريد.")
                    st.rerun()


# =========================================================
# TAB 5 — VETERINARY
# =========================================================

with tab5:
    st.subheader("💉 السجل البيطري")
    with st.form("vet_entry"):
        c1, c2, c3, c4 = st.columns(4)
        v_date = c1.date_input("التاريخ", datetime.date.today())
        v_age = c2.number_input("العمر", min_value=1, value=last_day)
        v_sym = c3.text_input("الأعراض")
        v_diag = c4.text_input("التشخيص")

        c5, c6 = st.columns(2)
        v_treat = c5.text_input("العلاج / التحصينة")
        v_withdraw = c6.number_input("فترة السحب أيام", min_value=0, value=3)

        if st.form_submit_button("💾 حفظ السجل"):
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO vet_logs (
                    cycle_id, date, age, symptoms, diagnosis, treatment, withdrawal_days
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (selected_cycle_id, str(v_date), v_age, v_sym, v_diag, v_treat, v_withdraw)
            )
            conn.commit()
            st.success("تم تسجيل السجل البيطري.")
            st.rerun()

    vet_df = pd.read_sql_query(
        """
        SELECT * FROM vet_logs
        WHERE cycle_id = ?
        ORDER BY date DESC
        """,
        conn,
        params=(selected_cycle_id,)
    )

    if not vet_df.empty:
        vet_df["انتهاء السحب"] = vet_df["age"] + vet_df["withdrawal_days"]
        renamed = {
            "date": "التاريخ", "age": "العمر", "symptoms": "الأعراض",
            "diagnosis": "التشخيص", "treatment": "العلاج", "withdrawal_days": "فترة السحب"
        }
        st.dataframe(vet_df.rename(columns=renamed), use_container_width=True)


# =========================================================
# TAB 6 — FINANCIAL
# =========================================================

with tab6:
    st.subheader("💰 التحليل المالي")
    chick_cost = tot_chicks * float(curr_cycle["chick_price"])
    feed_cost = (tot_feed_kg / 1000) * float(curr_cycle["feed_price_ton"])
    total_costs = chick_cost + feed_cost
    est_revenue = tot_weight_kg * float(curr_cycle["sell_price_kg"])
    net_profit = est_revenue - total_costs
    breakeven_kg = (total_costs / float(curr_cycle["sell_price_kg"])) if float(curr_cycle["sell_price_kg"]) > 0 else 0
    cost_per_kg = (total_costs / tot_weight_kg) if tot_weight_kg > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("إجمالي التكاليف", f"{total_costs:,.2f} ج.م")
    m2.metric("الإيرادات", f"{est_revenue:,.2f} ج.م")
    m3.metric("صافي الربح", f"{net_profit:,.2f} ج.م")
    m4.metric("نقطة التعادل", f"{breakeven_kg:,.1f} كجم")

    st.info(f"تكلفة إنتاج الكيلو: **{cost_per_kg:.2f} ج.م**")
    st.markdown("---")
    st.subheader("🎛️ تحليل الحساسية")

    s1, s2, s3 = st.columns(3)
    sim_feed_price = s1.slider("سعر طن العلف", 15000, 35000, int(curr_cycle["feed_price_ton"]), 500)
    sim_sell_price = s2.slider("سعر البيع / كجم", 50, 120, int(curr_cycle["sell_price_kg"]), 1)
    sim_mortality = s3.slider("النفوق النهائي %", 1.0, 15.0, float(mortality_pct if mortality_pct > 0 else 3), 0.5)

    sim_live_birds = tot_chicks * (1 - sim_mortality / 100)
    sim_tot_weight_kg = sim_live_birds * float(curr_cycle["target_weight"])
    simulated_fcr = 1.60
    sim_feed_kg = sim_tot_weight_kg * simulated_fcr
    sim_costs = chick_cost + (sim_feed_kg / 1000) * sim_feed_price
    sim_revenue = sim_tot_weight_kg * sim_sell_price
    sim_profit = sim_revenue - sim_costs

    x1, x2, x3 = st.columns(3)
    x1.metric("التكلفة التقديرية", f"{sim_costs:,.2f} ج.م")
    x2.metric("الإيراد التقديري", f"{sim_revenue:,.2f} ج.م")
    x3.metric("الربح التقديري", f"{sim_profit:,.2f} ج.م", delta=f"{sim_profit - net_profit:,.2f}")


# =========================================================
# TAB 7 — REPORTS
# =========================================================

with tab7:
    st.subheader("🖨️ التقارير والتصدير")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### 📥 التقرير Excel")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            summary_report = pd.DataFrame(
                [
                    {"المؤشر": "اسم الدورة", "القيمة": str(curr_cycle["name"])},
                    {"المؤشر": "تاريخ البدء", "القيمة": str(curr_cycle["start_date"])},
                    {"المؤشر": "العدد الأولي", "القيمة": tot_chicks},
                    {"المؤشر": "الطيور الحية", "القيمة": live_birds},
                    {"المؤشر": "النفوق %", "القيمة": f"{mortality_pct:.2f}%"},
                    {"المؤشر": "العلف كجم", "القيمة": tot_feed_kg},
                    {"المؤشر": "FCR", "القيمة": round(fcr, 2)},
                    {"المؤشر": "EPEF", "القيمة": round(epef, 1)},
                    {"المؤشر": "التكاليف", "القيمة": total_costs},
                    {"المؤشر": "الإيرادات", "القيمة": est_revenue},
                    {"المؤشر": "صافي الربح", "القيمة": net_profit},
                ]
            )
            summary_report.to_excel(writer, sheet_name="ملخص الدورة", index=False)

            if not logs_df.empty:
                logs_df.to_excel(writer, sheet_name="التسجيل اليومي", index=False)

            inv_summary_df.to_excel(writer, sheet_name="المخزون", index=False)

            if not vet_df.empty:
                vet_df.to_excel(writer, sheet_name="السجل البيطري", index=False)

        buffer.seek(0)
        st.download_button(
            label="📥 تحميل التقرير الشامل",
            data=buffer.getvalue(),
            file_name=f"BFM_Report_{selected_cycle_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col2:
        st.write("### 🖨️ طباعة / PDF")
        print_html = f"""
        <div style="direction:rtl; font-family:Arial; background:white; color:#000; padding:25px; border:2px solid #0284c7; border-radius:12px;">
            <h2 style="text-align:center; color:#0284c7;">🐔 تقرير دورة التسمين</h2>
            <hr>
            <p><strong>الدورة:</strong> {curr_cycle['name']}</p>
            <p><strong>تاريخ البدء:</strong> {curr_cycle['start_date']}</p>
            <p><strong>العدد الأولي:</strong> {tot_chicks:,}</p>
            <p><strong>الطيور الحية:</strong> {live_birds:,}</p>
            <p><strong>النفوق:</strong> {mortality_pct:.2f}%</p>
            <p><strong>العلف:</strong> {tot_feed_kg:,.1f} كجم</p>
            <p><strong>FCR:</strong> {fcr:.2f}</p>
            <p><strong>EPEF:</strong> {epef:.1f}</p>
            <hr>
            <h3>💰 الملخص المالي</h3>
            <table style="width:100%; border-collapse:collapse;">
                <tr><td style="padding:8px;">إجمالي التكاليف</td><td style="padding:8px;">{total_costs:,.2f}</td></tr>
                <tr><td style="padding:8px;">الإيرادات</td><td style="padding:8px;">{est_revenue:,.2f}</td></tr>
                <tr style="background:#e0f2fe; font-weight:bold;"><td style="padding:8px;">صافي الربح</td><td style="padding:8px;">{net_profit:,.2f}</td></tr>
            </table>
        </div>
        """

        components.html(
            f"""
            {print_html}
            <div style="margin-top:20px;">
                <button onclick="window.print()" style="width:100%; padding:14px; background:#0284c7; color:white; border:none; border-radius:8px; font-size:17px; font-weight:bold; cursor:pointer;">
                    🖨️ طباعة التقرير / حفظ PDF
                </button>
            </div>
            """,
            height=650,
            scrolling=True
        )


# =========================================================
# 15. FOOTER
# =========================================================

st.markdown(
    """
    <hr>
    <div style="text-align:center; color:#94a3b8; padding:15px; font-size:13px;">
        🐔 BFM — Broiler Farm Manager V11<br>نظام إدارة مزارع التسمين
    </div>
    """,
    unsafe_allow_html=True
)

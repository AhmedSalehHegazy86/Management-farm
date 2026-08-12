import datetime
import io
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم العريض باللغة العربية
# ---------------------------------------------------------
st.set_page_config(
    page_title="Broiler Farm Manager V9 - Auto App",
    page_icon="🐔",
    layout="wide",
)

st.markdown(
    """
    <style>
    body, div, p, span, h1, h2, h3, h4, h5, h6, input, button { direction: rtl; text-align: right; }
    .stMetric { text-align: right; background-color: #f8f9fa; padding: 10px; border-radius: 8px; }
    </style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 2. البيانات المعيارية القياسية (40 يوماً) من الملف الأصلي
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
# 3. إدارة قاعدة البيانات
# ---------------------------------------------------------
def get_connection():
    return sqlite3.connect("farm_manager_v9.db", check_same_thread=False)


def init_db():
    conn = get_connection()
    c = conn.cursor()

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

    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE, quantity REAL, min_limit REAL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS vet_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INT, date TEXT, age INT,
        symptoms TEXT, diagnosis TEXT, treatment TEXT, withdrawal_days INT
    )""")

    # إدخال مخزون افتراضي إذا لم يوجد
    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO inventory (item_name, quantity, min_limit) VALUES (?, ?, ?)",
            [
                ("علف بادئ (كجم)", 2000.0, 500.0),
                ("علف نامي (كجم)", 3000.0, 700.0),
                ("علف ناهي (كجم)", 2500.0, 600.0),
                ("مطهر (لتر)", 20.0, 5.0),
            ],
        )

    conn.commit()


init_db()

# ---------------------------------------------------------
# 4. القائمة الجانبية: إدارة وتحديد الدورة
# ---------------------------------------------------------
st.sidebar.title("🐔 إدارة المزرعة V9")
conn = get_connection()
cycles_df = pd.read_sql("SELECT * FROM cycles WHERE status='نشطة'", conn)

if cycles_df.empty:
    st.sidebar.warning("⚠️ لا توجد دورة نشطة. أنشئ دورة جديدة لبدء العمل.")
    with st.sidebar.form("add_first_cycle"):
        st.write("### ➕ إضافة دورة جديدة")
        c_name = st.text_input("اسم الدورة", "دورة يناير 2026")
        c_chicks = st.number_input("عدد الكتاكيت", value=2000, step=100)
        c_chick_p = st.number_input("سعر الكتكوت (جنية)", value=35.0)
        c_feed_p = st.number_input("سعر طن العلف (جنية)", value=24000.0)
        c_sell_p = st.number_input("سعر بيع الكيلو (جنية)", value=85.0)
        c_target_w = st.number_input("الوزن المستهدف (كجم)", value=2.2)
        if st.form_submit_button("إحداث الدورة"):
            c = conn.cursor()
            c.execute(
                """INSERT INTO cycles (name, chicks_count, chick_price, feed_price_ton, sell_price_kg, target_weight, start_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    c_name,
                    c_chicks,
                    c_chick_p,
                    c_feed_p,
                    c_sell_p,
                    c_target_w,
                    str(datetime.date.today()),
                ),
            )
            conn.commit()
            st.rerun()
    selected_cycle_id = None
else:
    cycle_dict = dict(zip(cycles_df["name"], cycles_df["id"]))
    selected_cycle_name = st.sidebar.selectbox(
        "اختر الدورة الحالية", list(cycle_dict.keys())
    )
    selected_cycle_id = cycle_dict[selected_cycle_name]
    curr_cycle = cycles_df[cycles_df["id"] == selected_cycle_id].iloc[0]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**تاريخ البدء:** {curr_cycle['start_date']}")
    st.sidebar.markdown(f"**عدد الطيور:** {curr_cycle['chicks_count']:,} طائر")

    with st.sidebar.expander("⚙️ تعديل إعدادات الدورة"):
        with st.form("edit_cycle_form"):
            e_chick_p = st.number_input(
                "سعر الكتكوت", value=float(curr_cycle["chick_price"])
            )
            e_feed_p = st.number_input(
                "سعر طن العلف", value=float(curr_cycle["feed_price_ton"])
            )
            e_sell_p = st.number_input(
                "سعر البيع/كجم", value=float(curr_cycle["sell_price_kg"])
            )
            if st.form_submit_button("حفظ التحديثات"):
                c = conn.cursor()
                c.execute(
                    "UPDATE cycles SET chick_price=?, feed_price_ton=?, sell_price_kg=? WHERE id=?",
                    (e_chick_p, e_feed_p, e_sell_p, selected_cycle_id),
                )
                conn.commit()
                st.success("تم تحديث الإعدادات!")
                st.rerun()

# ---------------------------------------------------------
# 5. الواجهة الرئيسية للبرنامج
# ---------------------------------------------------------
st.title("🐔 Broiler Farm Manager V9 - النظام الأوتوماتيكي")

if selected_cycle_id:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "📊 لوحة التحكم والأداء",
            "📝 التسجيل اليومي",
            "📈 المقارنة بالمعايير القياسية",
            "📦 إدارة المخزون",
            "💉 السجل البيطري",
            "💰 التحليل المالي وحساسية الأرباح",
        ]
    )

    logs_df = pd.read_sql(
        f"SELECT * FROM daily_logs WHERE cycle_id={selected_cycle_id} ORDER BY day ASC",
        conn,
    )

    # --- الحسابات الأساسية ---
    tot_chicks = curr_cycle["chicks_count"]
    tot_mortality = logs_df["mortality"].sum() if not logs_df.empty else 0
    live_birds = tot_chicks - tot_mortality
    mortality_pct = (tot_mortality / tot_chicks) * 100 if tot_chicks > 0 else 0.0

    tot_feed_kg = logs_df["feed_kg"].sum() if not logs_df.empty else 0.0
    tot_water_l = logs_df["water_l"].sum() if not logs_df.empty else 0.0

    last_weight_g = (
        logs_df[logs_df["weight_g"] > 0]["weight_g"].iloc[-1]
        if not logs_df[logs_df["weight_g"] > 0].empty
        else 45.0
    )
    tot_weight_kg = (live_birds * last_weight_g) / 1000.0

    fcr = (tot_feed_kg / tot_weight_kg) if tot_weight_kg > 0 else 0.0
    last_day = logs_df["day"].max() if not logs_df.empty else 1
    liveability = 100.0 - mortality_pct
    epef = (
        ((liveability * (last_weight_g / 1000.0)) / (last_day * fcr)) * 100
        if (fcr > 0 and last_day > 0)
        else 0.0
    )

    # --- Tab 1: لوحة التحكم ---
    with tab1:
        st.subheader("📌 ملخص المؤشرات الحالية")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("الطيور الحية", f"{live_birds:,} طائر")
        c2.metric("نسبة النفوق الإجمالية", f"{mortality_pct:.2f}%")
        c3.metric("إجمالي العلف المستهلك", f"{tot_feed_kg:,.1f} كجم")
        c4.metric("معدل التحويل (FCR)", f"{fcr:.2f}")
        c5.metric("معامل الكفاءة (EPEF)", f"{epef:.1f}")

        st.markdown("---")
        if mortality_pct > 5.0:
            st.error("🚨 تنبيه: نسبة النفوق عالية وتجاوزت الحد المسموح (5%)!")
        if fcr > 1.8 and fcr > 0:
            st.warning("⚠️ تنبيه: معدل التحويل الغذائي (FCR) أعلى من 1.8!")

        col_left, col_right = st.columns(2)
        with col_left:
            st.write("### 🌡️ متابعة درجة الحرارة والرطوبة اليومية")
            if not logs_df.empty:
                fig_env = go.Figure()
                fig_env.add_trace(
                    go.Scatter(
                        x=logs_df["day"],
                        y=logs_df["temp"],
                        name="الحرارة (°C)",
                        line=dict(color="red"),
                    )
                )
                fig_env.add_trace(
                    go.Scatter(
                        x=logs_df["day"],
                        y=logs_df["humidity"],
                        name="الرطوبة (%)",
                        line=dict(color="blue"),
                    )
                )
                fig_env.update_layout(
                    xaxis_title="اليوم", yaxis_title="القيمة", margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig_env, use_container_width=True)

        with col_right:
            st.write("### 💧 استهلاك العلف والمياه اليومي")
            if not logs_df.empty:
                fig_cons = go.Figure()
                fig_cons.add_trace(
                    go.Bar(
                        x=logs_df["day"],
                        y=logs_df["feed_kg"],
                        name="العلف (كجم)",
                        marker_color="orange",
                    )
                )
                fig_cons.add_trace(
                    go.Bar(
                        x=logs_df["day"],
                        y=logs_df["water_l"],
                        name="المياه (لتر)",
                        marker_color="cyan",
                    )
                )
                fig_cons.update_layout(
                    barmode="group",
                    xaxis_title="اليوم",
                    yaxis_title="الكمية",
                    margin=dict(l=20, r=20, t=30, b=20),
                )
                st.plotly_chart(fig_cons, use_container_width=True)

    # --- Tab 2: التسجيل اليومي ---
    with tab2:
        st.subheader("📝 إدخال / تحديث البيانات اليومية")

        with st.form("daily_entry_form"):
            col1, col2, col3, col4, col5 = st.columns(5)
            next_day_val = int(last_day if logs_df.empty else min(last_day + 1, 40))
            in_day = col1.number_input(
                "اليوم", min_value=1, max_value=40, value=next_day_val
            )
            in_feed = col2.number_input(
                "استهلاك العلف (كجم)", min_value=0.0, step=10.0
            )
            in_water = col3.number_input(
                "استهلاك المياه (لتر)", min_value=0.0, step=10.0
            )
            in_mort = col4.number_input("النفوق اليومي", min_value=0, step=1)
            in_weight = col5.number_input(
                "متوسط الوزن (جم)", min_value=0.0, step=10.0
            )

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
                    (
                        selected_cycle_id,
                        in_day,
                        in_feed,
                        in_water,
                        in_mort,
                        in_weight,
                        in_temp,
                        in_hum,
                        in_amm,
                        in_notes,
                    ),
                )

                # خصم العلف تلقائياً من نوع العلف المناسب للعمر
                feed_type = (
                    "علف بادئ (كجم)"
                    if in_day <= 10
                    else (
                        "علف نامي (كجم)" if in_day <= 25 else "علف ناهي (كجم)"
                    )
                )
                c.execute(
                    "UPDATE inventory SET quantity = quantity - ? WHERE item_name = ?",
                    (in_feed, feed_type),
                )

                conn.commit()
                st.success(f"تم حفظ بيانات اليوم {in_day} وتحديث المخزون بنجاح!")
                st.rerun()

        st.markdown("---")
        st.write("### 📋 جدول التسجيلات المسجلة بالدورة")
        st.dataframe(logs_df, use_container_width=True)

        # زر تصدير السجل إلى Excel
        if not logs_df.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                logs_df.to_excel(
                    writer, sheet_name="التسجيل_اليومي", index=False
                )
            st.download_button(
                label="📥 تحميل السجل اليومي كملف Excel",
                data=buffer.getvalue(),
                file_name=f"Daily_Log_{selected_cycle_name}.xlsx",
                mime="application/vnd.ms-excel",
            )

    # --- Tab 3: المقارنة بالمعايير القياسية ---
    with tab3:
        st.subheader("📈 مقارنة الأداء بالجدول القياسي")

        merged_df = pd.merge(
            STANDARD_BENCHMARKS,
            logs_df[["day", "weight_g", "feed_kg"]],
            on="day",
            how="left",
        )

        # رسم منحنى الوزن الفعلي والقياسي
        fig_w = go.Figure()
        fig_w.add_trace(
            go.Scatter(
                x=merged_df["day"],
                y=merged_df["std_weight"],
                name="الوزن القياسي (جم)",
                line=dict(color="gray", dash="dash"),
            )
        )
        fig_w.add_trace(
            go.Scatter(
                x=merged_df["day"],
                y=merged_df["weight_g"],
                name="الوزن الفعلي (جم)",
                line=dict(color="green", width=3),
            )
        )
        fig_w.update_layout(
            title="مقارنة الوزن الفعلي بالوزن القياسي",
            xaxis_title="اليوم",
            yaxis_title="الوزن (جم)",
        )
        st.plotly_chart(fig_w, use_container_width=True)

    # --- Tab 4: إدارة المخزون ---
    with tab4:
        st.subheader("📦 رصيد المخزون وحالة التوريد")
        inv_df = pd.read_sql("SELECT * FROM inventory", conn)

        # إشعار بإعادة الطلب
        reorder_items = inv_df[inv_df["quantity"] < inv_df["min_limit"]]
        if not reorder_items.empty:
            for _, item in reorder_items.iterrows():
                st.warning(
                    f"⚠️ تنبيه إعادة طلب: رصيد ({item['item_name']}) انخفض إلى {item['quantity']:.1f} (الحد الأدنى: {item['min_limit']})"
                )

        st.dataframe(inv_df, use_container_width=True)

        with st.expander("➕ إضافة أو توريد شحنة جديدة للمخزون"):
            with st.form("add_stock_form"):
                st_item = st.selectbox(
                    "اسم الصنف", inv_df["item_name"].tolist()
                )
                st_qty = st.number_input(
                    "الكمية المضافة", min_value=0.0, step=100.0
                )
                if st.form_submit_button("إضافة للمخزون"):
                    c = conn.cursor()
                    c.execute(
                        "UPDATE inventory SET quantity = quantity + ? WHERE item_name = ?",
                        (st_qty, st_item),
                    )
                    conn.commit()
                    st.success("تم تحديث المخزون بنجاح!")
                    st.rerun()

    # --- Tab 5: السجل البيطري ---
    with tab5:
        st.subheader("💉 السجل البيطري والتحصينات")
        with st.form("vet_entry"):
            c1, c2, c3, c4 = st.columns(4)
            v_date = c1.date_input("التاريخ", datetime.date.today())
            v_age = c2.number_input(
                "العمر (أيام)", min_value=1, value=int(last_day)
            )
            v_sym = c3.text_input("الأعراض / الملاحظات")
            v_diag = c4.text_input("التشخيص البيطري")

            c5, c6 = st.columns(2)
            v_treat = c5.text_input("العلاج / التحصينة")
            v_withdraw = c6.number_input(
                "فترة سحب الدواء (أيام)", min_value=0, value=3
            )

            if st.form_submit_button("💾 حفظ السجل البيطري"):
                c = conn.cursor()
                c.execute(
                    """INSERT INTO vet_logs (cycle_id, date, age, symptoms, diagnosis, treatment, withdrawal_days)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        selected_cycle_id,
                        str(v_date),
                        v_age,
                        v_sym,
                        v_diag,
                        v_treat,
                        v_withdraw,
                    ),
                )
                conn.commit()
                st.success("تم تسجيل العلاج بنجاح!")
                st.rerun()

        vet_df = pd.read_sql(
            f"SELECT * FROM vet_logs WHERE cycle_id={selected_cycle_id}", conn
        )
        st.dataframe(vet_df, use_container_width=True)

    # --- Tab 6: التحليل المالي وحساسية الأرباح ---
    with tab6:
        st.subheader("💰 التحليل المالي ونقطة التعادل")

        chick_cost = tot_chicks * curr_cycle["chick_price"]
        feed_cost = (tot_feed_kg / 1000.0) * curr_cycle["feed_price_ton"]
        total_costs = chick_cost + feed_cost

        est_revenue = tot_weight_kg * curr_cycle["sell_price_kg"]
        net_profit = est_revenue - total_costs
        breakeven_kg = (
            total_costs / curr_cycle["sell_price_kg"]
            if curr_cycle["sell_price_kg"] > 0
            else 0.0
        )
        cost_per_chick = total_costs / tot_chicks if tot_chicks > 0 else 0.0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("إجمالي التكاليف", f"{total_costs:,.2f} ج.م")
        m2.metric("إجمالي الإيرادات المتوقعة", f"{est_revenue:,.2f} ج.م")
        m3.metric("صافي الربح المتوقع", f"{net_profit:,.2f} ج.م")
        m4.metric("نقطة التعادل (كجم)", f"{breakeven_kg:,.1f} كجم")

        st.info(
            f"💡 **تكلفة الكتكوت الإجمالية (كتكوت + علف مأكول):** {cost_per_chick:.2f} جنية"
        )

        st.markdown("---")
        st.subheader("🎛️ تحليل الحساسية للربحية (Sensitivity Analysis)")
        st.write(
            "جرب تعديل المتغيرات أدناه لرؤية تأثيرها المباشر على الأرباح ونقطة التعادل:"
        )

        col_s1, col_s2, col_s3 = st.columns(3)
        sim_feed_price = col_s1.slider(
            "سعر طن العلف (جنية)",
            min_value=15000,
            max_value=35000,
            value=int(curr_cycle["feed_price_ton"]),
            step=500,
        )
        sim_sell_price = col_s2.slider(
            "سعر بيع الكيلو (جنية)",
            min_value=50,
            max_value=120,
            value=int(curr_cycle["sell_price_kg"]),
            step=1,
        )
        sim_mortality = col_s3.slider(
            "نسبة النفوق المتوقعة (%)",
            min_value=1.0,
            max_value=15.0,
            value=float(mortality_pct if mortality_pct > 0 else 3.0),
            step=0.5,
        )

        sim_live_birds = tot_chicks * (1 - sim_mortality / 100.0)
        sim_tot_weight_kg = sim_live_birds * (last_weight_g / 1000.0)
        sim_costs = chick_cost + (tot_feed_kg / 1000.0) * sim_feed_price
        sim_revenue = sim_tot_weight_kg * sim_sell_price
        sim_profit = sim_revenue - sim_costs

        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.metric("التكلفة المحاكاة", f"{sim_costs:,.2f} ج.م")
        s_col2.metric("الإيراد المحاكى", f"{sim_revenue:,.2f} ج.م")
        s_col3.metric(
            "صافي الربح المحاكى",
            f"{sim_profit:,.2f} ج.م",
            delta=f"{sim_profit - net_profit:,.2f} ج.م",
        )
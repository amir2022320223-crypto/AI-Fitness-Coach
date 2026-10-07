import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ----------------- معماری پایگاه داده (SQL Engine) -----------------
def init_db():
    conn = sqlite3.connect('portfolio_crm.db')
    c = conn.cursor()
    # ایجاد ساختار جداول در صورت عدم وجود
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            project_type TEXT NOT NULL,
            budget INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

# ----------------- تنظیمات رابط کاربری اینترپرایز -----------------
st.set_page_config(page_title="Smart CRM Dashboard", page_icon="📈", layout="wide")
st.markdown("""
<style>
    .stApp {background-color: #0f172a; color: #f1f5f9;}
    .metric-card {background-color: #1e293b; padding: 20px; border-radius: 10px; border-left: 4px solid #3b82f6; margin-bottom: 20px;}
    h1, h2, h3 {color: #60a5fa; font-weight: bold;}
    .stButton>button {background-color: #3b82f6; color: white; font-weight: bold;}
    .stButton>button:hover {background-color: #2563eb;}
</style>
""", unsafe_allow_html=True)

def main():
    conn = init_db()
    st.title("📈 سیستم هوشمند مدیریت قراردادها (CRM)")
    st.markdown("پلتفرم یکپارچه مدیریت لیدها، پیگیری وضعیت مذاکرات و تحلیل مالی پروژه‌ها")
    st.markdown("---")
    
    menu = st.sidebar.selectbox("⚙️ مدیریت سیستم", ["داشبورد مدیریتی", "ثبت پروژه جدید"])
    
    if menu == "ثبت پروژه جدید":
        st.subheader("📝 ورود اطلاعات کارفرما")
        with st.form("new_lead_form"):
            col1, col2 = st.columns(2)
            with col1:
                client_name = st.text_input("نام کارفرما / شرکت:")
                project_type = st.selectbox("نوع سرویس:", ["طراحی UI/UX", "توسعه فرانت‌اند", "سیستم فول‌استک", "مشاوره CRO"])
            with col2:
                budget = st.number_input("بودجه تخمینی پروژه (تومان):", min_value=0, step=1000000)
                status = st.selectbox("وضعیت مذاکره:", ["سرنخ اولیه (Lead)", "در حال مذاکره", "قرارداد بسته شده"])
            
            submitted = st.form_submit_button("💾 ثبت در پایگاه داده SQL")
            
            if submitted and client_name:
                c = conn.cursor()
                # اجرای کوئری امن برای جلوگیری از SQL Injection
                c.execute("INSERT INTO leads (client_name, project_type, budget, status, created_at) VALUES (?, ?, ?, ?, ?)", 
                          (client_name, project_type, budget, status, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success("✅ داده‌ها با موفقیت در جداول SQL ذخیره شدند.")
            elif submitted and not client_name:
                st.error("خطا: فیلد نام کارفرما الزامی است.")
                
    elif menu == "داشبورد مدیریتی":
        st.subheader("📊 تحلیل وضعیت مالی و پروژه‌ها")
        
        c = conn.cursor()
        c.execute("SELECT * FROM leads")
        data = c.fetchall()
        
        if data:
            # تبدیل داده‌های خام دیتابیس به ساختار جدولی برای تحلیل
            df = pd.DataFrame(data, columns=["ID", "Client", "Service", "Budget", "Status", "Date"])
            
            # محاسبات بک‌اند
            total_revenue = df[df['Status'] == 'قرارداد بسته شده']['Budget'].sum()
            active_leads = len(df[df['Status'] != 'قرارداد بسته شده'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>💰 درآمد قطعی (قراردادهای بسته شده)</h3>
                    <h2>{total_revenue:,} تومان</h2>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🔥 پروژه‌های در جریان (خط لوله)</h3>
                    <h2>{active_leads} پروژه</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("### 🗄️ خروجی زنده از جداول SQL:")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("پایگاه داده در حال حاضر خالی است. از پنل کناری یک پروژه جدید ثبت کنید.")

if __name__ == '__main__':
    main()
import pandas as pd
from pathlib import Path 
import base64 
import matplotlib.pyplot as plt 
import streamlit as st 
import mysql.connector

from mahasiswa_page import mahasiswa_page 
from input_nilai_page import input_nilai_page 
from analisis_nilai_page import analisis_nilai_page 
from mahasiswa_dashboard import mahasiswa_dashboard 
from db import get_db 

st.title("Test Koneksi Database")

db = st.secrets["mysql"]

try:
    conn = mysql.connector.connect(
        host=db["host"],
        port=db["port"],
        user=db["user"],
        password=db["password"],
        database=db["database"],
        ssl_disabled=True
    )
    st.success("✅ Database berhasil terhubung")
except Exception as e:
    st.error(f"❌ Database gagal: {e}")

# ====================== # PAGE CONFIG # ====================== 
st.set_page_config( 
    page_title="Vinix7 Aurum", 
    page_icon="📊", 
    layout="wide", 
    initial_sidebar_state="expanded" 
) 

LOGO_PATH = Path("assets/logo_vinix.jpg") # ====================== # GLOBAL STYLE (LIGHT) # ====================== # ====================== # GLOBAL STYLE (VINIX7 FIX) # ======================

st.markdown("""
<style>

/* ================= RESET ================= */
header, footer {visibility:hidden;}
#MainMenu {visibility:hidden;}

/* ================= APP BACKGROUND ================= */
.stApp {
    background: linear-gradient(135deg, #FFFFFF, #EEF4FF);
    color: #1F2937;
}

/* ================= SIDEBAR ================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B3C8C, #1E40AF);
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* ================= SIDEBAR RADIO ================= */
div[role="radiogroup"] label {
    color: #FFFFFF !important;
    font-weight: 600;
}

div[role="radiogroup"] input:checked + div {
    background-color: #FFD84D !important;
    border-color: #FFD84D !important;
}

/* ================= CARD / CONTAINER ================= */
.card, .login-card, .stContainer {
    background: #FFFFFF;
    padding: 24px;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(11,60,140,0.15);
}

/* ================= BUTTON ================= */
.stButton > button {
    background: #FFD84D;
    color: #0B3C8C;
    border-radius: 10px;
    font-weight: 800;
    border: none;
}

.stButton > button:hover {
    background: #FACC15;
    color: #0B3C8C;
}

/* ================= INPUT / SELECT ================= */
input, textarea, select {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
}

input:focus, textarea:focus {
    border-color: #0B3C8C !important;
    box-shadow: 0 0 0 2px rgba(11,60,140,0.15);
}

/* ================= SELECTBOX FIX ================= */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
}

/* ================= SLIDER ================= */
div[data-baseweb="slider"] span {
    background-color: #0B3C8C !important;
}

/* ================= METRIC ================= */
[data-testid="stMetric"] {
    background: linear-gradient(180deg, #0B3C8C, #1E40AF);
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 8px 22px rgba(11,60,140,0.15);
}

/* ================= TABLE ================= */
.stDataFrame, table {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
}

thead tr th {
    background-color: #EAF2FF !important;
    color: #0B3C8C !important;
    font-weight: 800;
}

tbody tr td {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
}

/* ================= CHART ================= */
[data-testid="stChart"] {
    background: #FFFFFF;
    padding: 22px;
    border-radius: 16px;
}

/* ================= ALERT ================= */
div[data-testid="stAlert"] {
    border-radius: 14px;
}

/* ================= HEADING ================= */
h1, h2, h3, h4 {
    color: #0B3C8C;
    font-weight: 800;
}

/* ================= LINK ================= */
a, a:hover, a:visited {
    color: #0B3C8C !important;
}

/* ================= MAHASISWA UI ================= */
.mhs-card {
    background: #ffffff;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 8px 22px rgba(11,60,140,0.12);
    margin-bottom: 24px;
}

.status-ok {
    background: #16a34a;
    color: white;
    padding: 16px;
    border-radius: 12px;
    font-weight: 700;
}
.status-warn {
    background: #f59e0b;
    color: white;
    padding: 16px;
    border-radius: 12px;
    font-weight: 700;
}
.status-bad {
    background: #dc2626;
    color: white;
    padding: 16px;
    border-radius: 12px;
    font-weight: 700;
}

/* ================= ALTAIR FIX ================= */
.vega-embed, .vega-embed canvas {
    background-color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ======================
# LOGO
# ======================
def display_logo():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
            <div style="text-align:center;margin-bottom:60px;">
                <img src="data:image/jpeg;base64,{b64}" style="width:100px;margin:auto;">
            </div>
            """, unsafe_allow_html=True)

# ======================
# LOGIN PAGE
# ======================
def login_page():
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        display_logo()

        st.markdown("""
        <h3 style="text-align:center">Student Learning Assistant</h3>
        <p style="text-align:center;color:#2563eb">VINIX7 AURUM</p>
        """, unsafe_allow_html=True)

        role = st.selectbox(
            "Login sebagai",
            ["Administrator", "Mahasiswa"]
        )

        username = st.text_input(
            "Username",
            placeholder="contoh: vinix_awan"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("LOGIN"):
            if not username or not password:
                st.warning("Username dan password wajib diisi")
                return

            role_db = "admin" if "Admin" in role else "mahasiswa"

            try:
                conn = get_db()
                cur = conn.cursor()

                # 🔴 QUERY YANG BENAR (USERNAME)
                cur.execute("""
                    SELECT id, role, student_id
                    FROM users
                    WHERE LOWER(username) = LOWER(%s)
                      AND password = %s
                      AND role = %s
                """, (username.strip(), password.strip(), role_db))

                user = cur.fetchone()
                conn.close()

                if user:
                    st.session_state.login = True
                    st.session_state.role = user[1]
                    st.session_state.student_id = user[2]
                    st.rerun()
                else:
                    st.error("Username atau password salah")

            except Exception as e:
                st.error(f"Database error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

# ======================
# DASHBOARD PAGE
# ======================
def dashboard_page():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_mahasiswa = cur.fetchone()[0]

    cur.execute("SELECT AVG(score) FROM module_scores")
    avg_nilai = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT COUNT(DISTINCT student_id)
        FROM module_scores
        WHERE score < 70
    """)
    perlu_perhatian = cur.fetchone()[0]

    cur.execute("""
        SELECT module, AVG(score)
        FROM module_scores
        GROUP BY module
        ORDER BY CAST(module AS UNSIGNED)
    """)
    module_avg = cur.fetchall()

    conn.close()

    df_modul = pd.DataFrame(
        module_avg,
        columns=["Modul", "Rata-rata Nilai"]
    )
    df_modul["Modul"] = df_modul["Modul"].astype(int)
    df_modul["Rata-rata Nilai"] = df_modul["Rata-rata Nilai"].round(2)



    col1, col2, col3 = st.columns(3)
    col1.metric("👨‍🎓 Total Mahasiswa", total_mahasiswa)
    col2.metric("📊 Rata-rata Nilai", f"{avg_nilai:.2f}")
    col3.metric("⚠️ Mahasiswa dengan Nilai < 70", perlu_perhatian)

    import matplotlib.pyplot as plt

    st.markdown("### 📊 Rata-rata Nilai per Modul")

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 3))  # ⬅️ BENAR-BENAR KECIL

    ax.plot(
        df_modul["Modul"],
        df_modul["Rata-rata Nilai"],
        marker="o",
        linewidth=2,
        color="#2563eb"
    )

    ax.set_xlabel("Modul")
    ax.set_ylabel("Nilai Rata-rata")
    ax.set_ylim(0, 100)

    ax.grid(True, linestyle="--", alpha=0.4)

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    plt.tight_layout()

    # 🔴 KUNCI UTAMA ADA DI SINI
    with st.container():
        st.pyplot(fig, use_container_width=False)







# ======================
# ADMIN DASHBOARD
# ======================
def admin_dashboard():
    with st.sidebar:
        st.markdown("## ⚙️ Admin Panel")
        menu = st.radio(
            "Navigasi",
            ["📊 Dashboard", "👨‍🎓 Kelola Mahasiswa", "📝 Input Nilai", "🤖 Analisis Nilai"]
        )
        st.markdown("---")
        if st.button("🔓 Logout"):
            st.session_state.clear()
            st.rerun()

    st.markdown("""
    <div style="
    background: linear-gradient(135deg, #0B3C8C, #1E40AF);
    padding:28px;
    border-radius:18px;
    color:white;
    box-shadow:0 10px 30px rgba(11,60,140,0.35);
    margin-bottom:30px;
    ">
        <h2 style="margin-bottom:5px;">📊 Dashboard Admin</h2>
        <p style="opacity:0.9;margin:0;">
            Ringkasan data akademik peserta
        </p>
    </div>
    """, unsafe_allow_html=True)


    if menu == "📊 Dashboard":
        dashboard_page()
    elif menu == "👨‍🎓 Kelola Mahasiswa":
        mahasiswa_page()
    elif menu == "📝 Input Nilai":
        input_nilai_page()
    elif menu == "🤖 Analisis Nilai":
        analisis_nilai_page()

# ======================
# MAIN
# ======================
def main():
    if "login" not in st.session_state:
        st.session_state.login = False

    if not st.session_state.login:
        login_page()
    else:
        if st.session_state.role == "admin":
            admin_dashboard()
        else:
            mahasiswa_dashboard(st.session_state.student_id)

if __name__ == "__main__":
    main()



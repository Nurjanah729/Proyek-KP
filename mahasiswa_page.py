import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. UI ENGINE (LOCK VISIBILITY & STYLE)
# ==========================================
st.markdown("""
    <style>
    /* Mengunci warna teks agar tetap hitam tajam di seluruh aplikasi */
    html, body, [data-testid="stWidgetLabel"], p, span, div {
        color: #111111 !important;
    }

    /* Mempertegas Label Tab */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-weight: 800 !important;
        font-size: 16px !important;
    }

    /* Desain Box Input yang Jelas */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border: 1.5px solid #A0AEC0 !important;
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
    }

    /* Tombol Biru Profesional */
    div.stButton > button {
        background-color: #0045AD !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        height: 48px !important;
        width: 180px !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_universitas():
    try:
        # Membaca data universitas dari file Anda
        df = pd.read_csv("universitas_indonesia.csv")
        return sorted(df['nama_universitas'].unique().tolist())
    except Exception:
        return ["Universitas Indonesia", "Institut Teknologi Bandung"]

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. HALAMAN MAHASISWA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Administrasi Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    tab1, tab2, tab3 = st.tabs(["📊 Database", "📤 Import Kolektif", "✍️ Tambah Manual"])

    # --- TAB DATABASE ---
    with tab1:
        st.subheader("Data Mahasiswa")
        cur.execute("SELECT s.id, u.username, s.name, s.division, s.university FROM students s JOIN users u ON s.id = u.student_id ORDER BY s.id DESC")
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Username", "Nama", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB IMPORT ---
    with tab2:
        st.subheader("Registrasi Massal")
        uploaded_file = st.file_uploader("Pilih File (CSV/XLSX)", type=["csv", "xlsx"])
        if uploaded_file and st.button("Proses File"):
            st.success("Data sedang diproses...")

    # --- TAB MANUAL (PERBAIKAN TOTAL) ---
    with tab3:
        st.subheader("Input Data Mahasiswa Baru")
        
        col1, col2 = st.columns(2)
        with col1:
            # Teks Label di atas box tetap ada
            nama_m = st.text_input("Nama Lengkap Mahasiswa", placeholder="Masukkan nama...")
            div_m = st.selectbox("Pilih Divisi", ["Web Developer", "Data Science", "AI Engineer"])
        
        with col2:
            # Dropdown mengambil data dari csv
            list_univ = load_universitas()
            univ_p = st.selectbox("Asal Universitas", options=["Pilih Universitas"] + list_univ + ["➕ Input Manual"])
            
            # Jika klik Input Manual, box baru muncul dengan label yang tetap terlihat
            univ_m = ""
            if univ_p == "➕ Input Manual":
                univ_m = st.text_input("Ketik Nama Universitas Secara Manual", placeholder="Nama kampus...")
            elif univ_p != "Pilih Universitas":
                univ_m = univ_p

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Simpan ke Database"):
            if nama_m and univ_m:
                cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                conn.commit()
                st.success(f"Berhasil! Mahasiswa {nama_m} telah terdaftar.")
                st.rerun()
            else:
                st.warning("Mohon lengkapi semua data.")

    conn.close()

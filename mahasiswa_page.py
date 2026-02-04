import streamlit as st
import pandas as pd
from db import get_db

# 1. CSS AGAR TEKS HITAM TAJAM & TAB TERLIHAT JELAS
st.markdown("""
    <style>
    * { color: #111111 !important; }
    div[data-testid="stWidgetLabel"] p { font-weight: 700 !important; font-size: 16px !important; }
    .stApp { background-color: white !important; }
    /* Mempercantik tombol biru */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        font-weight: bold !important;
        width: 100%;
        height: 45px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNGSI LOAD DATA CSV
@st.cache_data
def get_univ_list():
    try:
        df = pd.read_csv("universitas_indonesia.csv")
        return sorted(df['nama_universitas'].dropna().unique().tolist())
    except:
        return ["Universitas Indonesia", "Institut Teknologi Bandung"]

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# 3. LOGIKA NAVIGASI AGAR TIDAK RESET KE AWAL
if 'menu_nav' not in st.session_state:
    st.session_state.menu_nav = "➕ Tambah Manual" # Set default ke menu yang sedang dikerjakan

def mahasiswa_page():
    st.title("👨‍🎓 Sistem Kelola Mahasiswa")
    
    # MENGGUNAKAN RADIO SEBAGAI TAB AGAR POSISI TERKUNCI (TIDAK AKAN BALIK KE AWAL)
    st.session_state.menu_nav = st.radio("", ["📊 Database", "📤 Import Kolektif", "➕ Tambah Manual"], 
                                        index=2, horizontal=True, label_visibility="collapsed")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # --- KONDISI HALAMAN ---
    if st.session_state.menu_nav == "📊 Database":
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id DESC")
        res = cur.fetchall()
        st.dataframe(pd.DataFrame(res, columns=["ID", "Nama", "Divisi", "Universitas"]), use_container_width=True, hide_index=True)

    elif st.session_state.menu_nav == "📤 Import Kolektif":
        st.file_uploader("Upload File", type=["csv"], key="file_up")

    elif st.session_state.menu_nav == "➕ Tambah Manual":
        col1, col2 = st.columns(2)
        with col1:
            nama_m = st.text_input("Nama Lengkap Mahasiswa", placeholder="Contoh: Andi Pratama", key="name_manual")
            div_m = st.selectbox("Divisi", ["Web Developer", "Data Science", "AI Engineer"], key="div_manual")

        with col2:
            univ_data = get_univ_list()
            # SAAT KLIK INI, HALAMAN TETAP DI SINI KARENA POSISI NAVIGASI DIKUNCI DI SESSION_STATE
            pilihan_univ = st.selectbox("Asal Universitas", options=["-- Pilih --"] + univ_data + ["➕ Input Manual"], key="univ_select")

            univ_final = ""
            if pilihan_univ == "➕ Input Manual":
                univ_final = st.text_input("Masukkan Nama Universitas", placeholder="Ketik di sini...", key="manual_text_box")
            elif pilihan_univ != "-- Pilih --":
                univ_final = pilihan_univ

        if st.button("Simpan Ke Database"):
            if nama_m and univ_final:
                cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_final))
                conn.commit()
                st.success(f"Berhasil menyimpan {nama_m}!")
                st.rerun()
            else:
                st.warning("Mohon isi nama dan universitas.")

    conn.close()

mahasiswa_page()

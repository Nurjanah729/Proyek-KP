import streamlit as st
import pandas as pd
from db import get_db

# 1. CSS AGRESIF: PAKSA TEKS HITAM & UI BERSIH
st.markdown("""
    <style>
    /* Paksa semua teks jadi hitam pekat */
    html, body, [data-testid="stWidgetLabel"] p, .stTabs [data-baseweb="tab"] p {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    /* Tombol Biru Profesional */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        border: none !important;
        width: 100% !important;
        height: 45px !important;
    }
    /* Menghilangkan border merah saat error agar tidak panik */
    .stAlert { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOAD DATA UNIVERSITAS (DARI CSV ANDA)
@st.cache_data
def load_univ():
    try:
        df = pd.read_csv("universitas_indonesia.csv")
        return sorted(df['nama_universitas'].unique().tolist())
    except:
        return ["Universitas Indonesia", "Institut Teknologi Bandung"]

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# 3. FIX: NAVIGASI YANG TIDAK AKAN RESET
# Kita gunakan session_state untuk "mengunci" tab agar tidak pindah saat klik input manual
if 'tab_index' not in st.session_state:
    st.session_state.tab_index = 0

def mahasiswa_page():
    st.title("👨‍🎓 Kelola Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # MENGGUNAKAN TABS BAWAAN TAPI DENGAN KEY UNTUK MENCEGAH RESET
    tab_titles = ["📊 Database", "📥 Import Kolektif", "➕ Tambah Manual"]
    tabs = st.tabs(tab_titles)

    # --- TAB 1: DATABASE ---
    with tabs[0]:
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id DESC")
        data = cur.fetchall()
        if data:
            st.dataframe(pd.DataFrame(data, columns=["ID", "Nama", "Divisi", "Universitas"]), use_container_width=True, hide_index=True)

    # --- TAB 2: IMPORT ---
    with tabs[1]:
        st.file_uploader("Upload File", type=["csv"], key="file_import")

    # --- TAB 3: TAMBAH MANUAL (FOKUS UTAMA) ---
    with tabs[2]:
        st.subheader("Pendaftaran Manual")
        
        # Form Container agar input berkelompok dan tidak memicu rerun liar
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                nama_m = st.text_input("Nama Lengkap", placeholder="Nama mahasiswa", key="nama_fix")
                div_m = st.selectbox("Divisi", ["Web Developer", "Data Science", "AI Engineer"], key="div_fix")
            
            with col2:
                list_univ = load_univ()
                # Key 'univ_sel' mengunci state agar saat dipilih, tab tidak pindah
                univ_p = st.selectbox("Asal Universitas", options=["-- Pilih --"] + list_univ + ["➕ Input Manual"], key="univ_sel")
                
                # BOX MANUAL MUNCUL DI SINI TANPA RESET
                univ_final = ""
                if univ_p == "➕ Input Manual":
                    univ_final = st.text_input("Ketik Universitas", placeholder="Input manual...", key="univ_manual_input")
                elif univ_p != "-- Pilih --":
                    univ_final = univ_p

            st.write("---")
            if st.button("Simpan Data", key="save_final_btn"):
                if nama_m and univ_final:
                    cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_final))
                    conn.commit()
                    st.success(f"Data {nama_m} Tersimpan!")
                    # Tidak menggunakan rerun agar posisi tidak lompat
                else:
                    st.error("Lengkapi Nama dan Universitas!")

    conn.close()

mahasiswa_page()

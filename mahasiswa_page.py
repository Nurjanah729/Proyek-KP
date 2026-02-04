import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. UI CUSTOMIZATION (PROFESSIONAL LIGHT)
# ==========================================
st.markdown("""
    <style>
    /* Paksa teks Tab tetap terlihat hitam pekat dan tebal */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #1A1A1A !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Warna teks label di atas box input agar terlihat jelas */
    div[data-testid="stWidgetLabel"] p {
        color: #31333F !important;
        font-weight: 500 !important;
    }

    /* Mempercantik box input */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border: 1px solid #DDE1E6 !important;
        border-radius: 6px !important;
    }

    /* TOMBOL SIMPAN: Biru Royal Profesional */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        border-radius: 4px !important;
        border: none !important;
        font-weight: 600 !important;
        width: 180px !important;
        height: 45px !important;
    }
    div.stButton > button:hover {
        background-color: #003385 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def get_list_universitas():
    try:
        # Mengambil data dari file csv yang diunggah
        df = pd.read_csv("universitas_indonesia.csv")
        list_univ = sorted(df['nama_universitas'].dropna().unique().tolist())
        list_univ.append("➕ Input Manual")
        return list_univ
    except:
        return ["➕ Input Manual"]

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. MAIN INTERFACE
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Manajemen Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    tab_list, tab_import, tab_manual = st.tabs([
        "📊 Database", "📥 Registrasi Kolektif", "✍️ Entri Mandiri"
    ])

    # --- TAB 1: DATABASE ---
    with tab_list:
        st.subheader("Daftar Mahasiswa Terdaftar")
        cur.execute("SELECT s.id, u.username, s.name, s.division, s.university FROM students s JOIN users u ON s.id = u.student_id WHERE u.role = 'mahasiswa' ORDER BY s.id DESC")
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Username", "Nama", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 2: IMPORT KOLEKTIF ---
    with tab_import:
        st.subheader("Import Data via File")
        uploaded_file = st.file_uploader("Pilih file CSV atau Excel", type=["csv", "xlsx"], help="Format: id, name, division, university")
        
        if uploaded_file:
            df_up = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            if st.button("Proses Import", key="btn_bulk"):
                for _, row in df_up.iterrows():
                    sid, sname, sdiv, suniv = row['id'], row['name'], row['division'], row['university']
                    u, p = generate_credentials(sname, sid)
                    cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                    cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (u, p, "mahasiswa", sid))
                conn.commit()
                st.success("Data berhasil diimpor.")
                st.rerun()

    # --- TAB 3: ENTRI MANDIRI (DENGAN CSV UNIVERSITAS) ---
    with tab_manual:
        st.subheader("Input Data Mahasiswa Baru")
        
        col1, col2 = st.columns(2)
        with col1:
            # Teks di atas box diaktifkan kembali
            nama_m = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso", key="m_nama")
            div_m = st.selectbox("Divisi Penempatan", ["Web Developer", "Data Science", "AI Engineer"], key="m_div")
        
        with col2:
            # Menggunakan list dari CSV universitas_indonesia.csv
            univ_list = get_list_universitas()
            univ_p = st.selectbox("Asal Universitas", options=univ_list, index=None, placeholder="Pilih Kampus", key="m_univ_s")
            
            if univ_p == "➕ Input Manual":
                univ_m = st.text_input("Nama Universitas Manual", placeholder="Masukkan nama kampus", key="m_univ_t")
            else:
                univ_m = univ_p

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Simpan ke Database", key="m_save"):
            if nama_m and univ_m:
                cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                conn.commit()
                new_id = cur.lastrowid
                u, p = generate_credentials(nama_m, new_id)
                cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                conn.commit()
                st.success(f"Berhasil disimpan. Username: {u}")
            else:
                st.warning("Mohon lengkapi data.")

    conn.close()

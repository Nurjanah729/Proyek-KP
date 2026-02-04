import streamlit as st
import pandas as pd
from db import get_db
import random

# ==========================================
# 1. UI CUSTOMIZATION (LIGHT MODE PROFESSIONAL)
# ==========================================
st.markdown("""
    <style>
    /* Latar belakang putih bersih */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Memperbaiki Tab: Teks harus hitam pekat agar terlihat jelas */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 17px;
        font-weight: 600;
        color: #1A1A1A !important; 
    }
    
    /* Indikator Tab Aktif */
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #0045AD !important;
    }

    /* Input Box: Minimalis dengan Placeholder */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: #FDFDFD !important;
        border: 1px solid #DDE1E6 !important;
        color: #1A1A1A !important;
        border-radius: 6px !important;
        height: 45px;
    }

    /* Tombol Utama: Biru Profesional Tanpa Radius Berlebih */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        border-radius: 4px !important;
        border: none !important;
        font-weight: 500 !important;
        padding: 0.5rem 2rem !important;
        width: auto !important; /* Tidak memenuhi layar kecuali diatur */
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def get_list_universitas():
    try:
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
# 2. INTERFACE KELOLA MAHASISWA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Manajemen Mahasiswa")
    st.markdown("<p style='color: #4D5358;'>Kelola data akademik dan otoritas akses pengguna dalam satu dasbor terpadu.</p>", unsafe_allow_html=True)
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Navigasi dengan kontras tinggi
    tab_list, tab_import, tab_manual = st.tabs([
        "📊 Database Mahasiswa", 
        "📤 Registrasi Kolektif", 
        "➕ Pendaftaran Baru"
    ])

    # --- TAB 1: DAFTAR MAHASISWA ---
    with tab_list:
        st.subheader("Arsip Mahasiswa Terdaftar")
        cur.execute("""
            SELECT s.id, u.username, s.name, s.division, s.university 
            FROM students s 
            JOIN users u ON s.id = u.student_id 
            WHERE u.role = 'mahasiswa' 
            ORDER BY s.id DESC
        """)
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Username", "Nama Mahasiswa", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data mahasiswa yang terdata.")

    # --- TAB 2: IMPORT KOLEKTIF ---
    with tab_import:
        st.subheader("Integrasi Data Massal")
        # Menghilangkan teks manual, menggunakan tooltip info
        uploaded_file = st.file_uploader("", type=["csv", "xlsx"], 
                                         help="Unggah berkas dengan struktur kolom: id, name, division, university")
        
        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file, sep=None, engine='python') if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                df_up.columns = [c.strip().lower() for c in df_up.columns] 
                
                st.write("**Pratinjau Data Berkas:**")
                st.dataframe(df_up.head(3), use_container_width=True)

                if st.button("Proses Integrasi Berkas", key="btn_import"):
                    for _, row in df_up.iterrows():
                        sid, sname = int(row['id']), str(row['name'])
                        sdiv, suniv = str(row['division']), str(row['university'])
                        uname, upass = generate_credentials(sname, sid)

                        cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                        cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                    
                    conn.commit()
                    st.success("Integrasi data kolektif berhasil diselesaikan.")
                    st.rerun()
            except Exception as e:
                st.error(f"Kegagalan sistem proses berkas: {e}")

    # --- TAB 3: PENDAFTARAN MANUAL ---
    with tab_manual:
        st.subheader("Registrasi Mahasiswa Baru")
        
        # Desain tanpa label atas, menggunakan placeholder murni
        c1, c2 = st.columns(2)
        with c1:
            nama_m = st.text_input("", placeholder="Masukkan nama lengkap mahasiswa", key="in_nama")
            div_m = st.selectbox("", ["Web Developer", "Data Science", "AI Engineer"], index=0, key="in_div")
        
        with c2:
            univ_list = get_list_universitas()
            univ_p = st.selectbox("", options=univ_list, index=None, placeholder="Pilih Universitas", key="in_univ_s")
            
            univ_m = ""
            if univ_p == "➕ Input Manual":
                univ_m = st.text_input("", placeholder="Ketik Nama Universitas secara manual", key="in_univ_t")
            else:
                univ_m = univ_p

        # Tombol simpan yang rapi di sisi kiri
        if st.button("Simpan ke Database", key="btn_manual_save"):
            if nama_m and univ_m:
                cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                conn.commit()
                new_id = cur.lastrowid
                u, p = generate_credentials(nama_m, new_id)
                cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                conn.commit()
                st.success(f"Registrasi berhasil. Akun akses: {u}")
            else:
                st.warning("Seluruh kolom entri wajib dilengkapi.")

    conn.close()

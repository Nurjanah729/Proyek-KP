import streamlit as st
import pandas as pd
from db import get_db
import random

# ==========================================
# 1. UI FIX (MEMAKSA VISIBILITAS TEKS)
# ==========================================
st.markdown("""
    <style>
    /* Memaksa latar belakang aplikasi putih bersih */
    .stApp {
        background-color: #FFFFFF !important;
    }

    /* FIX TAB: Memaksa teks tab muncul dengan warna hitam pekat */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #111111 !important; 
        font-weight: 700 !important;
        font-size: 16px !important;
    }

    /* Tab yang sedang dipilih diberi warna biru royal */
    .stTabs [aria-selected="true"] p {
        color: #0045AD !important;
    }

    /* Memperbaiki warna tombol agar kontras (Biru Royal) */
    div.stButton > button {
        background-color: #0045AD !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 0.5rem 2rem !important;
        font-weight: bold !important;
    }

    /* Styling input box agar terlihat jelas batasnya */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border: 1px solid #CCCCCC !important;
        color: #111111 !important;
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
# 2. HALAMAN UTAMA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Kelola Mahasiswa")
    st.markdown("Manajemen data akademik dan akun akses mahasiswa dalam satu panel.")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Menggunakan tab dengan label yang dipaksa terlihat
    tab_list, tab_import, tab_manual = st.tabs([
        "📊 Daftar Mahasiswa", 
        "📤 Import File", 
        "➕ Tambah Manual"
    ])

    # --- TAB 1: DAFTAR ---
    with tab_list:
        st.subheader("Database Mahasiswa")
        cur.execute("""
            SELECT s.id, u.username, s.name, s.division, s.university 
            FROM students s 
            JOIN users u ON s.id = u.student_id 
            WHERE u.role = 'mahasiswa' 
            ORDER BY s.id DESC
        """)
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Username", "Nama", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data.")

    # --- TAB 2: IMPORT ---
    with tab_import:
        st.subheader("Registrasi Massal via File")
        # Instruksi format dipindahkan ke tooltip (ikon tanda tanya) agar bersih
        uploaded_file = st.file_uploader("", type=["csv", "xlsx"], 
                                         help="Format kolom: id, name, division, university")
        
        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file, sep=None, engine='python') if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                df_up.columns = [c.strip().lower() for c in df_up.columns] 
                
                st.write("**Preview Data:**")
                st.dataframe(df_up.head(3), use_container_width=True)

                if st.button("Daftarkan Semua Mahasiswa", key="btn_import"):
                    for _, row in df_up.iterrows():
                        sid, sname = int(row['id']), str(row['name'])
                        sdiv, suniv = str(row['division']), str(row['university'])
                        uname, upass = generate_credentials(sname, sid)

                        cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                        cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                    
                    conn.commit()
                    st.success("Import berhasil!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # --- TAB 3: TAMBAH MANUAL ---
    with tab_manual:
        st.subheader("Input Data Mahasiswa Baru")
        
        # Grid layout tanpa label teks di atas (menggunakan placeholder)
        c1, c2 = st.columns(2)
        with c1:
            nama_m = st.text_input("", placeholder="Nama Lengkap", key="m_nama")
            div_m = st.selectbox("", ["Web Developer", "Data Science", "AI Engineer"], index=0, key="m_div")
        
        with c2:
            univ_list = get_list_universitas()
            univ_p = st.selectbox("", options=univ_list, index=None, placeholder="Pilih Universitas", key="m_univ_s")
            
            univ_m = st.text_input("", placeholder="Input Universitas Manual", key="m_univ_t") if univ_p == "➕ Input Manual" else univ_p

        if st.button("Simpan ke Database", key="btn_save"):
            if nama_m and univ_m:
                cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                conn.commit()
                new_id = cur.lastrowid
                u, p = generate_credentials(nama_m, new_id)
                cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                conn.commit()
                st.success(f"Berhasil! Username: {u}")
            else:
                st.warning("Data belum lengkap.")

    conn.close()

import streamlit as st
import pandas as pd
from db import get_db
import random

# ==========================================
# 1. UI CUSTOMIZATION (CLEAN LIGHT MODE)
# ==========================================
st.markdown("""
    <style>
    /* Latar belakang halaman putih bersih */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Warna Tab yang tegas dan kontras (Hitam di atas Putih) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 2px solid #F0F2F6;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        color: #4A4A4A !important; /* Abu-abu gelap */
    }
    .stTabs [aria-selected="true"] {
        color: #0045AD !important; /* Biru Royal saat terpilih */
        border-bottom: 3px solid #0045AD !important;
    }

    /* Styling Input Box agar lebih elegan */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: #F8F9FA !important;
        border: 1px solid #E9ECEF !important;
        color: #212529 !important;
        border-radius: 8px !important;
    }

    /* Tombol Utama (Biru Profesional) */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #003385 !important;
        box-shadow: 0 4px 12px rgba(0,69,173,0.2);
    }

    /* Styling khusus untuk input manual - MEMPERJELAS TEKS */
    .manual-input-container {
        margin-top: 1rem;
        padding: 1.5rem;
        background-color: #F8F9FA;
        border-radius: 12px;
        border: 2px solid #E9ECEF;
    }
    .manual-input-container .stTextInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #0045AD !important;
        font-size: 16px !important;
        color: #212529 !important;
        padding: 12px 16px !important;
    }
    .manual-input-label {
        font-weight: 600 !important;
        color: #0045AD !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }
    .manual-input-help {
        color: #6C757D !important;
        font-size: 0.9rem !important;
        margin-top: 0.25rem !important;
        font-style: italic !important;
    }
    
    /* Styling untuk dropdown universitas */
    .university-select-container {
        margin-bottom: 1.5rem;
    }
    
    /* Highlight untuk opsi "Input Manual" */
    [data-baseweb="select"] div[role="option"]:contains("➕ Input Manual") {
        color: #0045AD !important;
        font-weight: 600 !important;
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
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
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
    st.markdown("<p style='color: #6C757D; font-size: 1.1em;'>Sistem administrasi pusat untuk pengelolaan data mahasiswa dan kredensial akses.</p>", unsafe_allow_html=True)
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Navigasi Tab dengan Label yang Jelas
    tab_list, tab_import, tab_manual = st.tabs([
        "📁 Database Terpusat", 
        "📤 Registrasi Kolektif", 
        "➕ Entri Mandiri"
    ])

    # --- TAB 1: DATABASE ---
    with tab_list:
        st.subheader("Daftar Entitas Terdaftar")
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
            st.dataframe(df, use_container_width=True, hide_index=True) # Menggunakan tabel bersih
        else:
            st.info("Tidak ada data mahasiswa yang ditemukan dalam database.")

    # --- TAB 2: IMPORT KOLEKTIF ---
    with tab_import:
        st.subheader("Unggah Data Massal")
        # Tooltip menggantikan teks manual yang berantakan
        uploaded_file = st.file_uploader("", type=["csv", "xlsx"], 
                                         help="Header wajib: id, name, division, university")
        
        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file, sep=None, engine='python') if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                df_up.columns = [c.strip().lower() for c in df_up.columns] # Normalisasi kolom
                
                st.write("**Pratinjau Berkas:**")
                st.dataframe(df_up.head(3), use_container_width=True)

                if st.button("Lakukan Integrasi Data", key="btn_bulk"):
                    for _, row in df_up.iterrows():
                        sid, sname = int(row['id']), str(row['name'])
                        sdiv, suniv = str(row['division']), str(row['university'])
                        uname, upass = generate_credentials(sname, sid)

                        cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                        cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                    
                    conn.commit()
                    st.success("Sinkronisasi database berhasil.")
                    st.rerun()
            except Exception as e:
                st.error(f"Kesalahan sistem: {e}")

    # --- TAB 3: ENTRI MANDIRI ---
    with tab_manual:
        st.subheader("Registrasi Mahasiswa Baru")
        
        # Grid Layout tanpa label teks atas
        c1, c2 = st.columns(2)
        
        with c1:
            nama_m = st.text_input("", placeholder="Nama Lengkap", key="m_nama")
            div_m = st.selectbox("", ["Web Developer", "Data Science", "AI Engineer"], index=0, key="m_div")
        
        with c2:
            univ_list = get_list_universitas()
            univ_p = st.selectbox("", options=univ_list, index=None, 
                                 placeholder="🔍 Pilih Universitas dari daftar...", 
                                 key="m_univ_s")
            
            # PERBAIKAN UTAMA: Membuat input manual lebih jelas
            if univ_p == "➕ Input Manual":
                # Container khusus untuk input manual dengan styling jelas
                st.markdown('<div class="manual-input-container">', unsafe_allow_html=True)
                st.markdown('<span class="manual-input-label">✏️ Input Nama Universitas Manual</span>', unsafe_allow_html=True)
                univ_m = st.text_input("", 
                                      placeholder="Ketik nama universitas disini...", 
                                      key="m_univ_t",
                                      label_visibility="collapsed")
                st.markdown('<span class="manual-input-help">Pastikan nama universitas ditulis dengan benar</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                univ_m = univ_p
                # Tampilkan pesan jika universitas dipilih dari daftar
                if univ_m:
                    st.info(f"✅ Universitas dipilih: **{univ_m}**")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tombol dengan feedback yang lebih jelas
        if st.button("Simpan ke Database", key="btn_save_manual", type="primary"):
            if nama_m and univ_m:
                cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                conn.commit()
                new_id = cur.lastrowid
                u, p = generate_credentials(nama_m, new_id)
                cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                conn.commit()
                
                # Tampilkan hasil dengan lebih jelas
                st.success("🎉 Pendaftaran Berhasil!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ID Mahasiswa", new_id)
                with col2:
                    st.metric("Username", u)
                with col3:
                    st.metric("Password", p)
                    
                # Tampilkan ringkasan data
                st.info(f"""
                **Ringkasan Data:**
                - Nama: {nama_m}
                - Divisi: {div_m}
                - Universitas: {univ_m}
                """)
            else:
                st.warning("⚠️ Mohon lengkapi seluruh data yang diperlukan.")

    conn.close()

import streamlit as st
import pandas as pd
from db import get_db
import random

# ==========================================
# 1. LOGIKA PENDUKUNG (UTILITY)
# ==========================================
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
# 2. ANTARMUKA UTAMA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Sistem Informasi Mahasiswa")
    st.caption("Otoritas manajemen data akademik dan akun akses mahasiswa.")
    
    conn = get_db()
    cur = conn.cursor()

    # Navigasi Tab Profesional
    tab_list, tab_import, tab_manual = st.tabs([
        "📊 Database Mahasiswa", 
        "📥 Registrasi Kolektif", 
        "✍️ Entri Mandiri"
    ])

    # --- TAB 1: DATABASE ---
    with tab_list:
        st.subheader("Daftar Mahasiswa Terdaftar")
        cur.execute("""
            SELECT s.id, u.username, s.name, s.division, s.university 
            FROM students s 
            JOIN users u ON s.id = u.student_id 
            WHERE u.role = 'mahasiswa' 
            ORDER BY s.id DESC
        """)
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Username", "Nama Lengkap", "Divisi", "Instansi Pendidikan"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data mahasiswa yang tersimpan dalam sistem.")

    # --- TAB 2: REGISTRASI KOLEKTIF (IMPORT) ---
    with tab_import:
        st.subheader("Sinkronisasi Data Massal")
        st.info("Pastikan file Anda memiliki header: id, name, division, university")
        
        uploaded_file = st.file_uploader("", type=["csv", "xlsx"], help="Drag & drop file laporan di sini")
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_up = pd.read_csv(uploaded_file, sep=None, engine='python')
                else:
                    df_up = pd.read_excel(uploaded_file)
                
                # Auto-fix data menumpuk
                df_up.columns = [c.strip().lower() for c in df_up.columns]
                if len(df_up.columns) == 1 and ',' in df_up.columns[0]:
                    raw_cols = df_up.columns[0]
                    df_up = df_up[raw_cols].str.split(',', expand=True)
                    df_up.columns = [c.strip().lower() for c in raw_cols.split(',')]

                st.write("**Pratinjau Berkas:**")
                st.dataframe(df_up.head(3), use_container_width=True)

                if st.button("Lakukan Integrasi Data", type="primary", use_container_width=True):
                    for _, row in df_up.iterrows():
                        sid, sname = int(row['id']), str(row['name'])
                        sdiv, suniv = str(row['division']), str(row['university'])
                        uname, upass = generate_credentials(sname, sid)

                        cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                        cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                    
                    conn.commit()
                    st.success("Sinkronisasi database berhasil diselesaikan.")
                    st.rerun()
            except Exception as e:
                st.error(f"Kegagalan sistem saat memproses berkas: {e}")

    # --- TAB 3: ENTRI MANDIRI (MANUAL) ---
    with tab_manual:
        st.subheader("Pendaftaran Mahasiswa Baru")
        
        # Form tanpa teks label di atas box (menggunakan placeholder)
        col_a, col_b = st.columns(2)
        with col_a:
            nama_m = st.text_input("", placeholder="Nama Lengkap Mahasiswa", key="m_nama")
            div_m = st.selectbox("", ["Web Developer", "Data Science", "AI Engineer"], index=0, key="m_div")
        
        with col_b:
            univ_list = get_list_universitas()
            univ_p = st.selectbox("", options=univ_list, index=None, placeholder="Pilih Instansi/Kampus", key="m_univ_s")
            
            univ_m = ""
            if univ_p == "➕ Input Manual":
                univ_m = st.text_input("", placeholder="Ketik Nama Universitas di sini", key="m_univ_t")
            else:
                univ_m = univ_p

        if st.button("Simpan ke Database", type="primary", use_container_width=True):
            if nama_m and univ_m:
                cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                conn.commit()
                new_id = cur.lastrowid
                u, p = generate_credentials(nama_m, new_id)
                cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                conn.commit()
                st.success(f"Mahasiswa baru terdaftar. Akun: {u} | Sandi: {p}")
            else:
                st.warning("Seluruh field entri wajib dilengkapi.")

    conn.close()

# Footer Profesional
st.divider()
st.caption("© 2026 Vinix Intelligence - Secure Administrative Portal")

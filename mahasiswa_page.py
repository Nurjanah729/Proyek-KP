import streamlit as st
import pandas as pd
from db import get_db
import random

# ==========================================
# 1. FUNGSI UTILITY
# ==========================================
@st.cache_data
def get_list_universitas():
    try:
        df = pd.read_csv("universitas_indonesia.csv")
        list_univ = sorted(df['nama_universitas'].dropna().unique().tolist())
        list_univ.append("➕ Input Manual (Tidak ada di daftar)")
        return list_univ
    except Exception:
        return ["➕ Input Manual (Tidak ada di daftar)"]

def generate_username(nama, s_id=None):
    base = nama.lower().split()[0]
    suffix = s_id if s_id else random.randint(100, 999)
    return f"vinix_{base}_{suffix}"

def generate_password(s_id):
    return f"VNX-{s_id}X"

# ==========================================
# 2. HALAMAN UTAMA
# ==========================================
def mahasiswa_page():
    # Header Profesional
    st.title("👨‍🎓 Manajemen Data Mahasiswa")
    st.markdown("""
        Pusat kendali data mahasiswa magang dan studi independen. 
        Gunakan tab di bawah untuk navigasi antar fungsi.
    """)
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Navigasi menggunakan Tabs agar interface tidak berantakan
    tab1, tab2, tab3 = st.tabs(["📋 Daftar Mahasiswa", "📥 Import Massal", "➕ Tambah Manual"])

    # ------------------------------------------
    # TAB 1: DAFTAR MAHASISWA
    # ------------------------------------------
    with tab1:
        st.subheader("Data Mahasiswa Terdaftar")
        cur.execute("""
            SELECT s.id, u.username, s.name, s.division, s.university
            FROM students s
            JOIN users u ON s.id = u.student_id
            WHERE u.role = 'mahasiswa'
            ORDER BY s.id DESC
        """)
        rows = cur.fetchall()
        
        if not rows:
            st.info("Saat ini belum ada data mahasiswa yang terdaftar di sistem.")
        else:
            df_list = pd.DataFrame(rows, columns=["ID", "Username", "Nama Lengkap", "Divisi", "Universitas"])
            # Tampilan table yang lebih bersih
            st.dataframe(df_list, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(df_list)} mahasiswa ditemukan.")

    # ------------------------------------------
    # TAB 2: IMPORT MASSAL
    # ------------------------------------------
    with tab2:
        st.subheader("Registrasi Massal via File")
        st.markdown("Unggah file Excel atau CSV sesuai dengan format yang ditentukan.")
        
        with st.container(border=True):
            st.warning("⚠️ **Format Kolom Wajib:** `id`, `name`, `division`, `university`")
            file_mhs = st.file_uploader("Upload File (.csv, .xlsx)", type=["csv", "xlsx"])

            if file_mhs:
                try:
                    if file_mhs.name.endswith('.csv'):
                        df_new = pd.read_csv(file_mhs, sep=None, engine='python')
                    else:
                        df_new = pd.read_excel(file_mhs)

                    # Auto-fix column naming
                    df_new.columns = [c.strip().lower() for c in df_new.columns]

                    # Logic Perbaikan Data Menumpuk
                    if len(df_new.columns) == 1 and ',' in df_new.columns[0]:
                        header_raw = df_new.columns[0]
                        df_new = df_new[header_raw].str.split(',', expand=True)
                        df_new.columns = [c.strip().lower() for c in header_raw.split(',')]

                    st.write("**Preview Data:**")
                    st.dataframe(df_new.head(3), use_container_width=True)

                    if st.button("🚀 Proses Sinkronisasi Data", use_container_width=True, type="primary"):
                        if 'id' not in df_new.columns:
                            st.error("Kolom 'id' tidak ditemukan. Periksa kembali header file Anda.")
                        else:
                            success_count = 0
                            for _, row in df_new.iterrows():
                                s_id, s_name = int(row['id']), str(row['name'])
                                s_div, s_univ = str(row['division']), str(row['university'])

                                # DB Update
                                cur.execute("""
                                    INSERT INTO students (id, name, division, university)
                                    VALUES (%s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE name=VALUES(name), division=VALUES(division), university=VALUES(university)
                                """, (s_id, s_name, s_div, s_univ))

                                u_name = generate_username(s_name, s_id)
                                u_pass = generate_password(s_id)
                                
                                cur.execute("""
                                    INSERT INTO users (username, password, role, student_id)
                                    VALUES (%s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE username=VALUES(username)
                                """, (u_name, u_pass, "mahasiswa", s_id))
                                success_count += 1
                            
                            conn.commit()
                            st.success(f"Berhasil menyinkronkan {success_count} data ke database.")
                            st.balloons()
                            st.rerun()
                except Exception as e:
                    st.error(f"Kesalahan sistem: {e}")

    # ------------------------------------------
    # TAB 3: TAMBAH MANUAL
    # ------------------------------------------
    with tab3:
        st.subheader("Input Data Mahasiswa Baru")
        with st.form("form_manual"):
            col1, col2 = st.columns(2)
            with col1:
                nama = st.text_input("Nama Lengkap", placeholder="Masukkan nama mahasiswa")
                divisi = st.selectbox("Divisi Penempatan", ["Web Developer", "Data Science", "AI Engineer"])
            
            with col2:
                list_univ = get_list_universitas()
                pilihan_univ = st.selectbox("Asal Universitas", options=list_univ, index=None, placeholder="Pilih Kampus...")
                
                universitas = ""
                if pilihan_univ == "➕ Input Manual (Tidak ada di daftar)":
                    universitas = st.text_input("Nama Universitas (Manual)")
                else:
                    universitas = pilihan_univ

            submitted = st.form_submit_button("💾 Simpan ke Sistem", use_container_width=True)

            if submitted:
                if not nama or not universitas:
                    st.error("Mohon lengkapi semua bidang input.")
                else:
                    try:
                        cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama, divisi, universitas))
                        conn.commit()
                        s_id = cur.lastrowid
                        
                        u_name = generate_username(nama, s_id)
                        u_pass = generate_password(s_id)

                        cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", 
                                   (u_name, u_pass, "mahasiswa", s_id))
                        conn.commit()
                        
                        st.success(f"Mahasiswa {nama} berhasil didaftarkan!")
                        st.info(f"Akses Login — User: **{u_name}** | Pass: **{u_pass}**")
                    except Exception as e:
                        st.error(f"Gagal menyimpan: {e}")

    conn.close()

# Footer
st.markdown("---")
st.caption("Vinix Management System v2.0 - Dashboard Administrasi")

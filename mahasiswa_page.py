import streamlit as st
import pandas as pd
from db import get_db
import random

# ==========================================
# 1. FUNGSI UNTUK MEMBACA CSV (TAMBAHAN)
# ==========================================
@st.cache_data
def get_list_universitas():
    try:
        if file_mhs.name.endswith('.csv'):
                    # Tambahkan sep=None agar pandas otomatis mendeteksi pemisah (koma atau titik koma)
            df_new = pd.read_csv(file_mhs, sep=None, engine='python')
        else:
            df_new = pd.read_excel(file_mhs)

                # Bersihkan nama kolom dari spasi yang tidak sengaja
        df_new.columns = [c.strip().lower() for c in df_new.columns]
                
        st.write("Preview Data:")
        st.dataframe(df_new.head())

        if st.button("✅ Daftarkan Semua Mahasiswa di Atas"):
                    # Cek apakah kolom 'id' benar-benar ada
            if 'id' not in df_new.columns:
                st.error(f"Kolom 'id' tidak ditemukan. Kolom yang terbaca: {list(df_new.columns)}")
            else:
                        # ... (lanjutkan kode simpan seperti sebelumnya)
def mahasiswa_page():
    st.markdown("## 👨‍🎓 Kelola Mahasiswa")
    st.markdown("Manajemen data mahasiswa magang & studi independen")

    # ======================
    # KONEKSI DB
    # ======================
    conn = get_db()
    cur = conn.cursor()

    # ==========================================
    # [KODE BARU] IMPORT MASSAL MAHASISWA
    # ==========================================
    with st.expander("📥 Import Massal Mahasiswa (Excel/CSV)"):
        st.markdown("Gunakan fitur ini untuk mendaftarkan banyak mahasiswa sekaligus.")
        st.info("Format kolom: **id, name, division, university**")
        file_mhs = st.file_uploader("Pilih file daftar mahasiswa", type=["csv", "xlsx"], key="import_mhs_bulk")

        if file_mhs is not None:
            try:
                df_new = pd.read_csv(file_mhs) if file_mhs.name.endswith('.csv') else pd.read_excel(file_mhs)
                st.write("Preview Data:")
                st.dataframe(df_new.head())

                if st.button("✅ Daftarkan Semua Mahasiswa di Atas"):
                    success_count = 0
                    for _, row in df_new.iterrows():
                        s_id = int(row['id'])
                        s_name = str(row['name'])
                        s_div = str(row['division'])
                        s_univ = str(row['university'])

                        # 1. Masukkan ke tabel students dengan ID tetap dari Excel
                        cur.execute("""
                            INSERT INTO students (id, name, division, university)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE name=VALUES(name), division=VALUES(division), university=VALUES(university)
                        """, (s_id, s_name, s_div, s_univ))

                        # 2. Buat akun login otomatis (Username: vinix_nama)
                        u_name = f"vinix_{s_name.lower().split()[0]}_{s_id}"
                        u_pass = f"VNX-{s_id}X" # Password sederhana untuk massal
                        
                        cur.execute("""
                            INSERT INTO users (username, password, role, student_id)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE username=VALUES(username)
                        """, (u_name, u_pass, "mahasiswa", s_id))
                        success_count += 1
                    
                    conn.commit()
                    st.success(f"🚀 Berhasil mendaftarkan {success_count} mahasiswa! Angka Dashboard pasti sudah berubah.")
                    st.balloons()
                    st.rerun()
            except Exception as e:
                st.error(f"Gagal import: {e}")

    # ======================
    # TAMBAH MAHASISWA (MANUAL)
    # ======================
    st.markdown("### ➕ Tambah Mahasiswa & Akun Login")

    st.markdown('<div class="login-label">Nama Mahasiswa</div>', unsafe_allow_html=True)
    nama = st.text_input(
        "",
        placeholder="contoh: Siti Nurjanah",
        label_visibility="collapsed",
        key="input_nama" 
    )
    
    st.markdown('<div class="login-label">Divisi</div>', unsafe_allow_html=True)
    divisi = st.selectbox(
        "",
        ["Web Developer", "Data Science", "AI Engineer"],
        label_visibility="collapsed",
        key="input_divisi"
    )
    
    st.markdown('<div class="login-label">Universitas</div>', unsafe_allow_html=True)
    list_univ = get_list_universitas()
    
    pilihan_univ = st.selectbox(
        "",
        options=list_univ,
        index=None,
        placeholder="🔍 Cari dan pilih universitas...",
        label_visibility="collapsed",
        key="select_univ"
    )

    universitas = ""
    if pilihan_univ == "➕ Input Manual (Tidak ada di daftar)":
        universitas = st.text_input(
            "", 
            placeholder="Masukkan nama universitas secara manual",
            label_visibility="collapsed"
        )
    else:
        universitas = pilihan_univ

    # ======================
    # GENERATE USERNAME & PASSWORD
    # ======================
    def generate_username(nama):
        if not nama: return ""
        base = nama.lower().split()[0]
        return f"vinix_{base}"

    def generate_password(nama):
        if not nama: return ""
        prefix = nama.upper().split()[0][:3]
        angka = random.randint(1000, 9999)
        return f"VNX-{prefix}-{angka}"

    if st.button("💾 Simpan Mahasiswa"):
        if not nama or not universitas:
            st.warning("Nama dan Universitas wajib diisi")
        else:
            username = generate_username(nama)
            password = generate_password(nama)

            try:
                cur.execute("""
                    INSERT INTO students (name, division, university)
                    VALUES (%s, %s, %s)
                """, (nama, divisi, universitas))
                
                conn.commit()
                cur.execute("SELECT LAST_INSERT_ID()")
                student_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO users (username, password, role, student_id)
                    VALUES (%s, %s, %s, %s)
                """, (username, password, "mahasiswa", student_id))

                conn.commit()
                st.success("✅ Mahasiswa & akun login berhasil dibuat")
                st.info(f"👤 **Username** : `{username}` | 🔑 **Password** : `{password}`")

            except Exception as e:
                conn.rollback()
                st.error(f"Gagal menyimpan data: {e}")

    # ======================
    # DAFTAR MAHASISWA
    # ======================
    st.markdown("---")
    st.markdown("### 📋 Daftar Mahasiswa Terdaftar")

    cur.execute("""
        SELECT s.id, u.username, s.name, s.division, s.university
        FROM students s
        JOIN users u ON s.id = u.student_id
        WHERE u.role = 'mahasiswa'
        ORDER BY s.id ASC
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        st.info("Belum ada mahasiswa terdaftar.")
        return

    df = pd.DataFrame(rows, columns=["ID", "Username", "Nama", "Divisi", "Universitas"])
    df.insert(0, "No", range(1, len(df) + 1))
    st.dataframe(df[["No", "Username", "Nama", "Divisi", "Universitas"]], use_container_width=True)



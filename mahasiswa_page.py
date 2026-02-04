import streamlit as st
import pandas as pd
from db import get_db
import random

# ==========================================
# 1. FUNGSI AMBIL DAFTAR UNIVERSITAS
# ==========================================
@st.cache_data
def get_list_universitas():
    try:
        # Membaca file universitas
        df = pd.read_csv("universitas_indonesia.csv")
        list_univ = sorted(df['nama_universitas'].dropna().unique().tolist())
        list_univ.append("➕ Input Manual (Tidak ada di daftar)")
        return list_univ
    except Exception as e:
        return [f"Error baca CSV: {e}", "➕ Input Manual (Tidak ada di daftar)"]

def mahasiswa_page():
    st.markdown("## 👨‍🎓 Kelola Mahasiswa")
    st.markdown("Manajemen data mahasiswa magang & studi independen")

    conn = get_db()
    cur = conn.cursor()

    # ==========================================
    # 2. FITUR IMPORT MASSAL (SOLUSI DASHBOARD 7 -> 100+)
    # ==========================================
    with st.expander("📥 Import Massal Mahasiswa (Excel/CSV)"):
        st.markdown("Gunakan fitur ini untuk mendaftarkan banyak mahasiswa sekaligus.")
        st.info("Format kolom: **id, name, division, university**")
        file_mhs = st.file_uploader("Pilih file daftar mahasiswa", type=["csv", "xlsx"], key="import_bulk_final")

        if file_mhs is not None:
            try:
                # Membaca file & Handle Error 'id' yang menyatu (Separator Auto-detect)
                if file_mhs.name.endswith('.csv'):
                    df_new = pd.read_csv(file_mhs, sep=None, engine='python')
                else:
                    df_new = pd.read_excel(file_mhs)

                # Bersihkan nama kolom agar tidak error 'id' lagi
                df_new.columns = [c.strip().lower() for c in df_new.columns]
                
                st.write("Preview Data:")
                st.dataframe(df_new.head())

                if st.button("✅ Daftarkan Semua Mahasiswa di Atas", use_container_width=True):
                    if 'id' not in df_new.columns:
                        st.error(f"Kolom 'id' tidak ditemukan! Kolom yang terbaca: {list(df_new.columns)}")
                    else:
                        success_count = 0
                        for _, row in df_new.iterrows():
                            s_id = int(row['id'])
                            s_name = str(row['name'])
                            s_div = str(row['division'])
                            s_univ = str(row['university'])

                            # Simpan ke tabel students agar Dashboard Update
                            cur.execute("""
                                INSERT INTO students (id, name, division, university)
                                VALUES (%s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE name=VALUES(name), division=VALUES(division), university=VALUES(university)
                            """, (s_id, s_name, s_div, s_univ))

                            # Buat akun login otomatis
                            u_name = f"vinix_{s_name.lower().split()[0]}_{s_id}"
                            u_pass = f"VNX-{s_id}X"
                            
                            cur.execute("""
                                INSERT INTO users (username, password, role, student_id)
                                VALUES (%s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE username=VALUES(username)
                            """, (u_name, u_pass, "mahasiswa", s_id))
                            success_count += 1
                        
                        conn.commit()
                        st.success(f"🚀 Berhasil mendaftarkan {success_count} mahasiswa!")
                        st.balloons()
                        st.rerun()
            except Exception as e:
                st.error(f"Gagal import: {e}")

    # ==========================================
    # 3. TAMBAH MAHASISWA MANUAL
    # ==========================================
    st.markdown("### ➕ Tambah Mahasiswa Manual")
    
    nama = st.text_input("Nama Mahasiswa", placeholder="contoh: Siti Nurjanah", key="manual_nama")
    divisi = st.selectbox("Divisi", ["Web Developer", "Data Science", "AI Engineer"], key="manual_div")
    
    list_univ = get_list_universitas()
    pilihan_univ = st.selectbox("Universitas", options=list_univ, index=None, placeholder="🔍 Pilih Kampus...", key="manual_univ")

    universitas = ""
    if pilihan_univ == "➕ Input Manual (Tidak ada di daftar)":
        universitas = st.text_input("Masukkan Universitas Manual", key="manual_univ_text")
    else:
        universitas = pilihan_univ

    if st.button("💾 Simpan Mahasiswa Manual"):
        if not nama or not universitas:
            st.warning("Nama dan Universitas wajib diisi")
        else:
            try:
                cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama, divisi, universitas))
                conn.commit()
                st.success("✅ Mahasiswa berhasil disimpan secara manual!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal: {e}")

    # ==========================================
    # 4. DAFTAR MAHASISWA TERDAFTAR
    # ==========================================
    st.markdown("---")
    st.markdown("### 📋 Daftar Mahasiswa Terdaftar")
    cur.execute("SELECT id, name, division, university FROM students ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()

    if rows:
        df_list = pd.DataFrame(rows, columns=["ID", "Nama", "Divisi", "Universitas"])
        st.dataframe(df_list, use_container_width=True)
    else:
        st.info("Belum ada mahasiswa terdaftar.")

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
        # 1. Membaca file sesuai nama yang kamu upload
        df = pd.read_csv("universitas_indonesia.csv")
        
        # 2. Ambil data dari kolom 'nama_universitas' (sesuai isi filemu)
        list_univ = sorted(df['nama_universitas'].dropna().unique().tolist())
        
        # 3. Tambahkan opsi manual
        list_univ.append("➕ Input Manual (Tidak ada di daftar)")
        return list_univ
    except Exception as e:
        # Jika muncul ini di web, berarti file CSV belum terbaca oleh GitHub/Streamlit
        return [f"Error baca CSV: {e}", "➕ Input Manual (Tidak ada di daftar)"]
def mahasiswa_page():
    st.markdown("## 👨‍🎓 Kelola Mahasiswa")
    st.markdown("Manajemen data mahasiswa magang & studi independen")

    # ======================
    # KONEKSI DB
    # ======================
    conn = get_db()
    cur = conn.cursor()

    # ======================
    # TAMBAH MAHASISWA
    # ======================
    st.markdown("### ➕ Tambah Mahasiswa & Akun Login")

    st.markdown('<div class="login-label">Nama Mahasiswa</div>', unsafe_allow_html=True)
    nama = st.text_input(
        "",
        placeholder="contoh: Siti Nurjanah",
        label_visibility="collapsed",
        key="input_nama" # Tambahkan key agar unik
    )
    
    st.markdown('<div class="login-label">Divisi</div>', unsafe_allow_html=True)
    divisi = st.selectbox(
        "",
        ["Web Developer", "Data Science", "AI Engineer"],
        label_visibility="collapsed",
        key="input_divisi"
    )
    
    # ==========================================
    # 2. PERUBAHAN INPUT UNIVERSITAS (DI SINI)
    # ==========================================
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

    # Logika munculkan input manual jika pilihan "Input Manual" diklik
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
                # simpan mahasiswa (MENGGUNAKAN VARIABEL UNIVERSITAS HASIL PILIHAN/INPUT)
                cur.execute("""
                    INSERT INTO students (name, division, university)
                    VALUES (%s, %s, %s)
                """, (nama, divisi, universitas))
                
                # Gunakan lastrowid atau fetch id sesuai database kamu
                # Jika di MySQL/Postgres:
                conn.commit()
                cur.execute("SELECT LAST_INSERT_ID()")
                student_id = cur.fetchone()[0]

                # simpan akun login
                cur.execute("""
                    INSERT INTO users (username, password, role, student_id)
                    VALUES (%s, %s, %s, %s)
                """, (username, password, "mahasiswa", student_id))

                conn.commit()

                st.success("✅ Mahasiswa & akun login berhasil dibuat")

                st.info(f"""
👤 **Username** : `{username}`  
🔑 **Password** : `{password}`  

📌 Informasi ini dibagikan ke mahasiswa saat onboarding (WhatsApp).
                """)

            except Exception as e:
                conn.rollback()
                st.error(f"Gagal menyimpan data: {e}")

    # ======================
    # DAFTAR MAHASISWA
    # ======================
    st.markdown("---")
    st.markdown("### 📋 Daftar Mahasiswa Terdaftar")

    cur.execute("""
        SELECT 
            s.id,
            u.username,
            s.name,
            s.division,
            s.university
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

    df = pd.DataFrame(
        rows,
        columns=["ID", "Username", "Nama", "Divisi", "Universitas"]
    )

    df.insert(0, "No", range(1, len(df) + 1))

    st.dataframe(
        df[["No", "Username", "Nama", "Divisi", "Universitas"]],
        use_container_width=True
    )


import streamlit as st
import pandas as pd
from db import get_db
import random

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
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="login-label">Divisi</div>', unsafe_allow_html=True)
    divisi = st.selectbox(
        "",
        ["Web Developer", "Data Science", "AI Engineer"],
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="login-label">Universitas</div>', unsafe_allow_html=True)
    universitas = st.text_input(
        "",
        placeholder="contoh: Universitas Padjadjaran",
        label_visibility="collapsed"
    )

    # ======================
    # GENERATE USERNAME & PASSWORD
    # ======================
    def generate_username(nama):
        base = nama.lower().split()[0]
        return f"vinix_{base}"

    def generate_password(nama):
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
                # simpan mahasiswa
                cur.execute("""
                    INSERT INTO students (name, division, university)
                    VALUES (%s, %s, %s)
                """, (nama, divisi, universitas))
                student_id = cur.lastrowid

                # simpan akun login (USERNAME, BUKAN EMAIL)
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


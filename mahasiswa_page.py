import streamlit as st
import pandas as pd
from db import get_db

# =========================
# LOAD UNIVERSITAS DARI CSV
# =========================
def load_universitas():
    try:
        df = pd.read_csv("universitas_indonesia.csv")
        return sorted(df["nama_universitas"].dropna().unique().tolist())
    except Exception:
        return []

# =========================
# HALAMAN MAHASISWA
# =========================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa")

    menu = st.radio(
        "Pilih Menu:",
        ["📊 Mahasiswa Terdaftar", "📝 Input Mahasiswa", "📤 Unggah Data CSV"],
        horizontal=True
    )

    conn = get_db()
    cur = conn.cursor()

    # =========================
    # INPUT MAHASISWA
    # =========================
    if menu == "📝 Input Mahasiswa":
        st.header("Input Data Mahasiswa")

        # INPUT DASAR
        m_nama = st.text_input(
            "Nama Lengkap*",
            placeholder="Contoh: Ahmad Budi"
        )

        m_div = st.selectbox(
            "Divisi*",
            ["Pilih Divisi", "Data Science", "Web Development", "AI Engineer"]
        )

        # =========================
        # UNIVERSITAS (CSV + OTHER)
        # =========================
        st.markdown("**Asal Universitas***")

        universitas_list = load_universitas()
        universitas_options = universitas_list + ["Other / Lainnya"]

        selected_univ = st.selectbox(
            "Pilih Universitas",
            universitas_options
        )

        manual_univ = ""
        if selected_univ == "Other / Lainnya":
            manual_univ = st.text_input(
                "Masukkan nama universitas",
                placeholder="Contoh: Universitas ABC"
            )

        final_univ = (
            manual_univ.strip()
            if selected_univ == "Other / Lainnya"
            else selected_univ
        )

        st.caption("*Wajib diisi")

        # =========================
        # SIMPAN DATA
        # =========================
        if st.button("💾 Simpan Data", type="primary"):
            if not m_nama:
                st.error("Nama Lengkap wajib diisi!")
            elif m_div == "Pilih Divisi":
                st.error("Divisi wajib dipilih!")
            elif not final_univ:
                st.error("Asal Universitas wajib diisi!")
            else:
                try:
                    # INSERT STUDENT (ID AUTO)
                    cur.execute(
                        "INSERT INTO students (name, division, university) VALUES (%s, %s, %s)",
                        (m_nama.strip(), m_div, final_univ.title())
                    )

                    student_id = cur.lastrowid

                    # GENERATE AKUN
                    nama_clean = m_nama.lower().split()[0]
                    username = f"vinix_{nama_clean}_{student_id}"
                    password = f"VNX-{student_id}X"

                    cur.execute(
                        "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)",
                        (username, password, "mahasiswa", student_id)
                    )

                    conn.commit()

                    st.success("✅ Data mahasiswa berhasil disimpan!")
                    st.info(f"**ID Mahasiswa:** {student_id}")
                    st.info(f"**Username:** {username}")
                    st.info(f"**Password:** {password}")

                except Exception as e:
                    st.error(f"Gagal menyimpan data: {e}")

    # =========================
    # DATA MAHASISWA
    # =========================
    elif menu == "📤 Unggah Data CSV":
        st.header("Unggah Data CSV Mahasiswa")
    
        uploaded_file = st.file_uploader(
            "Pilih file CSV",
            type=["csv"]
        )
    
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
    
                st.write("Preview Data:")
                st.dataframe(df.head(), use_container_width=True)
    
                if st.button("💾 Simpan Semua Data", type="primary"):
                    success, failed = 0, 0
    
                    for _, row in df.iterrows():
                        try:
                            name = str(row.get("name", "")).strip()
                            division = str(row.get("division", "")).strip()
                            university = str(row.get("university", "")).strip()
    
                            if name and division and university:
                                cur.execute(
                                    "INSERT INTO students (name, division, university) VALUES (%s, %s, %s)",
                                    (name, division, university)
                                )
    
                                student_id = cur.lastrowid
                                username = f"vinix_{name.lower().split()[0]}_{student_id}"
                                password = f"VNX-{student_id}X"
    
                                cur.execute(
                                    "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)",
                                    (username, password, "mahasiswa", student_id)
                                )
    
                                success += 1
                            else:
                                failed += 1
                        except:
                            failed += 1
    
                    conn.commit()
    
                    st.success(f"✅ {success} data berhasil disimpan")
                    if failed:
                        st.warning(f"⚠️ {failed} data gagal disimpan")
    
            except Exception as e:
                st.error(f"Gagal membaca file CSV: {e}")
    

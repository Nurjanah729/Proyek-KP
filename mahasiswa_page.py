import streamlit as st
import pandas as pd
from db import get_db

# ===============================
# LOAD UNIVERSITAS DARI CSV
# ===============================
@st.cache_data
def load_universitas():
    df = pd.read_csv("universitas_indonesia.csv")
    return df["universitas"].dropna().tolist()

# ===============================
# GENERATE AKUN
# ===============================
def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ===============================
# HALAMAN MAHASISWA
# ===============================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Administrasi Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    tab_list, tab_import, tab_manual = st.tabs([
        "📊 Database Utama",
        "📤 Registrasi Kolektif",
        "➕ Pendaftaran Manual"
    ])

    # ===============================
    # TAB 3: PENDAFTARAN MANUAL
    # ===============================
    with tab_manual:
        st.write("### Registrasi Mahasiswa Baru")

        col1, col2 = st.columns(2)

        # ===== KOLOM KIRI =====
        with col1:
            st.markdown("**Nama Lengkap**")
            nama_m = st.text_input(
                "",
                placeholder="Masukkan nama lengkap",
                key="in_nama"
            )

            st.markdown("**Divisi**")
            div_m = st.selectbox(
                "",
                ["Web Developer", "Data Science", "AI Engineer"],
                key="in_div"
            )

        # ===== KOLOM KANAN =====
        with col2:
            st.markdown("**Universitas**")

            list_univ = load_universitas()
            list_univ.append("➕ Input Manual")

            univ_p = st.selectbox(
                "",
                options=list_univ,
                index=None,
                placeholder="Pilih Universitas",
                key="in_univ_s"
            )

            if univ_p == "➕ Input Manual":
                st.markdown("**Nama Universitas**")
                univ_m = st.text_input(
                    "",
                    placeholder="Ketik nama universitas",
                    key="in_univ_t"
                )
            else:
                univ_m = univ_p

        st.markdown("<br>", unsafe_allow_html=True)

        # ===== SIMPAN =====
        if st.button("Simpan ke Database", key="in_save"):
            if nama_m and div_m and univ_m:
                try:
                    cur.execute(
                        "INSERT INTO students (name, division, university) VALUES (%s, %s, %s)",
                        (nama_m, div_m, univ_m)
                    )
                    conn.commit()

                    new_id = cur.lastrowid
                    u, p = generate_credentials(nama_m, new_id)

                    cur.execute(
                        "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)",
                        (u, p, "mahasiswa", new_id)
                    )
                    conn.commit()

                    st.success(f"✅ Berhasil!\n\nUsername: **{u}**  \nPassword: **{p}**")

                except Exception as e:
                    st.error(f"❌ Database Error: {e}")
            else:
                st.warning("⚠️ Mohon lengkapi semua data.")

    conn.close()

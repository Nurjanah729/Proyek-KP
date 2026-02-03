import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_db


def mahasiswa_dashboard(student_id):

    # ======================
    # INIT PAGE
    # ======================
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    # ======================
    # SIDEBAR (SATU KALI SAJA)
    # ======================
    with st.sidebar:
        st.markdown("## 🎓 Mahasiswa")

        if st.button("🏠 Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

        if st.button("⚙️ Pengaturan Akun"):
            st.session_state.page = "pengaturan"
            st.rerun()

        if st.button("🔓 Logout"):
            st.session_state.clear()
            st.rerun()

    # ==================================================
    # =============== HALAMAN PENGATURAN ===============
    # ==================================================
    if st.session_state.page == "pengaturan":
        st.markdown("## ⚙️ Pengaturan Akun")
        st.caption("Ubah username dan password")

        with st.form("form_pengaturan"):
            st.text("Username Baru")
            username_baru = st.text_input(" ", key="username")

            st.text("Password Lama")
            password_lama = st.text_input("  ", type="password", key="pass_lama")

            st.text("Password Baru")
            password_baru = st.text_input("   ", type="password", key="pass_baru")

            simpan = st.form_submit_button("💾 Simpan Perubahan")

        if simpan:
            if not username_baru or not password_lama or not password_baru:
                st.error("Semua field wajib diisi")
            else:
                conn = get_db()
                cur = conn.cursor()

                cur.execute(
                    "SELECT password FROM students WHERE id = %s",
                    (student_id,)
                )
                data = cur.fetchone()

                if not data:
                    st.error("Akun tidak ditemukan")
                elif data[0] != password_lama:
                    st.error("Password lama salah")
                else:
                    cur.execute("""
                        UPDATE students
                        SET username = %s, password = %s
                        WHERE id = %s
                    """, (username_baru, password_baru, student_id))
                    conn.commit()
                    st.success("✅ Akun berhasil diperbarui")

                conn.close()

        st.markdown("---")
        if st.button("⬅️ Kembali ke Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

        return  # ⛔ STOP DI SINI (dashboard tidak dirender)

    # ==================================================
    # ================= HALAMAN DASHBOARD ==============
    # ==================================================
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, division, university
        FROM students
        WHERE id = %s
    """, (student_id,))
    mahasiswa = cur.fetchone()

    if not mahasiswa:
        st.error("Data mahasiswa tidak ditemukan")
        conn.close()
        return

    nama, divisi, universitas = mahasiswa

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0B3C8C, #1E40AF);
        padding: 25px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;">
        <h2>🎓 Selamat Datang, {nama}</h2>
        <p><b>Divisi:</b> {divisi}</p>
        <p><b>Universitas:</b> {universitas}</p>
    </div>
    """, unsafe_allow_html=True)

    cur.execute("""
        SELECT module, score
        FROM module_scores
        WHERE student_id = %s
        ORDER BY CAST(module AS UNSIGNED)
    """, (student_id,))
    data_nilai = cur.fetchall()
    conn.close()

    if not data_nilai:
        st.warning("Nilai modul belum tersedia")
        return

    df = pd.DataFrame(data_nilai, columns=["Modul", "Nilai"])
    df["Modul"] = df["Modul"].astype(int)

    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Rata-rata", f"{df['Nilai'].mean():.2f}")
    col2.metric("⬆️ Tertinggi", df["Nilai"].max())
    col3.metric("⬇️ Terendah", df["Nilai"].min())

    st.markdown("### 📈 Grafik Nilai")
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.plot(df["Modul"], df["Nilai"], marker="o")
    ax.set_ylim(0, 100)
    ax.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig)

    st.markdown("### 📋 Detail Nilai")
    st.dataframe(df, use_container_width=True)

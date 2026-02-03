import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_db
from pengaturan import pengaturan_page  # import fungsi pengaturan


def mahasiswa_dashboard(student_id):

    # ======================
    # SIDEBAR
    # ======================
    with st.sidebar:
        st.markdown("## 🎓 Mahasiswa")
        st.markdown("Dashboard Akademik")
        st.markdown("---")

        # Menu navigasi
        page = st.radio("Menu", ["Dashboard", "Pengaturan"])
        
        if st.button("🔓 Logout"):
            st.session_state.clear()
            st.rerun()

    if page == "Pengaturan":
        pengaturan_page(student_id)
        return  # berhenti di sini, jangan render dashboard

    # ======================
    # DATABASE
    # ======================
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

    st.markdown("""
    <style>
    .welcome-container {
        background: linear-gradient(135deg, #0B3C8C, #1E40AF);
        padding: 28px;
        border-radius: 18px;
        color: white;
        box-shadow: 0 10px 30px rgba(11, 60, 140, 0.35);
        margin-bottom: 30px;
    }
    .welcome-container p { margin: 4px 0; }
    .welcome-quote {
        margin-top: 12px;
        color: #E5E7EB;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="welcome-container">
        <h2>🎓 Selamat Datang, {nama}</h2>
        <p><b>Divisi:</b> {divisi}</p>
        <p><b>Universitas:</b> {universitas}</p>
        <p class="welcome-quote">
            "Belajar hari ini adalah investasi masa depan."
        </p>
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

    # ======================
    # RINGKASAN
    # ======================
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Rata-rata Nilai", f"{df['Nilai'].mean():.2f}")
    col2.metric("⬆️ Nilai Tertinggi", df["Nilai"].max())
    col3.metric("⬇️ Nilai Terendah", df["Nilai"].min())

    # ======================
    # GRAFIK
    # ======================
    st.markdown("### 📈 Performa Nilai Modul")
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.plot(df["Modul"], df["Nilai"], marker="o", linewidth=2, color="#2563eb")
    ax.set_ylim(0, 100)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    st.pyplot(fig)

    # ======================
    # MODUL LEMAH (SATU-SATUNYA DEFINISI)
    # ======================
    modul_lemah = df[df["Nilai"] < 70]

    # ======================
    # STATUS AKADEMIK (CARD PUTIH)
    # ======================
    st.markdown("## 🎯 Status Akademik")

    if modul_lemah.empty:
        st.markdown("""
        <div class="mhs-card">
            <b>Status Akademik:</b> <span style="color:#16a34a;">Memenuhi Syarat</span><br><br>
            Semua nilai modul kamu sudah berada di atas standar minimal (70).  
            Kamu sudah berada di jalur yang baik, pertahankan konsistensi belajarmu.
        </div>
    """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="mhs-card" style="background:#FFF7ED;">
            <b>Status Akademik:</b> <span style="color:#EA580C;">Perlu Perbaikan</span><br><br>
            Terdapat <b>{len(modul_lemah)} modul</b> dengan nilai di bawah standar (70).  
            Nilai tersebut perlu diperbaiki agar proses akademik kamu dapat berlanjut dengan optimal.
        </div>
        """, unsafe_allow_html=True)


    # ======================
    # REKOMENDASI SISTEM (DALAM CARD)
    # ======================
    st.markdown("## 🧠 Rekomendasi Sistem")

    if modul_lemah.empty:
        st.info(
            "✅ **Keputusan Sistem**\n\n"
            "Seluruh nilai modul kamu sudah memenuhi standar.\n\n"
            "Kamu **sudah diperbolehkan melanjutkan ke Project Akhir**.\n\n"
            "Tetap jaga konsistensi belajar agar hasil tetap optimal."
        )

    else:
        st.info(
            "📌 **Keputusan Sistem**\n\n"
            "Saat ini kamu **belum disarankan** untuk melanjutkan ke **Project Akhir**.\n\n"
            "Hal ini karena masih terdapat modul dengan nilai di bawah standar.\n\n"
            "**Modul yang perlu diperbaiki:**"
        )

        for _, row in modul_lemah.iterrows():
            st.markdown(f"- **Modul {row['Modul']}** (Nilai {row['Nilai']})")

        st.markdown(
            "\nSetelah nilai modul tersebut memenuhi standar (≥ 70), "
            "kamu dapat melanjutkan ke tahap **Project Akhir**."
        )



    # ======================
    # TABEL (PUTIH)
    # ======================
    st.markdown("### 📋 Detail Nilai Modul")
    st.dataframe(df, use_container_width=True)


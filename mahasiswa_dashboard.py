import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_db
from pengaturan import pengaturan_page
from db import get_latest_prediction


def mahasiswa_dashboard(student_id):
    prediction = get_latest_prediction(student_id)


    # ======================
    # SIDEBAR
    # ======================
    with st.sidebar:
        st.markdown("## 🎓 Mahasiswa")
        st.markdown("Dashboard Akademik")
        st.markdown("---")

        page = st.radio("Menu", ["Dashboard", "Pengaturan"])
        
        if st.button("🔓 Logout"):
            st.session_state.clear()
            st.rerun()

    if page == "Pengaturan":
        conn = get_db()
        pengaturan_page(student_id, conn)
        conn.close()
        return

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
        cur.close()
        conn.close()
        return

    nama, divisi, universitas = mahasiswa

    kamus_modul = {
        "Data Science": {
            1: "Introduction to Data Science", 2: "Python for Data Analysis",
            3: "Exploratory Data Analysis", 4: "Statistics for DS",
            5: "Machine Learning Basics", 6: "Supervised Learning",
            7: "Unsupervised Learning", 8: "Deep Learning Intro",
            9: "Big Data Fundamentals", 10: "Model Deployment & MLOps"
        },
        "Web Development": {
            1: "HTML & CSS Dasar", 2: "Javascript ES6",
            3: "Responsive Design", 4: "Git & Version Control",
            5: "React.js Framework", 6: "Node.js Backend",
            7: "Database SQL", 8: "REST API",
            9: "Web Security", 10: "Cloud Hosting & Testing"
        },
        "AI Engineer": {
            1: "Linear Algebra for AI", 2: "Advanced Python AI",
            3: "Search Algorithms", 4: "Neural Networks",
            5: "Computer Vision", 6: "Natural Language Processing",
            7: "Reinforcement Learning", 8: "AI Model Deployment",
            9: "Generative AI Intro", 10: "AI Ethics & Governance"
        }
    }

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
    .mhs-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        margin-bottom: 20px;
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

    cur.close()
    conn.close()

    if not data_nilai:
        st.warning("Nilai modul belum tersedia")
        return

    df = pd.DataFrame(data_nilai, columns=["Modul", "Nilai"])
    df["Modul"] = df["Modul"].astype(int)

    judul_sesuai_divisi = kamus_modul.get(divisi, {})
    df["Keterangan"] = df["Modul"].map(judul_sesuai_divisi)
    df["Keterangan"] = df["Keterangan"].fillna("Materi Pelatihan Tambahan")
    df = df[["Modul", "Keterangan", "Nilai"]]

    df_display = df.copy()  # FIX PENTING

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
    st.pyplot(fig)

    modul_lemah = df[df["Nilai"] < 70]

    # ======================
    # STATUS AKADEMIK
    # ======================
    st.markdown("## 🎓 Status Akademik")

    if prediction:
        status = prediction["result"]
    
        if status == "Excellent":
            color = "#16a34a"
            emoji = "🏆"
            desc = "Performa akademik sangat baik"
        else:
            color = "#f59e0b"
            emoji = "👍"
            desc = "Performa akademik baik"
    
        st.markdown(f"""
        <div style="
            background-color:{color};
            padding:22px;
            border-radius:16px;
            color:white;
            text-align:center;
            box-shadow:0 12px 30px rgba(0,0,0,0.25);
            margin-top:10px;
        ">
            <h2 style="margin:0;">{emoji} {status}</h2>
            <p style="margin-top:8px;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ Status akademik belum dianalisis oleh admin.")
    

    # ======================
    # REKOMENDASI SISTEM
    # ======================
    st.markdown("## 🧠 Rekomendasi Sistem")

    if modul_lemah.empty:
        st.info(
            "Seluruh nilai modul kamu sudah memenuhi standar.\n\n"
            "Kamu **sudah diperbolehkan melanjutkan ke Project Akhir**."
        )
    else:
        st.info(
            "Kamu **belum disarankan** melanjutkan ke **Project Akhir**.\n\n"
            "**Modul yang perlu diperbaiki:**"
        )
        for _, row in modul_lemah.iterrows():
            st.markdown(f"- **Modul {row['Modul']}** (Nilai {row['Nilai']})")

    # ======================
    # TABEL + EXPORT
    # ======================
    st.markdown("### 📋 Detail Nilai Modul")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    col1 = st.columns(1)[0]


    with col1:
        csv = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Nilai",
            csv,
            f"Nilai_{nama.replace(' ', '_')}.csv",
            "text/csv",
            type="primary"
        )

    



import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_db
from pengaturan import pengaturan_page

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
        conn = get_db()  # ambil koneksi
        pengaturan_page(student_id, conn)  # kirim 2 argumen
        conn.close()
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
        cur.close()
        conn.close()
        return

    nama, divisi, universitas = mahasiswa

    # --- STEP 1: Judul Modul per Divisi ---
    kamus_modul = {
        "Data Science": {
            1: "Introduction to Data Science", 2: "Python for Data Analysis",
            3: "Exploratory Data Analysis", 4: "Statistics for DS",
            5: "Machine Learning Basics", 6: "Supervised Learning",
            7: "Unsupervised Learning", 8: "Deep Learning Intro",
            9: "Big Data Fundamentals", 10: "Model Deployment & MLOps"
        },
        "Web Development": {  # Sesuai dengan database
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
    @media print {
        .stButton, .stDownloadButton, [data-testid="stSidebar"] {
            display: none !important;
        }
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

    # --- LOGIKA PENYUSUNAN TABEL ---
    df = pd.DataFrame(data_nilai, columns=["Modul", "Nilai"])
    df["Modul"] = df["Modul"].astype(int)
    
    # Mapping keterangan berdasarkan divisi
    judul_sesuai_divisi = kamus_modul.get(divisi, {})
    df["Keterangan"] = df["Modul"].map(judul_sesuai_divisi)
    df["Keterangan"] = df["Keterangan"].fillna("Materi Pelatihan Tambahan")
    
    # Reorder kolom
    df = df[["Modul", "Keterangan", "Nilai"]]

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
    # MODUL LEMAH
    # ======================
    modul_lemah = df[df["Nilai"] < 70]

    # ======================
    # STATUS AKADEMIK
    # ======================
    st.markdown("## 🎯 Status Akademik")

    if modul_lemah.empty:
        st.markdown("""
        <div style="background:white; padding:20px; border-radius:10px; border-left:5px solid #16a34a; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <b>Status Akademik:</b> <span style="color:#16a34a;">Memenuhi Syarat</span><br><br>
            Semua nilai modul kamu sudah berada di atas standar minimal (70).  
            Kamu sudah berada di jalur yang baik, pertahankan konsistensi belajarmu.
        </div>
    """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#FFF7ED; padding:20px; border-radius:10px; border-left:5px solid #EA580C; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <b>Status Akademik:</b> <span style="color:#EA580C;">Perlu Perbaikan</span><br><br>
            Terdapat <b>{len(modul_lemah)} modul</b> dengan nilai di bawah standar (70).  
            Nilai tersebut perlu diperbaiki agar proses akademik kamu dapat berlanjut dengan optimal.
        </div>
        """, unsafe_allow_html=True)

    # ======================
    # REKOMENDASI SISTEM
    # ======================
    st.markdown("## 🧠 Rekomendasi Sistem")
    if modul_lemah.empty:
        st.info("✅ **Keputusan Sistem**: Kamu diperbolehkan melanjutkan ke **Project Akhir**.")
    else:
        st.warning("📌 **Keputusan Sistem**: Kamu belum disarankan ke Project Akhir. Perbaiki modul yang merah.")

    # ======================
    # TABEL & FITUR EKSPOR
    # ======================
    st.markdown("### 📋 Detail Nilai Modul")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    col_dl1, col_dl2 = st.columns([1, 4])
    with col_dl1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f'Nilai_{nama.replace(" ", "_")}.csv',
            mime='text/csv',
            type="primary"
        )
        
    with col_dl2:
        if st.button("🖨️ Cetak / Simpan PDF"):
            st.info("💡 Gunakan **Ctrl + P** untuk menyimpan sebagai PDF.")
            st.components.v1.html("<script>window.print();</script>", height=0)

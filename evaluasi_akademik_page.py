import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_db
from ml_model import run_analysis

def evaluasi_akademik_page():
    # Style agar tampilan dashboard terlihat premium dan bersih
    st.markdown("""
        <style>
        div[data-testid="stMetricValue"] { color: #FFCC00 !important; font-size: 28px; }
        .stDataFrame { border: 1px solid #E2E8F0; border-radius: 10px; }
        h1, h2, h3 { color: #0B3C8C !important; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📑 Laporan Evaluasi Akademik")
    st.write("Analisis Kesiapan Proyek Akhir Berbasis Machine Learning - PT Vinix Seven Aurum")
    st.divider()

    conn = get_db()
    # Mengambil data mahasiswa dan nilai menggunakan JOIN
    query = "SELECT s.id, s.name, m.module, m.score FROM students s LEFT JOIN module_scores m ON s.id = m.student_id"
    df_raw = pd.read_sql(query, conn)

    if df_raw.empty or df_raw['module'].isnull().all():
        st.info("ℹ️ Belum ada data nilai yang tersedia untuk diproses.")
        conn.close()
        return

    summary_list = []
    # Memproses tiap mahasiswa secara unik
    for student_id in df_raw['id'].unique():
        student_name = df_raw[df_raw['id'] == student_id]['name'].iloc[0]
        student_scores = df_raw[df_raw['id'] == student_id][['module', 'score']].dropna()
        
        if not student_scores.empty:
            student_scores.columns = ['Modul', 'Nilai']
            
            # Memanggil fungsi analisis Random Forest dari ml_model.py
            prediction, confidence, weak_mods, avg_score = run_analysis(student_scores)
            
            # Penentuan Rekomendasi Sistem (Logika sesuai Bab I)
            rekomendasi = "✅ Siap Lanjut Proyek" if prediction in ["Sangat Baik", "Baik"] else "⚠️ Perlu Bimbingan"
            
            summary_list.append({
                "Nama Mahasiswa": student_name, 
                "Rata-rata Nilai": avg_score,
                "Klasifikasi AI": prediction, 
                "Rekomendasi Sistem": rekomendasi, 
                "Modul Perlu Perbaikan": ", ".join(map(str, weak_mods)) if weak_mods else "Optimal"
            })

    df_final = pd.DataFrame(summary_list)

    # ==========================================
    # BAGIAN ATAS (METRICS SESUAI PERMINTAAN)
    # ==========================================
    col1, col2, col3 = st.columns(3)
    
    # 1. Data mahasiswa terproses
    col1.metric("Data Mahasiswa Terproses", f"{len(df_final)} Orang")
    
    # 2. Kesiapan proyek akhir (Persentase)
    siap = len(df_final[df_final["Rekomendasi Sistem"] == "✅ Siap Lanjut Proyek"])
    persen_siap = int((siap/len(df_final))*100) if len(df_final) > 0 else 0
    col2.metric("Kesiapan Proyek Akhir", f"{persen_siap}%")
    
    # Rerata Kolektif (Sebagai pembanding)
    col3.metric("Rerata Nilai Angkatan", round(df_final["Rata-rata Nilai"].mean(), 1))

    st.divider()

    # ==========================================
    # BAGIAN TABEL (SESUAI PERMINTAAN)
    # ==========================================
    st.subheader("📋 Rekapitulasi Penilaian AI")
    # Menampilkan tabel dengan kolom yang sudah disesuaikan
    st.dataframe(df_final, use_container_width=True, hide_index=True)

    # ==========================================
    # VISUALISASI PENDUKUNG
    # ==========================================
    st.subheader("📊 Distribusi Kesiapan")
    counts = df_final['Rekomendasi Sistem'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 2))
    counts.plot(kind='barh', color=['#0B3C8C', '#FFD84D'], ax=ax)
    ax.set_xlabel("Jumlah Mahasiswa")
    st.pyplot(fig)

    conn.close()

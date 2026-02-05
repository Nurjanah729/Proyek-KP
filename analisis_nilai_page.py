import streamlit as st
import pandas as pd
from db import get_db
from ml_model import run_analysis # Memanggil model Random Forest Anda

def analisis_nilai_admin():
    st.title("📊 Laporan Kelulusan & Performa Global")
    st.write("Hasil analisis Machine Learning untuk penentuan kelayakan Project Akhir.")
    st.divider()

    conn = get_db()
    
    # 1. Ambil semua data mahasiswa
    query_students = "SELECT id, name FROM students"
    df_students = pd.read_sql(query_students, conn)

    if df_students.empty:
        st.warning("⚠️ Belum ada data mahasiswa.")
        return

    summary_data = []

    # 2. Proses Analisis untuk Setiap Mahasiswa
    for _, student in df_students.iterrows():
        s_id = student['id']
        s_name = student['name']

        # Ambil nilai modul mahasiswa tersebut
        query_scores = f"SELECT module as Modul, score as Nilai FROM module_scores WHERE student_id = {s_id}"
        df_scores = pd.read_sql(query_scores, conn)

        if not df_scores.empty:
            # Jalankan Model Random Forest
            prediction, confidence, weak_mods, avg_score = run_analysis(df_scores)
            
            # Tentukan Status Kelayakan (Logika Bisnis sesuai Bab I)
            status_proyek = "✅ LAYAK" if prediction in ["Sangat Baik", "Baik"] else "⚠️ REVISI/REMEDIAL"
            
            summary_data.append({
                "Nama Mahasiswa": s_name,
                "Rata-rata": avg_score,
                "Prediksi AI": prediction,
                "Kepastian": f"{int(confidence*100)}%",
                "Status Project Akhir": status_proyek,
                "Modul Lemah": ", ".join(map(str, weak_mods)) if weak_mods else "-"
            })

    if summary_data:
        df_summary = pd.DataFrame(summary_data)

        # 3. Tampilkan Tabel Ringkasan (Monitoring Global)
        st.subheader("📋 Tabel Rekomendasi Kelayakan")
        st.dataframe(df_summary, use_container_width=True)

        # 4. Statistik Singkat untuk Manajemen PT Vinix
        col1, col2 = st.columns(2)
        with col1:
            total_layak = len(df_summary[df_summary["Status Project Akhir"] == "✅ LAYAK"])
            st.metric("Total Mahasiswa Layak", f"{total_layak} Orang")
        with col2:
            avg_kelas = round(df_summary["Rata-rata"].mean(), 2)
            st.metric("Rata-rata Kelas", avg_kelas)

    else:
        st.info("💡 Belum ada data nilai yang diinput untuk dianalisis.")

    conn.close()

if __name__ == "__main__":
    analisis_nilai_admin()

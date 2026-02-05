import streamlit as st
import pandas as pd
import plotly.express as px # Pastikan sudah install: pip install plotly
from db import get_db
from ml_model import run_analysis

def analisis_nilai_admin():
    # ==========================================
    # 1. UI CUSTOMIZATION (Sesuai Dashboard Mahasiswa)
    # ==========================================
    st.markdown("""
        <style>
        .main { background-color: #0E1117; }
        div[data-testid="stMetricValue"] { color: #FFCC00; font-size: 30px; }
        .stDataFrame { border: 1px solid #FFCC00; border-radius: 10px; }
        h1, h2, h3 { color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏛️ Dashboard Analisis Akademik (Admin)")
    st.write("Sistem Pendukung Keputusan Kelayakan Project Akhir - PT Vinix Seven Aurum")
    st.divider()

    conn = get_db()
    
    # Ambil data mahasiswa & nilai
    query = """
        SELECT s.id, s.name, m.module, m.score 
        FROM students s
        LEFT JOIN module_scores m ON s.id = m.student_id
    """
    df_raw = pd.read_sql(query, conn)

    if df_raw.empty or df_raw['module'].isnull().all():
        st.warning("⚠️ Belum ada data nilai yang tersedia untuk dianalisis.")
        conn.close()
        return

    # ==========================================
    # 2. PENGOLAHAN DATA DENGAN MACHINE LEARNING
    # ==========================================
    summary_list = []
    
    # Loop per mahasiswa untuk analisis Random Forest
    for student_id in df_raw['id'].unique():
        student_name = df_raw[df_raw['id'] == student_id]['name'].iloc[0]
        student_scores = df_raw[df_raw['id'] == student_id][['module', 'score']].dropna()
        
        if not student_scores.empty:
            # Ubah kolom agar sesuai fungsi run_analysis (Modul, Nilai)
            student_scores.columns = ['Modul', 'Nilai']
            
            # Eksekusi Model Random Forest
            prediction, confidence, weak_mods, avg_score = run_analysis(student_scores)
            
            # Logika Kelayakan (Sesuai Bab I: Mendukung Pengambilan Keputusan)
            status = "✅ LAYAK" if prediction in ["Sangat Baik", "Baik"] else "⚠️ REVISI"
            
            summary_list.append({
                "Nama Mahasiswa": student_name,
                "Rata-rata": avg_score,
                "Prediksi Performa": prediction,
                "Akurasi AI": f"{int(confidence*100)}%",
                "Rekomendasi": status,
                "Modul Lemah": ", ".join(map(str, weak_mods)) if weak_mods else "Tidak ada"
            })

    df_final = pd.DataFrame(summary_list)

    # ==========================================
    # 3. INTERFACE: METRICS & VISUALISASI
    # ==========================================
    # Baris 1: Ringkasan Angka
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Mahasiswa", len(df_final))
    with m2:
        layak_count = len(df_final[df_final["Rekomendasi"] == "✅ LAYAK"])
        st.metric("Layak Proyek Akhir", f"{layak_count} Orang")
    with m3:
        avg_class = round(df_final["Rata-rata"].mean(), 1)
        st.metric("Rata-rata Kelas", avg_class)

    st.divider()

    # Baris 2: Tabel & Grafik
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📋 Daftar Analisis Performa")
        # Styling baris berdasarkan status
        st.dataframe(df_final, use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("📊 Distribusi Hasil")
        fig = px.pie(df_final, names='Prediksi Performa', 
                     color='Prediksi Performa',
                     color_discrete_map={'Sangat Baik':'#00CC96', 'Baik':'#636EFA', 'Cukup':'#FECB52', 'Kurang':'#EF553B'},
                     hole=0.4)
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # 4. MODUL KRITIS (Insight untuk Admin)
    # ==========================================
    st.divider()
    st.subheader("💡 Insight untuk Manajemen")
    
    # Hitung modul yang paling sering muncul di 'Modul Lemah'
    all_weak = []
    for m in df_final["Modul Lemah"]:
        if m != "Tidak ada":
            all_weak.extend(m.split(", "))
    
    if all_weak:
        most_common_weak = max(set(all_weak), key=all_weak.count)
        st.error(f"**Peringatan:** Modul {most_common_weak} merupakan modul dengan kendala terbanyak di angkatan ini. Disarankan melakukan evaluasi materi.")
    else:
        st.success("**Luar Biasa:** Tidak ditemukan modul kritis. Performa akademik stabil.")

    conn.close()

if __name__ == "__main__":
    analisis_nilai_admin()

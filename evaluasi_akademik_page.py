import streamlit as st
import pandas as pd
import plotly.express as px # Menggunakan Plotly untuk Grafik Donat
from db import get_db
from ml_model import run_analysis

def evaluasi_akademik_page():
    # Style Dashboard
    st.markdown("""
        <style>
        div[data-testid="stMetricValue"] { color: #FFCC00 !important; font-size: 28px; }
        .stDataFrame { border: 1px solid #E2E8F0; border-radius: 10px; }
        h1, h2, h3 { color: #0B3C8C !important; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📑 Laporan Evaluasi Akademik")
    st.write("Analisis Performa Mahasiswa Berbasis Machine Learning - PT Vinix Seven Aurum")
    st.divider()

    conn = get_db()
    query = "SELECT s.id, s.name, m.module, m.score FROM students s LEFT JOIN module_scores m ON s.id = m.student_id"
    df_raw = pd.read_sql(query, conn)

    if df_raw.empty or df_raw['module'].isnull().all():
        st.info("ℹ️ Belum ada data nilai yang tersedia untuk diproses.")
        conn.close()
        return

    summary_list = []
    for student_id in df_raw['id'].unique():
        student_name = df_raw[df_raw['id'] == student_id]['name'].iloc[0]
        student_scores = df_raw[df_raw['id'] == student_id][['module', 'score']].dropna()
        
        if not student_scores.empty:
            student_scores.columns = ['Modul', 'Nilai']
            
            # Memanggil fungsi analisis Random Forest
            prediction, confidence, weak_mods, avg_score = run_analysis(student_scores)
            
            # Menyimpan data sesuai permintaan tabel (Hanya 3 kolom)
            summary_list.append({
                "Nama Mahasiswa": student_name, 
                "Rata-rata Nilai": avg_score,
                "Hasil Analisis": prediction # Menggunakan Label ML asli: Sangat Baik, Baik, dsb.
            })

    df_final = pd.DataFrame(summary_list)

    # ==========================================
    # BAGIAN ATAS (METRICS)
    # ==========================================
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Data Mahasiswa Terproses", f"{len(df_final)} Orang")
    
    # Kesiapan Proyek Akhir (Berdasarkan label Sangat Baik & Baik)
    siap = len(df_final[df_final["Hasil Analisis"].isin(["Sangat Baik", "Baik"])])
    persen_siap = int((siap/len(df_final))*100) if len(df_final) > 0 else 0
    col2.metric("Kesiapan Proyek Akhir", f"{persen_siap}%")
    
    col3.metric("Rerata Nilai Angkatan", round(df_final["Rata-rata Nilai"].mean(), 1))

    st.divider()

    # ==========================================
    # BAGIAN TABEL & GRAFIK DONUT
    # ==========================================
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.subheader("📋 Ringkasan Hasil Evaluasi")
        st.dataframe(df_final, use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("📊 Distribusi Performa")
        # Membuat Grafik Donat menggunakan Plotly
        fig = px.pie(
            df_final, 
            names='Hasil Analisis', 
            hole=0.5,
            color='Hasil Analisis',
            color_discrete_map={
                'Sangat Baik': '#00CC96', 
                'Baik': '#636EFA', 
                'Cukup': '#FECB52', 
                'Kurang': '#EF553B'
            }
        )
        fig.update_layout(
            showlegend=True, 
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)

    conn.close()

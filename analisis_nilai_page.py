import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_db
from ml_model import run_analysis

def evaluasi_akademik_page():
    # ==========================================
    # UI STYLING
    # ==========================================
    st.markdown("""
        <style>
        div[data-testid="stMetricValue"] { color: #FFCC00 !important; font-size: 28px; }
        .stDataFrame { border: 1px solid #333; border-radius: 8px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📑 Laporan Evaluasi Akademik")
    st.write("Sistem Pendukung Keputusan Berbasis Machine Learning - PT Vinix Seven Aurum")
    st.divider()

    conn = get_db()
    
    query = """
        SELECT s.id, s.name, m.module, m.score 
        FROM students s
        LEFT JOIN module_scores m ON s.id = m.student_id
    """
    df_raw = pd.read_sql(query, conn)

    if df_raw.empty or df_raw['module'].isnull().all():
        st.info("ℹ️ Belum ada data nilai terkini untuk dievaluasi.")
        conn.close()
        return

    # ==========================================
    # ANALISIS MACHINE LEARNING
    # ==========================================
    summary_list = []
    
    for student_id in df_raw['id'].unique():
        student_name = df_raw[df_raw['id'] == student_id]['name'].iloc[0]
        student_scores = df_raw[df_raw['id'] == student_id][['module', 'score']].dropna()
        
        if not student_scores.empty:
            student_scores.columns = ['Modul', 'Nilai']
            
            # Prediksi Random Forest
            prediction, confidence, weak_mods, avg_score = run_analysis(student_scores)
            
            # Istilah Profesional untuk Pengambil Keputusan
            status = "Sesuai Standar" if prediction in ["Sangat Baik", "Baik"] else "Perlu Penguatan"
            
            summary_list.append({
                "Nama Peserta": student_name,
                "Rerata Skor": avg_score,
                "Klasifikasi AI": prediction,
                "Status Akhir": status,
                "Catatan Modul": ", ".join(map(str, weak_mods)) if weak_mods else "Optimal"
            })

    df_final = pd.DataFrame(summary_list)

    # ==========================================
    # DASHBOARD VIEW
    # ==========================================
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Peserta", len(df_final))
    
    # Hitung presentase kelulusan
    memenuhi = len(df_final[df_final["Status Akhir"] == "Sesuai Standar"])
    persen_lulus = int((memenuhi/len(df_final))*100) if len(df_final) > 0 else 0
    
    col2.metric("Kelulusan Standar", f"{persen_lulus}%")
    col3.metric("Rerata Kolektif", round(df_final["Rerata Skor"].mean(), 1))

    st.divider()

    c_tab, c_pie = st.columns([2, 1])

    with c_tab:
        st.subheader("📋 Tabel Rekapitulasi Performa")
        st.dataframe(df_final, use_container_width=True, hide_index=True)

    with c_pie:
        st.subheader("📊 Distribusi Performa")
        fig = px.pie(df_final, names='Klasifikasi AI', 
                     color='Klasifikasi AI',
                     color_discrete_map={'Sangat Baik':'#00CC96', 'Baik':'#636EFA', 'Cukup':'#FECB52', 'Kurang':'#EF553B'},
                     hole=0.4)
        fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), 
                          paper_bgcolor='rgba(0,0,0,0)', legend_font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    conn.close()

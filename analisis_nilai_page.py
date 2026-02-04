import streamlit as st
import pandas as pd
from ml_model import run_analysis
from db import get_db

# ==========================================
# 1. UI CLEAN (TEKS PUTIH)
# ==========================================
st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p, label, .stMarkdown p, h2 {
        color: white !important;
    }
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        font-weight: bold !important;
        border: none;
        width: 100%;
        height: 45px;
    }
    </style>
    """, unsafe_allow_html=True)

def analisis_nilai_page():
    st.markdown("## 😎 Analisis Performa Akademik")
    st.markdown("Menganalisis data dari CSV menggunakan **Machine Learning**")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # 1. AMBIL DAFTAR MAHASISWA (Hasil Import CSV sebelumnya)
    cur.execute("SELECT id, name, division, university FROM students ORDER BY name ASC")
    students = cur.fetchall()

    if not students:
        st.warning("Data mahasiswa kosong. Silakan import CSV mahasiswa terlebih dahulu.")
        conn.close()
        return

    # Mapping nama untuk selectbox
    student_map = {f"{s[1]} | {s[2]} | {s[3]}": s[0] for s in students}
    selected_name = st.selectbox("Pilih Mahasiswa untuk Dianalisis", list(student_map.keys()))
    student_id = student_map[selected_name]

    # 2. AMBIL NILAI MODUL (Hasil Import CSV nilai sebelumnya)
    cur.execute("""
        SELECT module, score FROM module_scores 
        WHERE student_id = %s 
        ORDER BY CAST(module AS UNSIGNED) ASC
    """, (student_id,))
    rows = cur.fetchall()

    if not rows:
        st.error("Mahasiswa ini belum memiliki data nilai di database.")
        conn.close()
        return

    # Siapkan Dataframe untuk Machine Learning
    df = pd.DataFrame(rows, columns=["Modul", "Nilai"])
    df["Modul"] = pd.to_numeric(df["Modul"])
    df["Nilai"] = pd.to_numeric(df["Nilai"])
    
    st.write("### Data Nilai Saat Ini:")
    st.table(df)

    # 3. JALANKAN ANALISIS ML
    if st.button("🔍 Jalankan Analisis Performa"):
        with st.spinner("Sedang menghitung..."):
            # Memanggil fungsi dari ml_model.py
            result, confidence, weak_modules, avg_score = run_analysis(df)

            # Simpan hasil prediksi ke database
            try:
                cur.execute("""
                    INSERT INTO predictions (student_id, result) 
                    VALUES (%s, %s)
                """, (student_id, result))
                conn.commit()
                
                # Tampilkan Hasil
                st.success(f"### Hasil Prediksi: {result}")
                st.info(f"Rata-rata Nilai: **{avg_score:.2f}**")

                if weak_modules:
                    st.warning(f"⚠ Modul yang perlu ditingkatkan: {', '.join(map(str, weak_modules))}")
                else:
                    st.balloons()
                    st.success("🎉 Performa sangat baik di semua modul!")
            
            except Exception as e:
                st.error(f"Gagal menyimpan analisis: {e}")

    conn.close()

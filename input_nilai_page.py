import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. CSS ABSOLUT (ANTI TEKS HILANG)
# ==========================================
def apply_custom_css():
    st.markdown("""
        <style>
        /* Paksa semua teks & label jadi hitam pekat setiap saat */
        html, body, [data-testid="stWidgetLabel"] p, label, .stMarkdown p {
            color: #000000 !important;
            font-weight: 700 !important;
            opacity: 1 !important;
            -webkit-text-fill-color: #000000 !important;
        }
        
        /* Box Upload agar terlihat jelas */
        [data-testid="stFileUploader"] {
            border: 2px dashed #0045AD !important;
            background-color: #F0F2F6 !important;
            border-radius: 10px;
        }

        /* Tombol Biru Royal */
        div.stButton > button {
            background-color: #0045AD !important;
            color: white !important;
            font-weight: bold !important;
            height: 45px;
            width: 100%;
            border: none;
        }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 2. HALAMAN INPUT NILAI
# ==========================================
def input_nilai_page():
    apply_custom_css()
    st.title("📝 Manajemen Nilai Mahasiswa")
    st.divider()

    # Navigasi stabil menggunakan radio
    menu = st.radio("Pilih Menu:", ["📊 Lihat Nilai", "📤 Import Nilai (CSV/Excel)"], 
                    horizontal=True, key="nav_nilai_final")

    conn = get_db()
    cur = conn.cursor()

    if menu == "📊 Lihat Nilai":
        st.subheader("Daftar Nilai Mahasiswa")
        cur.execute("""
            SELECT s.name, m.module, m.score 
            FROM module_scores m 
            JOIN students s ON m.student_id = s.id 
            ORDER BY m.id DESC LIMIT 100
        """)
        res = cur.fetchall()
        if res:
            st.dataframe(pd.DataFrame(res, columns=["Nama", "Modul", "Skor"]), use_container_width=True)
        else:
            st.info("Belum ada data nilai.")

    elif menu == "📤 Import Nilai (CSV/Excel)":
        st.subheader("Unggah Nilai Kolektif")
        st.write("Format kolom: **student_id, module, score**")
        
        uploaded_file = st.file_uploader("Pilih Berkas", type=["csv", "xlsx"], key="uploader_nilai_v1")

        if uploaded_file:
            try:
                # Baca file
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.write("**Pratinjau Data:**")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("🚀 Simpan Nilai ke Database"):
                    for _, row in df.iterrows():
                        try:
                            sid = int(str(row['student_id']).upper().replace('S', ''))
                            mod = int(row['module'])
                            scr = int(row['score'])
                            
                            cur.execute("""
                                INSERT INTO module_scores (student_id, module, score) 
                                VALUES (%s, %s, %s) 
                                ON DUPLICATE KEY UPDATE score=VALUES(score)
                            """, (sid, mod, scr))
                        except:
                            continue
                    
                    conn.commit()
                    st.success("Berhasil mengimpor nilai!")
                    st.balloons()
            except Exception as e:
                st.error(f"Error membaca file: {e}")

    conn.close()

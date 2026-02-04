import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 🚀 Sinkronisasi Nilai Massal (Spreadsheet)")
    st.info("Gunakan fitur ini untuk menginput nilai dari mentor secara otomatis.")

    # 1. Upload File dari Mentor
    uploaded_file = st.file_uploader("Pilih File Spreadsheet (CSV atau Excel)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            # Membaca file berdasarkan format
            if uploaded_file.name.endswith('.csv'):
                df_mentor = pd.read_csv(uploaded_file)
            else:
                df_mentor = pd.read_excel(uploaded_file)

            st.markdown("#### 🔍 Preview Data Mentor")
            st.dataframe(df_mentor.head(), use_container_width=True)

            # Validasi Kolom (Pastikan ada kolom student_id, module, dan score)
            required_columns = ['student_id', 'module', 'score']
            if not all(col in df_mentor.columns for col in required_columns):
                st.error(f"Format file salah! Pastikan ada kolom: {', '.join(required_columns)}")
                return

            if st.button("📥 Sinkronkan ke Database Sekarang"):
                conn = get_db()
                cur = conn.cursor()
                
                counter = 0
                for _, row in df_mentor.iterrows():
                    # UPSERT Logic: Insert jika baru, Update jika sudah ada
                    cur.execute("""
                        INSERT INTO module_scores (student_id, module, score)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE score = VALUES(score)
                    """, (row['student_id'], row['module'], row['score']))
                    counter += 1
                
                conn.commit()
                cur.close()
                conn.close()
                
                st.success(f"✅ Berhasil menyinkronkan {counter} data nilai mahasiswa!")
                st.balloons()

        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")

# Jangan lupa panggil fungsi ini di app.py Anda

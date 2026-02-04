import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.title("📝 Manajemen Nilai Mahasiswa")
    
    tab1, tab2 = st.tabs(["📥 Import Nilai Mahasiswa", "✍️ Input Nilai Mahasiswa"])

    with tab1:
        
        uploaded_file = st.file_uploader("Pilih file Excel/CSV", type=["csv", "xlsx"], key="bulk_uploader")

        if uploaded_file is not None:
            try:
                # Membaca file berdasarkan format
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.write("Preview Data:")
                st.dataframe(df.head())

                if st.button("Simpan Nilai Mahaiswa", use_container_width=True):
                    conn = get_db()
                    cur = conn.cursor()
                    
                    c_score = 0
                    c_student = 0
                    
                    for _, row in df.iterrows():
                        # Membersihkan data dari teks (S001 -> 1, Modul 1 -> 1)
                        s_id = int(str(row['student_id']).upper().replace('S', ''))
                        m_num = int(str(row['module']).lower().replace('modul ', '').strip())
                        s_score = int(row['score'])
                        s_name = str(row['name']) if 'name' in df.columns else f"Mahasiswa {s_id}"

                        # 1. Daftarkan ke tabel students agar total di Dashboard naik
                        cur.execute("SELECT id FROM students WHERE id = %s", (s_id,))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO students (id, name, division, university) 
                                VALUES (%s, %s, %s, %s)
                            """, (s_id, s_name, "Batch Import", "Mentor Source"))
                            c_student += 1

                        # 2. Simpan Nilai
                        cur.execute("""
                            INSERT INTO module_scores (student_id, module, score)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE score = VALUES(score)
                        """, (s_id, m_num, s_score))
                        c_score += 1
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    st.success(f"✅ Berhasil! {c_score} nilai masuk & {c_student} mahasiswa baru terdaftar.")
                    st.balloons()
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")

    with tab2:
        st.write("Gunakan Tab 1 untuk mengunggah 100+ data sekaligus.")


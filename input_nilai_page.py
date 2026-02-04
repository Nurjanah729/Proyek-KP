import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 📝 Manajemen Nilai Mahasiswa")
    
    # Navigasi Tab
    tab1, tab2 = st.tabs(["📥 Import Massal (Spreadsheet)", "✍️ Input Manual"])

    # ==========================================
    # TAB 1: IMPORT MASSAL
    # ==========================================
    with tab1:
        st.subheader("Import Nilai dari Mentor")
        uploaded_file = st.file_uploader("Pilih file CSV atau Excel", type=["csv", "xlsx"], key="file_bulk")

        if uploaded_file is not None:
            try:
                # Membaca file sesuai format
                if uploaded_file.name.endswith('.csv'):
                    df_mentor = pd.read_csv(uploaded_file)
                else:
                    df_mentor = pd.read_excel(uploaded_file)
                
                st.write("Preview Data:")
                st.dataframe(df_mentor.head(), use_container_width=True)

                if st.button("🚀 Sinkronkan Sekarang", use_container_width=True):
                    conn = get_db()
                    cur = conn.cursor()
                    
                    count_score = 0
                    count_new_student = 0
                    
                    # Ambil daftar kolom untuk cek kolom 'name'
                    cols = df_mentor.columns.tolist()

                    for _, row in df_mentor.iterrows():
                        s_id = int(row['student_id'])
                        m_num = int(row['module'])
                        s_score = int(row['score'])

                        # 1. Cek apakah mahasiswa sudah terdaftar di tabel students
                        cur.execute("SELECT id FROM students WHERE id = %s", (s_id,))
                        if not cur.fetchone():
                            # Jika tidak ada, daftarkan otomatis agar Dashboard bertambah
                            s_name = row['name'] if 'name' in cols else f"Mahasiswa ID {s_id}"
                            cur.execute("""
                                INSERT INTO students (id, name, division, university) 
                                VALUES (%s, %s, %s, %s)
                            """, (s_id, s_name, "Batch Import", "Mentor Source"))
                            count_new_student += 1

                        # 2. Masukkan/Update nilai ke module_scores
                        cur.execute("""
                            INSERT INTO module_scores (student_id, module, score)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE score = VALUES(score)
                        """, (s_id, m_num, s_score))
                        count_score += 1
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    st.success(f"✅ Berhasil! {count_score} nilai masuk & {count_new_student} mahasiswa baru terdaftar.")
                    st.balloons()
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")

    # ==========================================
    # TAB 2: INPUT MANUAL
    # ==========================================
    with tab2:
        st.info("Pilih mahasiswa untuk mengupdate nilai secara satuan.")
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT id, name FROM students ORDER BY name ASC")
        students = cur.fetchall()
        
        if students:
            student_map = {f"{s[1]} (ID: {s[0]})": s[0] for s in students}
            selected = st.selectbox("Cari Mahasiswa", options=list(student_map.keys()), index=None)
            
            if selected:
                st.write(f"Mengedit nilai untuk: **{selected}**")
                # Tambahkan logika form manual di sini jika diperlukan
        
        cur.close()
        conn.close()

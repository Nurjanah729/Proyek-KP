import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.title("📝 Manajemen Nilai Mahasiswa")
    
    # Navigasi Tab untuk memisahkan metode input
    tab1, tab2 = st.tabs(["📥 Import Massal (Spreadsheet)", "✍️ Input Manual per Mahasiswa"])

    # ==========================================
    # TAB 1: IMPORT MASSAL (DARI MENTOR)
    # ==========================================
    with tab1:
        st.subheader("Import Nilai dari Mentor")
        st.info("Gunakan format CSV atau Excel dengan kolom: student_id, module, score")
        
        uploaded_file = st.file_uploader("Pilih file dari mentor", type=["csv", "xlsx"], key="bulk_upload")

        if uploaded_file is not None:
            try:
                # Membaca file
                if uploaded_file.name.endswith('.csv'):
                    df_mentor = pd.read_csv(uploaded_file)
                else:
                    df_mentor = pd.read_excel(uploaded_file)

                st.write("Preview Data:")
                st.dataframe(df_mentor.head(), use_container_width=True)

        if st.button("🚀 Sinkronkan Semua Nilai", use_container_width=True):
            conn = get_db()
            cur = conn.cursor()
            
            try:
                count_score = 0
                count_new_student = 0
                
                # Ambil semua kolom yang ada di file upload
                cols = df_mentor.columns.tolist()
        
                for _, row in df_mentor.iterrows():
                    s_id = int(row['student_id'])
                    m_num = int(row['module'])
                    s_score = int(row['score'])
        
                    # 1. CEK: Apakah ID ini sudah ada di tabel students?
                    cur.execute("SELECT id FROM students WHERE id = %s", (s_id,))
                    exists = cur.fetchone()
        
                    # 2. JIKA BELUM ADA: Daftarkan otomatis ke tabel students
                    if not exists:
                        # Jika ada kolom 'name' di Excel gunakan itu, jika tidak gunakan placeholder
                        s_name = row['name'] if 'name' in cols else f"Mahasiswa ID {s_id}"
                        
                        cur.execute("""
                            INSERT INTO students (id, name, division, university)
                            VALUES (%s, %s, %s, %s)
                        """, (s_id, s_name, "Batch Import", "Mentor Source"))
                        count_new_student += 1
        
                    # 3. INPUT NILAI ke module_scores
                    cur.execute("""
                        INSERT INTO module_scores (student_id, module, score)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE score = VALUES(score)
                    """, (s_id, m_num, s_score))
                    count_score += 1
                
                conn.commit()
                st.success(f"✅ Berhasil! {count_score} nilai masuk. {count_new_student} mahasiswa baru didaftarkan.")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")
            finally:
                cur.close()
                conn.close()

            except Exception as e:
                st.error(f"Gagal membaca file: {e}. Pastikan library 'openpyxl' sudah terinstall.")

    # ==========================================
    # TAB 2: INPUT MANUAL (PER MAHASISWA)
    # ==========================================
    with tab2:
        st.subheader("Update Nilai Satuan")
        conn = get_db()
        cur = conn.cursor()

        # Ambil daftar mahasiswa untuk dropdown
        cur.execute("SELECT id, name, division FROM students ORDER BY name ASC")
        students = cur.fetchall()
        student_map = {f"{s[1]} ({s[2]})": s[0] for s in students}

        selected_student = st.selectbox("Pilih Mahasiswa", options=list(student_map.keys()), index=None)

        if selected_student:
            student_id = student_map[selected_student]
            
            # Ambil nilai yang sudah ada
            cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
            existing_scores = dict(cur.fetchall())

            # Siapkan DataFrame untuk Editor
            df_manual = pd.DataFrame({
                "Modul": [f"Modul {i}" for i in range(1, 11)],
                "Nilai": [existing_scores.get(i, 0) for i in range(1, 11)]
            })

            with st.form("manual_update_form"):
                edited_df = st.data_editor(
                    df_manual,
                    column_config={
                        "Modul": st.column_config.TextColumn("Nama Modul", disabled=True),
                        "Nilai": st.column_config.NumberColumn("Nilai (0-100)", min_value=0, max_value=100)
                    },
                    hide_index=True,
                    use_container_width=True
                )

                if st.form_submit_button("💾 Simpan Perubahan"):
                    for _, row in edited_df.iterrows():
                        mod_num = int(row["Modul"].split(" ")[1])
                        cur.execute("""
                            INSERT INTO module_scores (student_id, module, score)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE score = VALUES(score)
                        """, (student_id, mod_num, int(row["Nilai"])))
                    
                    conn.commit()
                    st.success("✅ Nilai berhasil diperbarui!")
        
        cur.close()
        conn.close()





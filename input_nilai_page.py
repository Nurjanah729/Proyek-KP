import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 📝 Input Nilai Modul (Pilih & Ketik)")
    
    conn = get_db()
    cur = conn.cursor()

    # 1. Pilih Mahasiswa
    cur.execute("SELECT id, name, division, university FROM students ORDER BY name ASC")
    students = cur.fetchall()
    if not students:
        st.warning("Belum ada data mahasiswa.")
        return

    student_map = {f"{s[1]} | {s[2]}": s[0] for s in students}
    selected_student = st.selectbox("Cari Mahasiswa", options=list(student_map.keys()), index=None)

    if not selected_student:
        conn.close()
        return

    student_id = student_map[selected_student]
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    st.markdown("---")
    st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")

    # 2. Persiapkan Data Tabel untuk Input
    # Kita buat 10 baris (Modul 1-10)
    df_input = pd.DataFrame({
        "Modul": [f"Modul {i}" for i in range(1, 11)],
        "Nilai": [existing_scores.get(i, 80) for i in range(1, 11)]
    })

    # 3. BAGIAN INI KUNCI AGAR TIDAK ADA "NO RESULTS"
    # Kita pakai data_editor dengan column_config Selectbox
    # Admin bisa pilih angka yang tersedia, atau ketik langsung di kolomnya
    
    with st.form("form_input_keren"):
        edited_df = st.data_editor(
            df_input,
            column_config={
                "Modul": st.column_config.TextColumn("Nama Modul", disabled=True),
                "Nilai": st.column_config.SelectboxColumn(
                    "Pilih/Ketik Nilai",
                    help="Klik untuk pilih, atau double klik untuk ketik angka bebas",
                    width="large",
                    options=[0, 50, 60, 70, 75, 80, 85, 90, 95, 100],
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True,
            key="input_tabel_nilai"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Simpan Semua Nilai", use_container_width=True):
            try:
                cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
                for _, row in edited_df.iterrows():
                    # Ambil angka modul dari teks "Modul 1" -> 1
                    mod_num = int(row['Modul'].split(' ')[1])
                    cur.execute("INSERT INTO module_scores (student_id, module, score) VALUES (%s, %s, %s)", 
                                (student_id, mod_num, int(row['Nilai'])))
                conn.commit()
                st.success("✅ Berhasil! Nilai tersimpan tanpa error.")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal simpan: {e}")

    conn.close()

import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 📝 Input Nilai Modul")

    conn = get_db()
    cur = conn.cursor()

    # =============================
    # 1. Pilih Mahasiswa
    # =============================
    cur.execute("SELECT id, name, division, university FROM students ORDER BY name ASC")
    students = cur.fetchall()

    if not students:
        st.warning("Belum ada data mahasiswa.")
        return

    student_map = {f"{s[1]} | {s[2]}": s[0] for s in students}
    selected_student = st.selectbox(
        "Cari Mahasiswa",
        options=list(student_map.keys()),
        index=None
    )

    if not selected_student:
        conn.close()
        return

    student_id = student_map[selected_student]

    # =============================
    # 2. Ambil nilai yang sudah ada
    # =============================
    cur.execute(
        "SELECT module, score FROM module_scores WHERE student_id = %s",
        (student_id,)
    )
    existing_scores = dict(cur.fetchall())

    st.markdown("---")
    st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")

    # =============================
    # 3. Data awal tabel
    # =============================
    df_input = pd.DataFrame({
        "Modul": [f"Modul {i}" for i in range(1, 11)],
        "Nilai": [existing_scores.get(i, 70) for i in range(1, 11)]
    })

    # =============================
    # 4. FORM INPUT NILAI
    # =============================
    with st.form("form_input_nilai"):
        edited_df = st.data_editor(
            df_input,
            column_config={
                "Modul": st.column_config.TextColumn(
                    "Nama Modul",
                    disabled=True
                ),
                "Nilai": st.column_config.SelectboxColumn(
                    "Pilih Nilai",
                    help="Nilai hanya boleh 50–60, 70–80, atau 90–100",
                    width="large",
                    options=(

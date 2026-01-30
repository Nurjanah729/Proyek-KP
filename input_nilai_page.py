import streamlit as st
import pandas as pd
from db import get_db

# ======================
# INPUT NILAI PAGE
# ======================
def input_nilai_page():
    st.markdown("""
    <h3>📝 Input Nilai Modul</h3>
    <p style="color:#6b7280;">
        Masukkan nilai modul mahasiswa untuk analisis performa
    </p>
    """, unsafe_allow_html=True)

    conn = get_db()
    cur = conn.cursor()

    # ======================
    # PILIH MAHASISWA
    # ======================
    cur.execute("""
        SELECT id, name, division, university
        FROM students
        ORDER BY id DESC
    """)
    students = cur.fetchall()

    if not students:
        st.warning("⚠️ Belum ada mahasiswa. Tambahkan mahasiswa terlebih dahulu.")
        conn.close()
        return

    student_map = {
        f"{s[1]} | {s[2]} | {s[3]}": s[0]
        for s in students
    }

    selected_student = st.selectbox(
        "Pilih Mahasiswa",
        list(student_map.keys())
    )

    student_id = student_map[selected_student]

    st.markdown("---")

    # ======================
    # INPUT NILAI MODUL (SLIDER)
    # ======================
    st.markdown("## 📊 Nilai Modul")

    if "scores" not in st.session_state:
    st.session_state.scores = {}

    for modul in range(1, 11):
    st.markdown(f"**Modul {modul}**")

    nilai = st.slider(
        label=f"Nilai Modul {modul}",
        min_value=0,
        max_value=100,
        value=st.session_state.scores.get(modul, 75),
        key=f"modul_{modul}",
        label_visibility="collapsed"
    )

    # SIMPAN KE SESSION STATE
    st.session_state.scores[modul] = nilai

    # ======================
    # SIMPAN NILAI
    # ======================
    if st.button("💾 Simpan Nilai"):
    cur.execute(
        "DELETE FROM module_scores WHERE student_id = %s",
        (student_id,)
    )

    for module, score in st.session_state.scores.items():
        cur.execute("""
            INSERT INTO module_scores (student_id, module, score)
            VALUES (%s, %s, %s)
        """, (student_id, module, score))

    conn.commit()
    conn.close()

    st.success("✅ Nilai berhasil disimpan")
    st.session_state.scores = {}  # reset kalau mau
    st.rerun()

    st.markdown("---")

    # ======================
    # TAMPILKAN NILAI TERSIMPAN
    # ======================
    conn = get_db()
    df = pd.read_sql_query("""
        SELECT module AS Modul, score AS Nilai
        FROM module_scores
        WHERE student_id = %s
        ORDER BY CAST(module AS UNSIGNED) ASC
    """, conn, params=(student_id,))

    # PAKSA MODULE JADI ANGKA
    df["Modul"] = df["Modul"].astype(int)

    # URUTKAN BERDASARKAN ANGKA
    df = df.sort_values(by="Modul")

    # RESET INDEX SUPAYA MULAI DARI 1
    df.index = range(1, len(df) + 1)

    conn.close()

    if not df.empty:
        st.markdown("### 📋 Nilai Tersimpan")
        st.table(df)





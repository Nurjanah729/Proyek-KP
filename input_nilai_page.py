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
    # 2. Ambil nilai existing
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
                    "Nilai (55–100 / Other)",
                    options=list(range(0, 101)) + ["Other"],
                    help="Pilih nilai atau pilih Other lalu double-click untuk input manual",
                    required=True,
                    width="large"
                )
            },
            hide_index=True,
            use_container_width=True
        )

        if st.form_submit_button("💾 Simpan Semua Nilai", use_container_width=True):
            try:
                cur.execute(
                    "DELETE FROM module_scores WHERE student_id = %s",
                    (student_id,)
                )

                for _, row in edited_df.iterrows():
                    mod_num = int(row["Modul"].split(" ")[1])
                    raw_nilai = row["Nilai"]

                    # Jika masih Other, paksa admin mengetik angka
                    if raw_nilai == "Other":
                        raise ValueError(
                            "Pilih Other lalu ketik nilai manual (double-click sel)"
                        )

                    # Simpan APA ADANYA sebagai integer
                    nilai = int(raw_nilai)

                    cur.execute(
                        """
                        INSERT INTO module_scores (student_id, module, score)
                        VALUES (%s, %s, %s)
                        """,
                        (student_id, mod_num, nilai)
                    )

                conn.commit()
                st.success("✅ Nilai berhasil disimpan")
                st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Gagal menyimpan: {e}")

    conn.close()

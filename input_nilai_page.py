import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### ⚡ Input Nilai Cepat (Mode Spreadsheet)")
    st.info("Pilih mahasiswa, ketik nilai di tabel, lalu tekan tombol Simpan di bawah.")

    conn = get_db()
    cur = conn.cursor()

    # 1. PILIH MAHASISWA
    cur.execute("SELECT id, name, division, university FROM students ORDER BY name ASC")
    students = cur.fetchall()

    if not students:
        st.warning("Belum ada data mahasiswa.")
        return

    student_map = {f"{s[1]} | {s[2]}": s[0] for s in students}
    selected_student = st.selectbox("Cari Mahasiswa", options=list(student_map.keys()), index=None, placeholder="🔍 Ketik nama...")

    if not selected_student:
        conn.close()
        return

    student_id = student_map[selected_student]

    # 2. AMBIL DATA NILAI LAMA
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    # Buat DataFrame awal (Modul 1-10)
    df_nilai = pd.DataFrame({
        "Modul": [i for i in range(1, 11)],
        "Nilai": [existing_scores.get(i, 0) for i in range(1, 11)]
    })

    # 3. DATA EDITOR (Tabel yang bisa langsung diketik)
    st.write(f"✍️ **Edit Nilai: {selected_student.split(' | ')[0]}**")
    
    # Bagian ini yang bikin nggak capek: Bisa diketik langsung seperti Excel
    edited_df = st.data_editor(
        df_nilai,
        column_config={
            "Modul": st.column_config.NumberColumn("Modul", disabled=True),
            "Nilai": st.column_config.NumberColumn(
                "Nilai (0-100)",
                min_value=0,
                max_value=100,
                required=True,
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    # 4. TOMBOL SIMPAN
    if st.button("💾 Simpan Semua Nilai"):
        try:
            # Hapus yang lama, masukkan yang baru hasil editan tabel
            cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
            
            for index, row in edited_df.iterrows():
                cur.execute("""
                    INSERT INTO module_scores (student_id, module, score)
                    VALUES (%s, %s, %s)
                """, (student_id, int(row['Modul']), int(row['Nilai'])))
            
            conn.commit()
            st.success("✅ Nilai berhasil diperbarui!")
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"Gagal: {e}")
        finally:
            conn.close()

import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### ⚡ Input Nilai Cepat (Mode Excel)")
    st.info("Pilih mahasiswa, isi nilai pada tabel di bawah, lalu klik Simpan.")

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

    # 2. SIAPKAN DATA NILAI (Ambil dari DB atau buat baru)
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_data = dict(cur.fetchall())

    # Buat DataFrame untuk tabel edit
    # Modul 1 sampai 10
    df_input = pd.DataFrame({
        "Modul": [f"Modul {i}" for i in range(1, 11)],
        "Nilai": [existing_data.get(i, 0) for i in range(1, 11)]
    })

    # 3. TAMPILKAN EDITOR TABEL (INI YANG BIKIN GA CAPE)
    st.markdown(f"**Edit Nilai untuk: {selected_student.split(' | ')[0]}**")
    
    edited_df = st.data_editor(
        df_input,
        column_config={
            "Modul": st.column_config.TextColumn("Modul", disabled=True), # Nama modul ga bisa diubah
            "Nilai": st.column_config.NumberColumn(
                "Nilai (0-100)",
                min_value=0,
                max_value=100,
                step=1,
                format="%d"
            ),
        },
        hide_index=True,
        use_container_width=True,
        key="editor_nilai"
    )

    # 4. TOMBOL SIMPAN SEKALIGUS
    if st.button("🚀 Simpan Semua Nilai"):
        try:
            cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
            
            # Ambil data dari tabel yang sudah diedit user
            for _, row in edited_df.iterrows():
                mod_num = int(row['Modul'].split(' ')[1])
                score_val = int(row['Nilai'])
                
                cur.execute("""
                    INSERT INTO module_scores (student_id, module, score)
                    VALUES (%s, %s, %s)
                """, (student_id, mod_num, score_val))

            conn.commit()
            st.success("✅ Semua nilai berhasil diperbarui!")
            st.balloons() # Efek biar admin senang
        except Exception as e:
            conn.rollback()
            st.error(f"Gagal: {e}")
        finally:
            conn.close()

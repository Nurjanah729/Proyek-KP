import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 📝 Input Nilai Cepat (Mode Grouping)")
    
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
    
    # 2. DEFINISI RENTANG (Agar Admin Gak Capek Scroll)
    # Kita sediakan angka utama saja sebagai "Shortcut"
    opsi_nilai = [
        "100", "95", "90", # Group 90-100
        "85", "80",       # Group 80-85
        "75", "70",       # Group 70-75
        "65", "60",       # Group 60-65
        "50", "0"
    ]

    with st.form("form_nilai"):
        st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")
        col1, col2 = st.columns(2)
        scores_to_save = {}

        for i in range(1, 11):
            target_col = col1 if i <= 5 else col2
            current_val = str(existing_scores.get(i, 80))

            with target_col:
                # TRICK: Gunakan st.selectbox tetapi tambahkan nilai manual ke daftar opsi secara dinamis
                # Ini mencegah "No Results" karena nilai manual akan dianggap bagian dari daftar
                temp_options = opsi_nilai.copy()
                if current_val not in temp_options:
                    temp_options.append(current_val)
                    temp_options.sort(key=int, reverse=True)

                # Gunakan st.text_input atau st.number_input yang diletakkan di bawah selectbox kecil
                # Tujuannya agar admin bisa memilih CEPAT atau mengetik MANUAL
                
                st.markdown(f"**Modul {i}**")
                pilihan = st.selectbox(
                    f"Pilih Cepat Modul {i}",
                    options=temp_options,
                    index=temp_options.index(current_val),
                    key=f"sel_{i}",
                    label_visibility="collapsed"
                )
                
                # Admin bisa tetap mengubah angka secara manual di sini jika butuh spesifik
                final_val = st.text_input(
                    f"Atau Ketik Manual Modul {i}", 
                    value=pilihan, 
                    key=f"txt_{i}",
                    label_visibility="collapsed"
                )
                
                scores_to_save[i] = final_val

        if st.form_submit_button("💾 Simpan Semua Nilai", use_container_width=True):
            try:
                cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
                for mod_num, score_val in scores_to_save.items():
                    cur.execute("INSERT INTO module_scores (student_id, module, score) VALUES (%s, %s, %s)", 
                                (student_id, mod_num, int(score_val)))
                conn.commit()
                st.success("Berhasil disimpan!")
                st.rerun()
            except:
                st.error("Pastikan input adalah angka!")
    conn.close()

import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    # Header yang rapi
    st.markdown("### 📝 Input Nilai Modul")
    
    conn = get_db()
    cur = conn.cursor()

    # 1. Pilih Mahasiswa
    cur.execute("SELECT id, name, division, university FROM students ORDER BY name ASC")
    students = cur.fetchall()
    
    if not students:
        st.warning("⚠️ Belum ada data mahasiswa.")
        return

    student_map = {f"{s[1]} | {s[2]}": s[0] for s in students}
    selected_student = st.selectbox("Cari Mahasiswa", options=list(student_map.keys()), index=None, placeholder="🔍 Pilih Mahasiswa...")

    if not selected_student:
        conn.close()
        return

    student_id = student_map[selected_student]
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    st.markdown("---")
    st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")

    # 2. Form Input Nilai
    # Menggunakan number_input agar admin bisa mengetik angka berapapun (87, 99, dll) tanpa error
    with st.form("form_nilai_clean"):
        col1, col2 = st.columns(2)
        scores_to_save = {}

        for i in range(1, 11):
            target_col = col1 if i <= 5 else col2
            current_val = int(existing_scores.get(i, 80)) # Ambil nilai lama atau default 80
            
            with target_col:
                st.markdown(f"**Modul {i}**")
                # Kotak input angka yang bisa diketik bebas atau diklik panahnya
                # Tidak akan muncul "No Results" jika admin mengetik angka manual
                nilai = st.number_input(
                    label=f"Modul {i}",
                    min_value=0,
                    max_value=100,
                    value=current_val,
                    key=f"input_mod_{i}",
                    label_visibility="collapsed" # Menghilangkan label ganda agar rapi
                )
                scores_to_save[i] = nilai

        st.markdown("<br>", unsafe_allow_html=True)
        btn_simpan = st.form_submit_button("💾 Simpan Semua Nilai", use_container_width=True)

    # 3. Logika Simpan
    if btn_simpan:
        try:
            cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
            for mod_num, score_val in scores_to_save.items():
                cur.execute("INSERT INTO module_scores (student_id, module, score) VALUES (%s, %s, %s)", 
                            (student_id, mod_num, score_val))
            conn.commit()
            st.success("✅ Nilai berhasil disimpan!")
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"Gagal: {e}")
        finally:
            conn.close()

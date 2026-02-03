import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 📝 Input Nilai Modul")
    
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
    
    # DAFTAR ANGKA UTAMA (Biar admin gak capek scroll)
    opsi_utama = ["100", "95", "90", "85", "80", "75", "70", "65", "60", "50", "0"]

    with st.form("form_nilai_efisien"):
        st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")
        
        col1, col2 = st.columns(2)
        scores_to_save = {}

        for i in range(1, 11):
            target_col = col1 if i <= 5 else col2
            
            # Ambil nilai lama dari database
            current_val = str(existing_scores.get(i, 80)) 
            
            with target_col:
                # --- TRIK AGAR BISA KETIK BEBAS TANPA 'NO RESULTS' ---
                # Kita buat daftar opsi yang isinya angka utama + angka yang sedang diketik
                # Streamlit akan selalu menganggap angka tersebut ada di daftar
                
                opsi_tampilan = opsi_utama.copy()
                if current_val not in opsi_tampilan:
                    opsi_tampilan.append(current_val)
                
                # Urutkan angka dari besar ke kecil
                opsi_tampilan = sorted(list(set(opsi_tampilan)), key=int, reverse=True)

                nilai_input = st.selectbox(
                    f"Modul {i}",
                    options=opsi_tampilan,
                    index=opsi_tampilan.index(current_val),
                    key=f"mod_{i}",
                    help="Pilih angka atau ketik angka bebas lalu tekan Enter"
                )
                scores_to_save[i] = nilai_input

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 Simpan Semua Nilai", use_container_width=True):
            try:
                cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
                for mod_num, score_val in scores_to_save.items():
                    cur.execute("INSERT INTO module_scores (student_id, module, score) VALUES (%s, %s, %s)", 
                                (student_id, mod_num, int(score_val)))
                conn.commit()
                st.success("✅ Nilai berhasil disimpan!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan. Pastikan input adalah angka. Error: {e}")
    
    conn.close()

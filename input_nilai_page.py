import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 📝 Input Nilai Modul (Pilihan Cepat)")
    
    conn = get_db()
    cur = conn.cursor()

    # 1. PILIH MAHASISWA
    cur.execute("SELECT id, name, division, university FROM students ORDER BY name ASC")
    students = cur.fetchall()

    if not students:
        st.warning("⚠️ Belum ada data mahasiswa.")
        return

    student_map = {f"{s[1]} | {s[2]}": s[0] for s in students}
    selected_student = st.selectbox("Cari Mahasiswa", options=list(student_map.keys()), index=None, placeholder="🔍 Ketik nama mahasiswa...")

    if not selected_student:
        conn.close()
        return

    student_id = student_map[selected_student]

    # Ambil data lama dari database
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    st.markdown("---")
    
    # 2. DAFTAR PILIHAN NILAI (Agar tidak capek scroll 1-100)
    # Kita berikan angka-angka yang paling sering diberikan dosen
    opsi_nilai = [100, 95, 90, 85, 80, 75, 70, 65, 60, 50, 0]

    with st.form("form_nilai_cepat"):
        st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")
        
        col1, col2 = st.columns(2)
        scores_to_save = {}

        for i in range(1, 11):
            target_col = col1 if i <= 5 else col2
            
            # Ambil nilai lama, jika tidak ada default ke 80
            current_val = existing_scores.get(i, 80)
            
            # Jika nilai lama tidak ada di daftar opsi_nilai, tambahkan secara otomatis 
            # supaya tidak error saat load data lama
            display_options = opsi_nilai.copy()
            if current_val not in display_options:
                display_options.append(current_val)
                display_options.sort(reverse=True)

            with target_col:
                nilai = st.selectbox(
                    f"Modul {i}",
                    options=display_options,
                    index=display_options.index(current_val),
                    key=f"modul_{i}"
                )
                scores_to_save[i] = nilai

        st.markdown("<br>", unsafe_allow_html=True)
        btn_simpan = st.form_submit_button("💾 Simpan Semua Nilai", use_container_width=True)

    # 3. LOGIKA SIMPAN
    if btn_simpan:
        try:
            cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
            for mod_num, score_val in scores_to_save.items():
                cur.execute("""
                    INSERT INTO module_scores (student_id, module, score)
                    VALUES (%s, %s, %s)
                """, (student_id, mod_num, score_val))
            conn.commit()
            st.success("✅ Nilai berhasil diperbarui!")
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"Gagal menyimpan: {e}")
        finally:
            conn.close()

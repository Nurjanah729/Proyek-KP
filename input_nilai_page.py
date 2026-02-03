import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### ⚡ Input Nilai Cepat (Klik & Pilih)")
    
    conn = get_db()
    cur = conn.cursor()

    # 1. PILIH MAHASISWA (Tetap pakai search agar cepat)
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

    # Ambil nilai lama untuk default
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    st.markdown("---")
    st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")

    # 2. RENTANG NILAI (Kelipatan 5 atau 10 biasanya paling sering dipakai)
    # Kita buat pilihan agar admin tinggal klik tanpa ngetik
    opsi_nilai = [0, 50, 60, 65, 70, 75, 80, 85, 90, 95, 100]

    final_scores = {}

    # Gunakan Container agar rapi
    with st.form("bulk_input"):
        for i in range(1, 11):
            default_val = existing_scores.get(i, 80) # Default ke 80 jika belum ada
            
            # Menggunakan radio horizontal agar admin tinggal KLIK
            final_scores[i] = st.radio(
                f"Modul {i}",
                options=opsi_nilai,
                index=opsi_nilai.index(default_val) if default_val in opsi_nilai else 5,
                horizontal=True,
                key=f"mod_{i}"
            )
            st.markdown("<hr style='margin:10px 0; opacity:0.2'>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 SIMPAN SEMUA NILAI SEKALIGUS", use_container_width=True)

    # 3. LOGIKA SIMPAN
    if submitted:
        try:
            cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
            for mod_num, score_val in final_scores.items():
                cur.execute("""
                    INSERT INTO module_scores (student_id, module, score)
                    VALUES (%s, %s, %s)
                """, (student_id, mod_num, score_val))
            conn.commit()
            st.success("✅ Nilai berhasil disimpan!")
            st.balloons()
        except Exception as e:
            conn.rollback()
            st.error(f"Gagal: {e}")
        finally:
            conn.close()

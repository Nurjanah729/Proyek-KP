import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### ⚡ Input Nilai Super Cepat (Mode Geser)")
    
    conn = get_db()
    cur = conn.cursor()

    # 1. PILIH MAHASISWA
    cur.execute("SELECT id, name, division, university FROM students ORDER BY name ASC")
    students = cur.fetchall()

    if not students:
        st.warning("⚠️ Belum ada data mahasiswa.")
        return

    student_map = {f"{s[1]} | {s[2]}": s[0] for s in students}
    selected_student = st.selectbox("Cari Mahasiswa", options=list(student_map.keys()), index=None, placeholder="🔍 Ketik nama...")

    if not selected_student:
        conn.close()
        return

    student_id = student_map[selected_student]
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    st.markdown("---")
    
    # 2. RENTANG NILAI (Hanya angka kepala yang sering muncul)
    # Ini membantu admin agar tidak perlu scroll/ngetik
    rentang_cepat = list(range(0, 101)) # 0 sampai 100 tersedia semua

    with st.form("form_anti_cape"):
        st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")
        
        scores_to_save = {}
        
        # Kita buat tampilan menyamping agar tidak banyak scroll ke bawah
        for i in range(1, 11):
            current_val = int(existing_scores.get(i, 80))
            
            # Pakai select_slider: Tinggal geser ke angka yang dimau
            # Sangat cepat, tidak ada "No Results", tidak perlu ngetik
            nilai = st.select_slider(
                f"Modul {i}",
                options=rentang_cepat,
                value=current_val,
                key=f"slide_{i}"
            )
            scores_to_save[i] = nilai
            st.markdown("<hr style='margin:5px 0; opacity:0.1'>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        btn_simpan = st.form_submit_button("💾 SIMPAN SEMUA NILAI SEKALIGUS", use_container_width=True)

    # 3. LOGIKA SIMPAN
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

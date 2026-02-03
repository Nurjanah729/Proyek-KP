import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 📝 Input Nilai (Mode Klik Cepat & Ketik Bebas)")
    
    conn = get_db()
    cur = conn.cursor()

    # 1. PILIH MAHASISWA
    cur.execute("SELECT id, name, division, university FROM students ORDER BY name ASC")
    students = cur.fetchall()

    if not students:
        st.warning("⚠️ Belum ada data mahasiswa.")
        return

    student_map = {f"{s[1]} | {s[2]}": s[0] for s in students}
    selected_student = st.selectbox("Cari Mahasiswa", options=list(student_map.keys()), index=None, placeholder="🔍 Cari nama...")

    if not selected_student:
        conn.close()
        return

    student_id = student_map[selected_student]
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    st.markdown("---")
    st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")

    # 2. LOGIKA INPUT NILAI
    # Gunakan form agar hemat reload
    with st.form("form_nilai_keren"):
        col1, col2 = st.columns(2)
        scores_to_save = {}

        for i in range(1, 11):
            target_col = col1 if i <= 5 else col2
            
            with target_col:
                st.write(f"**Modul {i}**")
                
                # Baris tombol pintasan agar tidak capek ngetik
                # Admin klik ini, angka di input_number bawahnya akan berubah
                quick_options = [60, 70, 80, 90, 100]
                
                # Ambil nilai awal dari DB
                val_awal = int(existing_scores.get(i, 80))

                # Kunci Utama: Gunakan number_input agar BISA DIKETIK BEBAS (87, 96, dll)
                nilai_akhir = st.number_input(
                    f"Nilai Modul {i}",
                    min_value=0, 
                    max_value=100, 
                    value=val_awal,
                    key=f"num_{i}",
                    label_visibility="collapsed"
                )
                
                st.caption("Pintasan: 60 | 70 | 80 | 90 | 100")
                scores_to_save[i] = nilai_akhir
                st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        btn_simpan = st.form_submit_button("💾 SIMPAN SEMUA NILAI", use_container_width=True)

    # 3. SIMPAN KE DATABASE
    if btn_simpan:
        try:
            cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
            for mod_num, score_val in scores_to_save.items():
                cur.execute("INSERT INTO module_scores (student_id, module, score) VALUES (%s, %s, %s)", 
                            (student_id, mod_num, int(score_val)))
            conn.commit()
            st.success("✅ Nilai berhasil disimpan!")
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"Gagal: {e}")
        finally:
            conn.close()

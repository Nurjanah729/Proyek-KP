import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 📝 Input Nilai Modul (Hybrid Mode)")
    st.info("Pilih angka yang tersedia atau pilih 'Lainnya...' untuk mengetik angka spesifik.")
    
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
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    st.markdown("---")
    
    # 2. DAFTAR PILIHAN CEPAT
    opsi_cepat = [100, 95, 90, 85, 80, 75, 70, 65, 60, 0, "Lainnya (Input Manual)"]

    with st.form("form_hybrid_nilai"):
        st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")
        
        col1, col2 = st.columns(2)
        scores_to_save = {}

        for i in range(1, 11):
            target_col = col1 if i <= 5 else col2
            current_val = existing_scores.get(i, 80)
            
            with target_col:
                st.markdown(f"**Modul {i}**")
                
                # Cek apakah nilai lama ada di pilihan cepat
                is_custom = current_val not in opsi_cepat[:-1]
                default_idx = opsi_cepat.index(current_val) if not is_custom else opsi_cepat.index("Lainnya (Input Manual)")

                # Pilih Cara Input
                pilihan = st.selectbox(
                    f"Pilih Nilai Modul {i}",
                    options=opsi_cepat,
                    index=default_idx,
                    key=f"sel_{i}",
                    label_visibility="collapsed"
                )

                # Jika pilih 'Lainnya', munculkan input angka
                if pilihan == "Lainnya (Input Manual)":
                    nilai_akhir = st.number_input(
                        f"Input Spesifik Modul {i}", 
                        0, 100, 
                        int(current_val) if is_custom else 80, 
                        key=f"num_{i}",
                        label_visibility="collapsed"
                    )
                else:
                    nilai_akhir = pilihan
                
                scores_to_save[i] = nilai_akhir
                st.markdown("<br>", unsafe_allow_html=True)

        btn_simpan = st.form_submit_button("💾 Simpan Semua Nilai", use_container_width=True)

    # 3. LOGIKA SIMPAN
    if btn_simpan:
        try:
            cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
            for mod_num, score_val in scores_to_save.items():
                cur.execute("INSERT INTO module_scores (student_id, module, score) VALUES (%s, %s, %s)", 
                            (student_id, mod_num, score_val))
            conn.commit()
            st.success("✅ Nilai berhasil diperbarui!")
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"Gagal: {e}")
        finally:
            conn.close()

import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    st.markdown("### 📝 Input Nilai (Pilih atau Ketik Langsung)")
    
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
    
    # 2. DAFTAR OPSI (Agar admin tidak scroll jauh)
    # Ini hanya sebagai bantuan, admin tetap bisa mengetik angka lain
    opsi_angka = ["0", "50", "60", "70", "75", "80", "85", "90", "95", "100"]

    with st.form("form_input_nilai"):
        st.write(f"📍 Mengisi nilai untuk: **{selected_student.split('|')[0]}**")
        
        col1, col2 = st.columns(2)
        scores_to_save = {}

        for i in range(1, 11):
            target_col = col1 if i <= 5 else col2
            current_val = str(existing_scores.get(i, 80)) # Default 80
            
            with target_col:
                # MENGGUNAKAN SELECTBOX YANG BISA DIKETIK
                # Admin bisa pilih 80, atau hapus dan ketik 87
                nilai_input = st.selectbox(
                    f"Modul {i}",
                    options=opsi_angka,
                    index=opsi_angka.index(current_val) if current_val in opsi_angka else None,
                    key=f"mod_{i}",
                    help="Pilih angka atau ketik angka bebas"
                )
                
                # Logika: Jika admin tidak pilih dari daftar tapi ngetik sendiri
                # Streamlit selectbox secara default akan menangkap teks yang diketik
                scores_to_save[i] = nilai_input

        st.markdown("<br>", unsafe_allow_html=True)
        btn_simpan = st.form_submit_button("💾 Simpan Semua Nilai", use_container_width=True)

    # 3. LOGIKA SIMPAN
    if btn_simpan:
        try:
            cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))
            for mod_num, score_val in scores_to_save.items():
                # Validasi agar inputan selalu angka
                try:
                    score_final = int(score_val)
                except:
                    score_final = 0 # Jika inputan aneh, set 0
                
                cur.execute("""
                    INSERT INTO module_scores (student_id, module, score)
                    VALUES (%s, %s, %s)
                """, (student_id, mod_num, score_final))
            
            conn.commit()
            st.success("✅ Nilai berhasil disimpan!")
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"Gagal: {e}")
        finally:
            conn.close()

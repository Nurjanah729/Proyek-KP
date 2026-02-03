import streamlit as st
import pandas as pd
from db import get_db

# ======================
# INPUT NILAI PAGE
# ======================
def input_nilai_page():
    st.markdown("""
    <div style="background-color:#f8fafc; padding:20px; border-radius:10px; border-left: 5px solid #3b82f6; margin-bottom:20px;">
        <h3 style="margin:0;">📝 Input Nilai Modul</h3>
        <p style="color:#64748b; margin:5px 0 0 0;">Pilih mahasiswa dan tentukan nilai untuk setiap modul</p>
    </div>
    """, unsafe_allow_html=True)

    conn = get_db()
    cur = conn.cursor()

    # ===============================
    # 1. PILIH MAHASISWA (SEARCHABLE)
    # ===============================
    cur.execute("""
        SELECT id, name, division, university
        FROM students
        ORDER BY name ASC
    """)
    students = cur.fetchall()

    if not students:
        st.warning("⚠️ Belum ada data mahasiswa di database.")
        conn.close()
        return

    # Buat map untuk label selectbox
    student_map = {
        f"{s[1]} | {s[2]} | {s[3]}": s[0]
        for s in students
    }

    selected_student = st.selectbox(
        "Pilih Mahasiswa",
        options=list(student_map.keys()),
        index=None,
        placeholder="🔍 Ketik nama untuk mencari...",
        help="Cari berdasarkan nama, divisi, atau universitas"
    )

    # Berhenti di sini jika mahasiswa belum dipilih
    if not selected_student:
        st.info("Silakan cari dan pilih mahasiswa untuk menampilkan form nilai.")
        conn.close()
        return

    student_id = student_map[selected_student]

    # Ambil nilai yang sudah ada di database (untuk auto-fill)
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    st.markdown("---")

    # ==================================
    # 2. FORM INPUT NILAI (SELECTBOX)
    # ==================================
    st.markdown(f"### 📊 Input Nilai: **{selected_student.split(' | ')[0]}**")
    
    # List pilihan angka 0-100
    opsi_nilai = list(range(0, 101))

    # Gunakan form agar aplikasi tidak reload setiap kali angka diubah
    with st.form("form_input_nilai"):
        col1, col2 = st.columns(2)
        
        scores_to_save = {}

        for modul in range(1, 11):
            # Modul 1-5 di kolom kiri, 6-10 di kolom kanan
            target_col = col1 if modul <= 5 else col2
            
            # Ambil nilai lama dari DB, jika belum ada default ke 75
            default_val = int(existing_scores.get(modul, 75))
            
            with target_col:
                # Pastikan default_val ada dalam opsi_nilai untuk menghindari error index
                if default_val not in opsi_nilai: default_val = 75
                
                nilai = st.selectbox(
                    f"Modul {modul}",
                    options=opsi_nilai,
                    index=opsi_nilai.index(default_val),
                    key=f"val_modul_{modul}"
                )
                scores_to_save[modul] = nilai

        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("💾 Simpan Perubahan Nilai")

    # ======================
    # 3. LOGIKA SIMPAN
    # ======================
    if submit_button:
        try:
            # Hapus data nilai lama mahasiswa ini
            cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))

            # Masukkan data nilai yang baru
            for module, score in scores_to_save.items():
                cur.execute("""
                    INSERT INTO module_scores (student_id, module, score)
                    VALUES (%s, %s, %s)
                """, (student_id, module, score))

            conn.commit()
            st.success(f"✅ Berhasil! Nilai untuk {selected_student.split(' | ')[0]} telah diperbarui.")
            st.rerun() # Refresh untuk update tabel di bawah
        except Exception as e:
            conn.rollback()
            st.error(f"Terjadi kesalahan saat menyimpan: {e}")
        finally:
            conn.close()

    st.markdown("---")

    # ======================
    # 4. TABEL REKAP NILAI
    # ======================
    conn = get_db()
    df_existing = pd.read_sql_query("""
        SELECT module AS Modul, score AS Nilai
        FROM module_scores
        WHERE student_id = %s
        ORDER BY CAST(module AS UNSIGNED) ASC
    """, conn, params=(student_id,))

    if not df_existing.empty:
        st.markdown("### 📋 Nilai Saat Ini di Database")
        st.dataframe(df_existing, use_container_width=True, hide_index=True)
    else:
        st.info("Mahasiswa ini belum memiliki nilai tersimpan.")

    conn.close()

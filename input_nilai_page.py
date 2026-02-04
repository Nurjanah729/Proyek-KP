import streamlit as st
import pandas as pd
from db import get_db

def input_nilai_page():
    # Header dengan Style Modern
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0B3C8C, #1E40AF); padding:20px; border-radius:15px; margin-bottom:25px;">
            <h2 style="color:white; margin:0;">📝 Input Nilai Modul</h2>
            <p style="color:rgba(255,255,255,0.8); margin:0;">Kelola performa akademik mahasiswa secara presisi</p>
        </div>
    """, unsafe_allow_html=True)

    conn = get_db()
    cur = conn.cursor()

    # =============================
    # 1. Pilih Mahasiswa (Dalam Card)
    # =============================
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        cur.execute("SELECT id, name, division, university FROM students ORDER BY name ASC")
        students = cur.fetchall()
        
        if not students:
            st.warning("⚠️ Belum ada data mahasiswa di database.")
            return

        student_map = {f"{s[1]} | {s[2]} ({s[3]})": s[0] for s in students}
        selected_student = st.selectbox(
            "Cari dan Pilih Mahasiswa",
            options=list(student_map.keys()),
            index=None,
            placeholder="Ketik nama mahasiswa..."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if not selected_student:
        st.info("💡 Pilih mahasiswa terlebih dahulu untuk mulai menginput nilai.")
        conn.close()
        return

    student_id = student_map[selected_student]
    nama_mhs = selected_student.split('|')[0].strip()

    # =============================
    # 2. Ambil nilai existing & Info Mahasiswa
    # =============================
    cur.execute("SELECT module, score FROM module_scores WHERE student_id = %s", (student_id,))
    existing_scores = dict(cur.fetchall())

    # Ringkasan Singkat (Metrics)
    avg_now = sum(existing_scores.values()) / len(existing_scores) if existing_scores else 0
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.success(f"📍 Sedang memproses: **{nama_mhs}**")
    with col2:
        st.metric("Rata-rata Saat Ini", f"{avg_now:.1f}")

    st.markdown("---")

    # =============================
    # 3. Form Input Nilai (Modern Editor)
    # =============================
    df_input = pd.DataFrame({
        "Modul": [f"Modul {i}" for i in range(1, 11)],
        "Nilai": [existing_scores.get(i, 0) for i in range(1, 11)]
    })

    with st.form("form_input_nilai"):
        st.markdown("##### 📊 Tabel Nilai Modul 1-10")
        
        # Data editor yang lebih profesional
        edited_df = st.data_editor(
            df_input,
            column_config={
                "Modul": st.column_config.TextColumn("Daftar Modul", disabled=True),
                "Nilai": st.column_config.NumberColumn(
                    "Nilai (0-100)",
                    min_value=0,
                    max_value=100,
                    step=1,
                    format="%d",
                    help="Input angka langsung antara 0 sampai 100"
                )
            },
            hide_index=True,
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tombol Simpan yang Menonjol
        submit_btn = st.form_submit_button("💾 SIMPAN PERUBAHAN NILAI", use_container_width=True)

        if submit_btn:
            try:
                # Hapus data lama
                cur.execute("DELETE FROM module_scores WHERE student_id = %s", (student_id,))

                # Insert data baru
                for _, row in edited_df.iterrows():
                    mod_num = int(row["Modul"].split(" ")[1])
                    nilai = int(row["Nilai"])

                    cur.execute(
                        "INSERT INTO module_scores (student_id, module, score) VALUES (%s, %s, %s)",
                        (student_id, mod_num, nilai)
                    )

                conn.commit()
                st.balloons()
                st.success(f"✅ Nilai untuk {nama_mhs} berhasil diperbarui!")
                st.rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Terjadi kesalahan: {e}")

    conn.close()

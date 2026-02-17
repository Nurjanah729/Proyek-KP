import streamlit as st
import pandas as pd
from ml_model import run_analysis
from db import get_db


# ======================
# HALAMAN ANALISIS NILAI
# ======================
def analisis_nilai_page():
    st.markdown("## 😎 Analisis Performa Akademik")
    st.markdown("Analisis performa mahasiswa menggunakan pendekatan **Machine Learning**")

    conn = get_db()
    cur = conn.cursor()

    # ======================
    # PILIH MAHASISWA
    # ======================
    cur.execute("""
        SELECT s.id, s.name, s.division, s.university
        FROM students s
        ORDER BY s.name ASC
    """)
    students = cur.fetchall()

    if not students:
        st.warning("Belum ada data mahasiswa.")
        conn.close()
        return

    student_map = {
    f"{s[0]} | {s[1]} | {s[2]} | {s[3]}": s[0]
    for s in students
    }


    selected_student = st.selectbox(
        "Pilih Mahasiswa",
        list(student_map.keys())
    )

    student_id = student_map[selected_student]
    

    # ======================
    # AMBIL NILAI MODUL
    # ======================
    cur.execute("""
        SELECT module, score
        FROM module_scores
        WHERE student_id = %s
        ORDER BY CAST(module AS UNSIGNED) ASC
    """, (student_id,))

    rows = cur.fetchall()

    if not rows:
        st.warning("Mahasiswa ini belum memiliki nilai.")
        conn.close()
        return

    df = pd.DataFrame(rows, columns=["Modul", "Nilai"])
    df["Modul"] = pd.to_numeric(df["Modul"])
    df["Nilai"] = pd.to_numeric(df["Nilai"])
    df = df.sort_values(by="Modul")

    st.table(df)

    # ======================
    # JALANKAN ANALISIS ML
    # ======================
    if st.button("🔍 Menjalankan Analisis", type="primary"):

        # 🔥 RUN RANDOM FOREST
        result, confidence, weak_modules, avg_score = run_analysis(df)

        # NORMALISASI LABEL (MODEL KAMU CUMA 2)
        hasil = "Excellent" if str(result).lower() == "excellent" else "Good"

        # ======================
        # SIMPAN KE DATABASE
        # ======================
        try:
            # hapus hasil lama biar tidak numpuk
            cur.execute(
                "DELETE FROM predictions WHERE student_id = %s",
                (student_id,)
            )

            cur.execute("""
                INSERT INTO predictions (student_id, result)
                VALUES (%s, %s)
            """, (student_id, hasil))

            conn.commit()

        except Exception as e:
            st.error(f"Gagal menyimpan hasil analisis: {e}")
            conn.close()
            return

        # ======================
        # TAMPILKAN HASIL
        # ======================
        st.success(f"✅ Hasil Analisis ML: **{hasil}**")
        st.write(f"📊 Confidence Model: {confidence}")
        st.write(f"📈 Rata-rata Nilai: {avg_score}")

        if weak_modules:
            st.warning(f"⚠ Modul lemah: {', '.join(map(str, weak_modules))}")
        else:
            st.info("🎉 Tidak ada modul lemah")

    conn.close()

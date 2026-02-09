import streamlit as st
import pandas as pd
from db import get_db
import io
from ml_model import run_analysis

# ==========================================
# 1. UI FIXED (TEKS PUTIH & TOMBOL KUNING)
# ==========================================
st.markdown("""
<style>
html, body, [data-testid="stWidgetLabel"] p, label, .stMarkdown p, h3, h2, h1, span {
    color: white !important;
    font-weight: 600 !important;
}
div.stButton > button {
    background-color: #FFCC00 !important;
    color: black !important;
    font-weight: bold !important;
    border: none !important;
    height: 48px;
    width: 100%;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI ML → SIMPAN KE predictions
# ==========================================
def analisis_ml_dan_simpan(student_id):
    conn = get_db()

    df = pd.read_sql("""
        SELECT module AS Modul, score AS Nilai
        FROM module_scores
        WHERE student_id = %s
        ORDER BY module
    """, conn, params=(student_id,))

    if df.empty:
        conn.close()
        return

    # JALANKAN MODEL ML
    prediction, confidence, weak_modules, avg_score = run_analysis(df)

    # LABEL SESUAI MODEL KAMU
    hasil = "Excellent" if str(prediction).lower() in ["excellent", "2"] else "Good"

    cur = conn.cursor()

    # HAPUS HASIL LAMA
    cur.execute("DELETE FROM predictions WHERE student_id = %s", (student_id,))

    # SIMPAN (SESUSAI STRUKTUR TABEL!)
    cur.execute("""
        INSERT INTO predictions (student_id, result)
        VALUES (%s, %s)
    """, (student_id, hasil))

    conn.commit()
    cur.close()
    conn.close()



# ==========================================
# 3. HALAMAN INPUT NILAI
# ==========================================
def input_nilai_page():
    st.title("📥 Import Nilai Mahasiswa")
    st.write("Unggah CSV/XLSX → nilai langsung dianalisis ML")
    st.divider()

    uploaded_file = st.file_uploader(
        "Pilih file (CSV/XLSX)",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                content = uploaded_file.getvalue().decode("utf-8")
                df = pd.read_csv(io.StringIO(content), sep=None, engine="python")
            else:
                df = pd.read_excel(uploaded_file)

            df.columns = df.columns.str.strip().str.lower()

            st.write("### Preview Data")
            st.dataframe(df.head())

            if st.button("Simpan Nilai"):
                conn = get_db()
                cur = conn.cursor()

                success = 0
                student_ids = set()

                for _, row in df.iterrows():
                    try:
                        s_id = int(str(row["student_id"]).replace("S", ""))
                        module = int(str(row["module"]).replace("modul", ""))
                        score = int(row["score"])

                        cur.execute("""
                            INSERT INTO module_scores (student_id, module, score)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE score = VALUES(score)
                        """, (s_id, module, score))

                        student_ids.add(s_id)
                        success += 1
                    except:
                        continue

                conn.commit()
                cur.close()
                conn.close()

                # 🔥 LANGSUNG JALANKAN ML
                for sid in student_ids:
                    analisis_ml_dan_simpan(sid)

                st.success(f"✅ {success} data disimpan ")
                st.balloons()

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ==========================================
# 4. MAIN
# ==========================================
if __name__ == "__main__":
    input_nilai_page()



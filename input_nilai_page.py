import streamlit as st
import pandas as pd
from db import get_db
import io # Tambahkan ini agar pembacaan file lebih stabil

# ==========================================
# 1. UI FIXED (TEKS PUTIH & TOMBOL KUNING)
# ==========================================
st.markdown("""
    <style>
    /* Paksa teks tetap putih */
    html, body, [data-testid="stWidgetLabel"] p, label, .stMarkdown p, h3, h2, h1, span {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Tombol Kuning Emas agar seragam dengan halaman Mahasiswa */
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
# 2. HALAMAN INPUT NILAI (ANTI-DATA MENUMPUK)
# ==========================================
def input_nilai_page():
    st.title("📥 Import Nilai Mahasiswa")
    st.write("Unggah berkas CSV untuk memperbarui nilai mahasiswa ID 1-5.")
    st.divider()

    uploaded_file = st.file_uploader("Pilih file (CSV/XLSX)", type=["csv", "xlsx"], key="final_uploader_nilai")

    if uploaded_file is not None:
        try:
            # PERBAIKAN: Gunakan pendeteksi kolom otomatis (sep=None)
            if uploaded_file.name.endswith('.csv'):
                content = uploaded_file.getvalue().decode('utf-8')
                df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
            else:
                df = pd.read_excel(uploaded_file)

            # Bersihkan nama kolom dari spasi dan huruf kapital
            df.columns = df.columns.str.strip().str.lower()

            st.write("### Preview Data:")
            st.dataframe(df.head())

            if st.button("Simpan Data Nilai"):
                conn = get_db()
                cur = conn.cursor()
                
                success_count = 0
                for _, row in df.iterrows():
                    try:
                        # Logika pembersihan ID Anda sudah bagus, kita pertahankan
                        raw_id = str(row['student_id']).upper().replace('S', '')
                        s_id = int(''.join(filter(str.isdigit, raw_id)))
                        
                        raw_mod = str(row['module']).lower().replace('modul', '').strip()
                        m_num = int(''.join(filter(str.isdigit, raw_mod)))
                        
                        s_score = int(row['score'])

                        # Simpan/Update Nilai ke tabel module_scores
                        cur.execute("""
                            INSERT INTO module_scores (student_id, module, score)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE score = VALUES(score)
                        """, (s_id, m_num, s_score))
                        success_count += 1
                    except:
                        continue
                
                conn.commit()
                cur.close()
                conn.close()
                
                st.success(f"✅ Berhasil menyimpan {success_count} data nilai!")
                st.balloons()

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {e}")

if __name__ == "__main__":
    input_nilai_page()

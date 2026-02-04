import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. UI CLEAN (KEMBALI KE PUTIH/DEFAULT)
# ==========================================
st.markdown("""
    <style>
    /* Mengembalikan warna teks ke default putih/terang */
    html, body, [data-testid="stWidgetLabel"] p, label, .stMarkdown p {
        color: white !important;
    }
    
    /* Tombol Biru agar tetap terlihat profesional */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        font-weight: bold !important;
        border: none;
        border-radius: 5px;
        height: 45px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. HALAMAN INPUT NILAI (KHUSUS IMPORT)
# ==========================================
def input_nilai_page():
    st.title("📥 Import Nilai Mahasiswa")
    st.write("Silakan unggah berkas CSV atau Excel untuk memperbarui nilai.")
    st.divider()

    # Langsung ke fitur Upload (Tanpa Tab/Tanpa Input Manual)
    uploaded_file = st.file_uploader("Pilih file (CSV/XLSX)", type=["csv", "xlsx"], key="final_uploader_nilai")

    if uploaded_file is not None:
        try:
            # Membaca file berdasarkan format
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.write("### Preview Data:")
            st.dataframe(df.head())

            if st.button("Simpan Data Nilai"):
                conn = get_db()
                cur = conn.cursor()
                
                success_count = 0
                for _, row in df.iterrows():
                    try:
                        # Membersihkan data dari teks (S001 -> 1)
                        raw_id = str(row['student_id']).upper().replace('S', '')
                        s_id = int(''.join(filter(str.isdigit, raw_id)))
                        
                        # Modul 1 -> 1
                        raw_mod = str(row['module']).lower().replace('modul', '').strip()
                        m_num = int(''.join(filter(str.isdigit, raw_mod)))
                        
                        s_score = int(row['score'])

                        # Simpan/Update Nilai
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
            st.error(f"❌ Terjadi kesalahan saat membaca file: {e}")

if __name__ == "__main__":
    input_nilai_page()

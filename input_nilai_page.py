import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. CSS FINAL: PAKSA TEKS HITAM PEKAT
# ==========================================
st.markdown("""
    <style>
    /* Mengunci teks agar tidak transparan dan tetap hitam pekat */
    html, body, [data-testid="stWidgetLabel"] p, .stTabs [data-baseweb="tab"] p, p, span, label {
        color: #000000 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* Box File Uploader agar kontras */
    [data-testid="stFileUploader"] {
        border: 2px solid #000000 !important;
        background-color: #FFFFFF !important;
        padding: 15px;
        border-radius: 10px;
    }

    /* Tombol Biru Solid */
    div.stButton > button {
        background-color: #0045AD !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        height: 50px;
        width: 100%;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI HALAMAN (DENGAN SESSION STATE)
# ==========================================
def input_nilai_page():
    st.title("📝 Manajemen Nilai Mahasiswa")
    st.divider()

    # MENGUNCI POSISI MENU AGAR TIDAK KEMBALI KE AWAL
    if 'menu_nilai' not in st.session_state:
        st.session_state.menu_nilai = "📥 Import Nilai Mahasiswa"

    # Navigasi menggunakan radio agar stabil saat upload file
    menu = st.radio("Pilih Metode:", ["📥 Import Nilai Mahasiswa", "✍️ Input Nilai Manual"], 
                    horizontal=True, key="nav_nilai_manual")

    if menu == "📥 Import Nilai Mahasiswa":
        st.subheader("Unggah Nilai Kolektif")
        
        # Menggunakan key unik agar file tidak hilang saat rerun
        uploaded_file = st.file_uploader("Pilih file Excel atau CSV", type=["csv", "xlsx"], key="file_nilai_uploader")

        if uploaded_file is not None:
            try:
                # Membaca file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                # Menampilkan preview data
                st.write("**Pratinjau Data:**")
                st.dataframe(df.head(), use_container_width=True)

                # Tombol Simpan
                if st.button("Simpan Data Nilai Ke Database"):
                    conn = get_db()
                    cur = conn.cursor()
                    
                    c_score = 0
                    c_student = 0
                    
                    for _, row in df.iterrows():
                        try:
                            # Membersihkan data
                            s_id = int(str(row['student_id']).upper().replace('S', ''))
                            m_num = int(str(row['module']).lower().replace('modul ', '').strip())
                            s_score = int(row['score'])
                            s_name = str(row['name']) if 'name' in df.columns else f"Mahasiswa {s_id}"

                            # 1. Pastikan Mahasiswa ada
                            cur.execute("SELECT id FROM students WHERE id = %s", (s_id,))
                            if not cur.fetchone():
                                cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s)", 
                                           (s_id, s_name, "Batch Import", "Mentor Source"))
                                c_student += 1

                            # 2. Simpan Nilai
                            cur.execute("""
                                INSERT INTO module_scores (student_id, module, score)
                                VALUES (%s, %s, %s)
                                ON DUPLICATE KEY UPDATE score = VALUES(score)
                            """, (s_id, m_num, s_score))
                            c_score += 1
                        except:
                            continue
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    st.success(f"✅ Sukses! {c_score} nilai disimpan.")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"Format file tidak sesuai: {e}")

    else:
        st.info("Fitur input manual dinonaktifkan sementara. Gunakan fitur Import CSV.")

# Jalankan
if __name__ == "__main__":
    input_nilai_page()

import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. CSS SUPREME (MENGUNCI WARNA HITAM)
# ==========================================
st.markdown("""
    <style>
    /* Mengunci teks di seluruh aplikasi agar tetap hitam pekat */
    * {
        color: #000000 !important;
    }
    
    /* Memastikan label di atas box input/upload terlihat sangat jelas */
    div[data-testid="stWidgetLabel"] p, label, .stMarkdown p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }

    /* Style khusus Box Upload agar tidak 'kosong' secara visual */
    [data-testid="stFileUploader"] {
        border: 2px solid #000000 !important;
        background-color: #F0F2F6 !important;
        padding: 10px;
        border-radius: 10px;
    }

    /* Tombol Biru Royal Solid */
    div.stButton > button {
        background-color: #0045AD !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: none !important;
        height: 50px !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI LOGIKA
# ==========================================
def generate_credentials(nama, s_id):
    u_name = f"vinix_{str(nama).lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 3. HALAMAN UTAMA (MAHASISWA & NILAI)
# ==========================================
def input_nilai_page():
    st.title("📝 Manajemen Nilai Mahasiswa")
    st.divider()

    # MENGGUNAKAN RADIO SEBAGAI NAVIGASI (AGAR TIDAK RESET)
    menu = st.radio("Pilih Operasi:", ["📥 Import Nilai (CSV/Excel)", "✍️ Input Nilai Manual"], 
                    horizontal=True, key="nav_nilai_unique")

    if menu == "📥 Import Nilai (CSV/Excel)":
        st.subheader("Unggah File Nilai")
        
        # KEY ADALAH KUNCI: Harus unik agar data tidak hilang saat rerun
        uploaded_file = st.file_uploader("Pilih berkas CSV atau Excel", type=["csv", "xlsx"], key="uploader_nilai_final")

        if uploaded_file is not None:
            try:
                # Baca file
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                
                st.write("**Pratinjau Data:**")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("🚀 Simpan Semua Nilai ke Database", key="btn_simpan_nilai"):
                    conn = get_db()
                    cur = conn.cursor()
                    
                    for _, row in df.iterrows():
                        try:
                            # Pembersihan ID (Contoh S001 jadi 1)
                            raw_id = str(row['student_id']).upper().replace('S', '')
                            s_id = int(''.join(filter(str.isdigit, raw_id)))
                            
                            # Modul 1 jadi 1
                            raw_mod = str(row['module']).lower().replace('modul', '').strip()
                            m_num = int(''.join(filter(str.isdigit, raw_mod)))
                            
                            s_score = int(row['score'])
                            s_name = str(row['name']) if 'name' in df.columns else f"Mahasiswa {s_id}"

                            # Simpan Mahasiswa Jika Belum Ada
                            cur.execute("INSERT IGNORE INTO students (id, name, division, university) VALUES (%s, %s, %s, %s)", 
                                       (s_id, s_name, "Batch Import", "Mentor Source"))

                            # Simpan Nilai
                            cur.execute("""
                                INSERT INTO module_scores (student_id, module, score)
                                VALUES (%s, %s, %s)
                                ON DUPLICATE KEY UPDATE score = VALUES(score)
                            """, (s_id, m_num, s_score))
                        except:
                            continue
                    
                    conn.commit()
                    st.success("✅ Data Berhasil Disinkronisasi!")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"Format file bermasalah: {e}")

    else:
        st.info("Fitur input manual ditiadakan untuk menjaga stabilitas data. Gunakan Import CSV.")

if __name__ == "__main__":
    input_nilai_page()

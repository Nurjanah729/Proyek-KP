import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. CSS ABSOLUT (SANGAT PENTING: TARUH PALING ATAS)
# ==========================================
st.markdown("""
    <style>
    /* Paksa semua teks label dan paragraf agar terlihat (Hitam Tajam) */
    /* Jika Anda ingin tetap putih, ganti #000000 menjadi #FFFFFF */
    html, body, [data-testid="stWidgetLabel"] p, label, .stMarkdown p {
        color: #000000 !important; 
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    
    /* Memperjelas area upload */
    [data-testid="stFileUploader"] {
        border: 2px solid #0045AD !important;
        background-color: #F8F9FA !important;
    }

    /* Tombol Kuning/Emas agar terlihat jelas seperti di gambar */
    div.stButton > button {
        background-color: #FFD700 !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        height: 45px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_credentials(nama, s_id):
    u_name = f"vinix_{str(nama).lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa")
    st.divider()

    # Gunakan radio agar navigasi tidak melompat ke awal
    menu = st.radio("Menu:", ["📊 Database", "📤 Unggah Berkas CSV"], horizontal=True, key="nav_mhs")

    if menu == "📤 Unggah Berkas CSV":
        st.subheader("Registrasi Kolektif via CSV")
        
        uploaded_file = st.file_uploader("Pilih Berkas CSV", type=["csv"], key="uploader_csv_final")

        if uploaded_file:
            try:
                # PERBAIKAN: Membaca CSV dengan deteksi delimiter otomatis
                # Ini mengatasi masalah "Berhasil mengimpor 0" karena format file yang tidak rapi
                df = pd.read_csv(uploaded_file, sep=None, engine='python')
                
                st.write("**Pratinjau Data Berkas:**")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("Konfirmasi & Simpan ke Database"):
                    conn = get_db()
                    cur = conn.cursor()
                    
                    success_count = 0
                    for _, row in df.iterrows():
                        try:
                            # Pastikan nama kolom sesuai dengan file Anda
                            sid = row['id']
                            sname = row['name']
                            sdiv = row['division']
                            suniv = row['university']
                            
                            uname, upass = generate_credentials(sname, sid)

                            # Insert ke database
                            cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                            cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                            
                            success_count += 1
                        except Exception as e:
                            continue

                    conn.commit()
                    conn.close()
                    
                    if success_count > 0:
                        st.success(f"Berhasil mengimpor {success_count} mahasiswa!")
                        st.balloons()
                    else:
                        st.error("Gagal mengimpor. Periksa apakah judul kolom di CSV sudah benar (id, name, division, university).")

            except Exception as e:
                st.error(f"File tidak terbaca: {e}")

if __name__ == "__main__":
    mahasiswa_page()

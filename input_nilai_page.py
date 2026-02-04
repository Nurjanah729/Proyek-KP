import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. CSS ABSOLUT (TEKS HITAM & LABEL JELAS)
# ==========================================
st.markdown("""
    <style>
    /* Paksa semua teks di seluruh aplikasi menjadi Hitam Pekat */
    * {
        color: #000000 !important;
    }
    
    /* Memperjelas Label di atas Box */
    div[data-testid="stWidgetLabel"] p, label {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        opacity: 1 !important;
    }

    /* Mempertegas area Upload */
    [data-testid="stFileUploader"] {
        border: 2px solid #0045AD !important;
        background-color: #F8F9FA !important;
        border-radius: 10px;
    }

    /* Tombol Biru Royal Solid */
    div.stButton > button {
        background-color: #0045AD !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        height: 50px !important;
        width: 100% !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_credentials(nama, s_id):
    u_name = f"vinix_{str(nama).lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. HALAMAN MAHASISWA (KHUSUS IMPORT)
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Database Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Menggunakan radio sebagai navigasi agar posisi tidak reset saat upload file
    menu = st.radio("Pilih Tampilan:", ["📊 Database Mahasiswa", "📤 Registrasi Kolektif (CSV)"], 
                    horizontal=True, key="nav_mahasiswa_final")

    if menu == "📊 Database Mahasiswa":
        st.subheader("Data Mahasiswa Terdaftar")
        cur.execute("""
            SELECT s.id, u.username, s.name, s.division, s.university 
            FROM students s 
            JOIN users u ON s.id = u.student_id 
            ORDER BY s.id DESC
        """)
        res = cur.fetchall()
        if res:
            df_display = pd.DataFrame(res, columns=["ID", "Username", "Nama", "Divisi", "Universitas"])
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data mahasiswa.")

    elif menu == "📤 Registrasi Kolektif (CSV)":
        st.subheader("Unggah Data Mahasiswa Baru")
        st.write("Pastikan kolom CSV: **id, name, division, university**")
        
        # Key unik 'uploader_mhs' menjaga file tidak hilang saat rerun
        uploaded_file = st.file_uploader("Pilih Berkas CSV", type=["csv"], key="uploader_mhs")

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("**Pratinjau Data:**")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("🚀 Proses & Simpan ke Database"):
                    count = 0
                    for _, row in df.iterrows():
                        try:
                            sid, sname, sdiv, suniv = row['id'], row['name'], row['division'], row['university']
                            uname, upass = generate_credentials(sname, sid)

                            # Simpan Mahasiswa
                            cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                            # Simpan Akun
                            cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                            count += 1
                        except:
                            continue
                    
                    conn.commit()
                    st.success(f"Berhasil menambahkan {count} mahasiswa!")
                    st.balloons()
            except Exception as e:
                st.error(f"Gagal membaca file: {e}")

    conn.close()

if __name__ == "__main__":
    mahasiswa_page()

import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. CSS FINAL: PAKSA TEKS HITAM & FIX VISUAL
# ==========================================
st.markdown("""
    <style>
    /* Mengunci semua teks agar tetap hitam tajam */
    html, body, [data-testid="stWidgetLabel"] p, .stTabs [data-baseweb="tab"] p {
        color: black !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    
    /* Memperjelas area drop file */
    [data-testid="stFileUploader"] {
        border: 2px dashed #0045AD !important;
        background-color: #F8F9FA !important;
        border-radius: 10px;
    }

    /* Tombol Biru Solid */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        font-weight: bold !important;
        height: 50px;
        width: 100%;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA NAVIGASI (AGAR TIDAK LONCAT)
# ==========================================
# Menginisialisasi session state untuk tab jika belum ada
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "📤 Unggah Berkas CSV"

def generate_credentials(nama, s_id):
    u_name = f"vinix_{str(nama).lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 3. INTERFACE UTAMA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # MENGGUNAKAN RADIO SEBAGAI NAVIGASI (JAUH LEBIH STABIL DARI ST.TABS)
    # Ini menjamin admin tidak akan terlempar ke halaman awal saat upload file
    menu = st.radio("Navigasi", ["📊 Database Mahasiswa", "📤 Unggah Berkas CSV"], 
                    horizontal=True, label_visibility="collapsed")

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
            st.info("Database masih kosong.")

    elif menu == "📤 Unggah Berkas CSV":
        st.subheader("Registrasi Kolektif via CSV")
        st.write("Pastikan CSV memiliki kolom: **id, name, division, university**")
        
        # Key unik untuk uploader agar state tersimpan
        uploaded_file = st.file_uploader("Pilih file CSV Anda", type=["csv"], key="uploader_final_step")

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("**Pratinjau Data Berkas:**")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("Konfirmasi & Simpan ke Database"):
                    success_count = 0
                    for _, row in df.iterrows():
                        try:
                            sid, sname, sdiv, suniv = row['id'], row['name'], row['division'], row['university']
                            uname, upass = generate_credentials(sname, sid)

                            # Simpan Data Mahasiswa
                            cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                            # Simpan Akun User
                            cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                            
                            success_count += 1
                        except:
                            continue

                    conn.commit()
                    st.success(f"Berhasil mengimpor {success_count} mahasiswa!")
                    # Tetap di halaman ini, tidak pindah ke database otomatis
            except Exception as e:
                st.error(f"Format CSV salah: {e}")

    conn.close()

if __name__ == "__main__":
    mahasiswa_page()


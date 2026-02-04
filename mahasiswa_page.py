import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. UI LOCK (TEKS HITAM & LABEL JELAS)
# ==========================================
st.markdown("""
    <style>
    /* Memaksa semua teks dan label di atas box menjadi hitam pekat */
    html, body, [data-testid="stWidgetLabel"] p, .stTabs [data-baseweb="tab"] p {
        color: #000000 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    
    /* Box Upload: Border dipertegas agar terlihat jelas */
    [data-testid="stFileUploader"] {
        border: 2px dashed #0045AD;
        padding: 10px;
        border-radius: 10px;
    }

    /* Tombol Biru Profesional */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px;
        width: 100%;
        height: 50px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_credentials(nama, s_id):
    # Logika pembuatan username & password otomatis
    u_name = f"vinix_{str(nama).lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. HALAMAN UTAMA (KHUSUS IMPORT CSV)
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa (CSV)")
    st.info("Halaman ini khusus untuk pendaftaran mahasiswa secara kolektif menggunakan berkas CSV.")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    tab_arsip, tab_upload = st.tabs(["📊 Database Mahasiswa", "📤 Unggah Berkas CSV"])

    # --- TAB 1: LIHAT DATA ---
    with tab_arsip:
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
            st.warning("Belum ada data mahasiswa di database.")

    # --- TAB 2: PROSES CSV ---
    with tab_upload:
        st.subheader("Tambah Mahasiswa via CSV")
        st.markdown("""
        **Format Kolom CSV Wajib:**
        `id`, `name`, `division`, `university`
        """)
        
        uploaded_file = st.file_uploader("Pilih Berkas CSV Mahasiswa", type=["csv"], key="csv_uploader_final")

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("**Pratinjau Data:**")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("Daftarkan Semua Mahasiswa Sekarang"):
                    success_count = 0
                    for _, row in df.iterrows():
                        try:
                            sid = int(row['id'])
                            sname = str(row['name'])
                            sdiv = str(row['division'])
                            suniv = str(row['university'])
                            
                            # Buat Akun Otomatis
                            uname, upass = generate_credentials(sname, sid)

                            # Simpan ke Tabel Students
                            cur.execute("""
                                INSERT INTO students (id, name, division, university) 
                                VALUES (%s, %s, %s, %s) 
                                ON DUPLICATE KEY UPDATE name=VALUES(name), division=VALUES(division), university=VALUES(university)
                            """, (sid, sname, sdiv, suniv))

                            # Simpan ke Tabel Users
                            cur.execute("""
                                INSERT INTO users (username, password, role, student_id) 
                                VALUES (%s, %s, %s, %s) 
                                ON DUPLICATE KEY UPDATE username=VALUES(username)
                            """, (uname, upass, "mahasiswa", sid))
                            
                            success_count += 1
                        except Exception as e:
                            st.error(f"Gagal memproses baris {sname}: {e}")

                    conn.commit()
                    st.success(f"Berhasil memproses {success_count} data mahasiswa!")
                    st.balloons()
            
            except Exception as e:
                st.error(f"Gagal membaca file: {e}")

    conn.close()

if __name__ == "__main__":
    mahasiswa_page()

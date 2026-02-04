import streamlit as st
import pandas as pd
from db import get_db
import io

# ==========================================
# 1. FIX INTERFACE: TEKS PUTIH & TOMBOL KUNING
# ==========================================
st.markdown("""
    <style>
    /* Paksa teks agar SELALU PUTIH dan terlihat jelas */
    html, body, [data-testid="stWidgetLabel"] p, label, .stMarkdown p, h3, h2, h1, span {
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px black;
    }
    
    /* Input file uploader tetap kontras */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px dashed #FFD700;
        border-radius: 10px;
    }

    /* Tombol Kuning Emas sesuai gambar Anda */
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

def generate_credentials(nama, s_id):
    u_name = f"vinix_{str(nama).lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. HALAMAN MAHASISWA (FIX CSV & INTERFACE)
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa")
    st.divider()

    # Navigasi Horizontal yang Stabil
    menu = st.radio("Pilih Menu:", ["📊 Database Mahasiswa", "📤 Unggah Berkas CSV"], 
                    horizontal=True, key="nav_fix_final")

    conn = get_db()
    cur = conn.cursor()

    if menu == "📤 Unggah Berkas CSV":
        st.subheader("Registrasi Kolektif via CSV")
        st.info("Pastikan CSV memiliki kolom: id, name, division, university")
        
        uploaded_file = st.file_uploader("Pilih Berkas CSV Anda", type=["csv"], key="uploader_final")

        if uploaded_file is not None:
            try:
                # FIX CSV: Membaca file dan memaksa pemisahan kolom jika menumpuk
                content = uploaded_file.getvalue().decode('utf-8')
                df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
                
                # Membersihkan spasi pada nama kolom
                df.columns = df.columns.str.strip()

                st.write("### Pratinjau Data Berkas:")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("Konfirmasi & Simpan ke Database"):
                    success_count = 0
                    for _, row in df.iterrows():
                        try:
                            # Mengambil data dengan nama kolom yang dibersihkan
                            sid = row['id']
                            sname = row['name']
                            sdiv = row['division']
                            suniv = row['university']
                            
                            uname, upass = generate_credentials(sname, sid)

                            # 1. Simpan ke tabel students
                            cur.execute("""
                                INSERT INTO students (id, name, division, university) 
                                VALUES (%s, %s, %s, %s) 
                                ON DUPLICATE KEY UPDATE name=VALUES(name)
                            """, (sid, sname, sdiv, suniv))
                            
                            # 2. Simpan ke tabel users
                            cur.execute("""
                                INSERT INTO users (username, password, role, student_id) 
                                VALUES (%s, %s, %s, %s) 
                                ON DUPLICATE KEY UPDATE username=VALUES(username)
                            """, (uname, upass, "mahasiswa", sid))
                            
                            success_count += 1
                        except Exception as e:
                            continue

                    conn.commit()
                    if success_count > 0:
                        st.success(f"✅ Berhasil mengimpor {success_count} mahasiswa!")
                        st.balloons()
                    else:
                        st.error("❌ Gagal mengimpor. Pastikan judul kolom di CSV Anda tepat: id, name, division, university")

            except Exception as e:
                st.error(f"Terjadi kesalahan pembacaan CSV: {e}")

    else:
        # Tampilan Database Mahasiswa
        st.subheader("Database Terdaftar")
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id DESC")
        res = cur.fetchall()
        if res:
            st.table(pd.DataFrame(res, columns=["ID", "Nama", "Divisi", "Universitas"]))

    conn.close()

if __name__ == "__main__":
    mahasiswa_page()

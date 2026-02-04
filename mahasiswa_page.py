import streamlit as st
import pandas as pd
from db import get_db
import io

# ==========================================
# 1. FIX INTERFACE: TEKS PUTIH & TOMBOL KUNING
# ==========================================
st.markdown("""
    <style>
    /* Mengunci teks agar SELALU PUTIH */
    html, body, [data-testid="stWidgetLabel"] p, label, .stMarkdown p, h3, h2, h1, span {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Area upload file */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.05);
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
# 2. FUNGSI UTAMA (FIX CSV & IMPORT)
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa")
    st.divider()

    # Navigasi tetap di tempat
    menu = st.radio("Pilih Menu:", ["📊 Database Mahasiswa", "📤 Unggah Berkas CSV"], 
                    horizontal=True, key="nav_final_stable")

    conn = get_db()
    cur = conn.cursor()

    if menu == "📤 Unggah Berkas CSV":
        st.subheader("Registrasi Kolektif via CSV")
        
        uploaded_file = st.file_uploader("Pilih Berkas CSV", type=["csv"], key="uploader_csv_v3")

        if uploaded_file is not None:
            try:
                # SOLUSI CSV MENUMPUK: Membaca mentah lalu memaksa split
                content = uploaded_file.getvalue().decode('utf-8')
                # Menggunakan sep=None dan engine='python' untuk deteksi otomatis pemisah (koma/titik koma)
                df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
                
                # Membersihkan nama kolom dari spasi atau karakter aneh
                df.columns = df.columns.str.strip().str.lower()

                st.write("### Pratinjau Data (Pastikan sudah terbagi kolom):")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("Konfirmasi & Simpan ke Database"):
                    success_count = 0
                    # Memastikan kolom yang dibutuhkan ada
                    required = ['id', 'name', 'division', 'university']
                    if all(col in df.columns for col in required):
                        for _, row in df.iterrows():
                            try:
                                sid, sname = row['id'], row['name']
                                sdiv, suniv = row['division'], row['university']
                                uname, upass = generate_credentials(sname, sid)

                                # Simpan ke students & users
                                cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                                cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                                success_count += 1
                            except: continue
                        
                        conn.commit()
                        st.success(f"✅ Berhasil mengimpor {success_count} mahasiswa!")
                        st.balloons()
                    else:
                        st.error(f"❌ Header CSV salah. Harus ada: {', '.join(required)}. Kolom terbaca: {', '.join(df.columns)}")

            except Exception as e:
                st.error(f"Gagal membaca CSV: {e}")

    else:
        # Tampilan Database
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id DESC")
        res = cur.fetchall()
        if res:
            st.table(pd.DataFrame(res, columns=["ID", "Nama", "Divisi", "Universitas"]))

    conn.close()

if __name__ == "__main__":
    mahasiswa_page()

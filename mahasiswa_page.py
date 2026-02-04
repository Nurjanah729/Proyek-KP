import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. UI LOCK (TEKS HITAM & LABEL JELAS)
# ==========================================
st.markdown("""
    <style>
    /* Memaksa semua teks dan label menjadi hitam pekat */
    html, body, [data-testid="stWidgetLabel"] p, .stTabs [data-baseweb="tab"] p {
        color: #000000 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    
    /* Box Input: Border dipertegas agar kontras */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border: 1.5px solid #333333 !important;
        background-color: white !important;
    }

    /* Tombol Biru Profesional */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px;
        width: 100%;
        height: 48px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA DATA (UNIVERSITAS DARI CSV)
# ==========================================
@st.cache_data
def get_univ_list():
    try:
        # Membaca file yang Anda unggah
        df = pd.read_csv("universitas_indonesia.csv")
        return sorted(df['nama_universitas'].dropna().unique().tolist())
    except:
        # Cadangan jika file tidak terbaca
        return ["Universitas Indonesia", "Institut Teknologi Bandung", "Universitas Gadjah Mada"]

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 3. HALAMAN UTAMA (STABIL & BERSIH)
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Manajemen Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Menggunakan key agar tab tidak reset
    tab1, tab2, tab3 = st.tabs(["📊 Database", "📤 Import Kolektif", "✍️ Tambah Mahasiswa"])

    with tab1:
        st.subheader("Daftar Mahasiswa")
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id DESC")
        res = cur.fetchall()
        if res:
            df = pd.DataFrame(res, columns=["ID", "Nama", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Import Massal")
        st.file_uploader("Pilih Berkas CSV", type=["csv"], key="uploader_final")

    with tab3:
        st.subheader("Tambah Mahasiswa Baru")
        
        # Grid Input: Teks di atas box (Label) DIJAMIN muncul
        col1, col2 = st.columns(2)
        
        with col1:
            nama_m = st.text_input("Nama Lengkap", placeholder="Masukkan nama...", key="f_nama")
            div_m = st.selectbox("Divisi Penempatan", ["Web Developer", "Data Science", "AI Engineer"], key="f_div")
        
        with col2:
            # Mengambil data dari universitas_indonesia.csv
            univ_data = get_univ_list()
            univ_m = st.selectbox("Asal Universitas", options=["-- Pilih Universitas --"] + univ_data, key="f_univ")

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Simpan Data Mahasiswa"):
            if nama_m and univ_m != "-- Pilih Universitas --":
                try:
                    # 1. Simpan ke tabel students
                    cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                    conn.commit()
                    
                    # 2. Ambil ID dan buat akun login
                    new_id = cur.lastrowid
                    u, p = generate_credentials(nama_m, new_id)
                    cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                    conn.commit()
                    
                    st.success(f"Berhasil! Mahasiswa {nama_m} telah terdaftar.")
                    st.info(f"Kredensial Login -> User: {u} | Pass: {p}")
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.warning("Mohon isi Nama Lengkap dan pilih Universitas.")

    conn.close()

# Jalankan fungsi
if __name__ == "__main__":
    mahasiswa_page()

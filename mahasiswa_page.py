import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. CSS AGRESIF (MEMAKSA TEKS TETAP HITAM)
# ==========================================
st.markdown("""
    <style>
    /* Mengunci warna teks global agar tidak berubah saat rerun */
    html, body, [data-testid="stWidgetLabel"], p, span, label {
        color: #111111 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Memastikan teks Tab tetap hitam pekat dan tebal */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #111111 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }

    /* Styling Box Input agar border terlihat jelas */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border: 1px solid #B0B0B0 !important;
        background-color: #FFFFFF !important;
        color: #111111 !important;
        border-radius: 8px !important;
    }

    /* Tombol Biru Royal Profesional */
    div.stButton > button {
        background-color: #0045AD !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def get_univ_data():
    try:
        df = pd.read_csv("universitas_indonesia.csv")
        return sorted(df['nama_universitas'].dropna().unique().tolist())
    except Exception as e:
        st.error(f"Gagal memuat file universitas: {e}")
        return []

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. HALAMAN UTAMA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Kelola Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    tab1, tab2, tab3 = st.tabs(["📊 Database", "📤 Import Kolektif", "➕ Tambah Manual"])

    with tab1:
        st.subheader("Data Mahasiswa Terdaftar")
        cur.execute("SELECT s.id, u.username, s.name, s.division, s.university FROM students s JOIN users u ON s.id = u.student_id ORDER BY s.id DESC")
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Username", "Nama", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Import Massal")
        uploaded_file = st.file_uploader("Pilih Berkas CSV/XLSX", type=["csv", "xlsx"])
        # Logika import file tetap ada di sini...

    # --- PERBAIKAN TOTAL TAB MANUAL ---
    with tab3:
        st.subheader("Registrasi Mahasiswa Baru")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nama_m = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap...", key="form_nama")
            div_m = st.selectbox("Divisi Penempatan", ["Web Developer", "Data Science", "AI Engineer"], key="form_div")
        
        with col2:
            # Mengambil list dari CSV
            list_univ = get_univ_data()
            pilihan_univ = st.selectbox(
                "Asal Universitas", 
                options=["Pilih Universitas"] + list_univ + ["➕ Input Manual"],
                key="form_univ_select"
            )
            
            # Logika Input Manual agar label TIDAK hilang saat diklik
            univ_m = ""
            if pilihan_univ == "➕ Input Manual":
                # Label ini sekarang dipaksa hitam oleh CSS di atas
                univ_m = st.text_input("Ketik Nama Universitas", placeholder="Input manual di sini...", key="form_univ_manual")
            elif pilihan_univ != "Pilih Universitas":
                univ_m = pilihan_univ

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Simpan Data Mahasiswa"):
            if nama_m and univ_m:
                try:
                    # Simpan ke tabel students
                    cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                    conn.commit()
                    
                    # Generate Akun
                    new_id = cur.lastrowid
                    u, p = generate_credentials(nama_m, new_id)
                    cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                    conn.commit()
                    
                    st.success(f"Mahasiswa {nama_m} berhasil didaftarkan!")
                    st.info(f"Kredensial Login -> User: {u} | Pass: {p}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan: {e}")
            else:
                st.warning("Mohon lengkapi seluruh kolom input di atas.")

    conn.close()

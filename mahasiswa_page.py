import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. STYLE AGAR TEKS PASTI TERLIHAT (HITAM)
# ==========================================
st.markdown("""
    <style>
    /* Mengunci teks agar tetap hitam pekat */
    html, body, [data-testid="stWidgetLabel"], p, label {
        color: #111111 !important;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #111111 !important;
        font-weight: 700 !important;
    }
    /* Style tombol biru */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        font-weight: bold !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA DATA & SESSION (AGAR TIDAK RESET)
# ==========================================
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

@st.cache_data
def get_univ_list():
    try:
        df = pd.read_csv("universitas_indonesia.csv")
        return sorted(df['nama_universitas'].dropna().unique().tolist())
    except:
        return ["Universitas Indonesia", "Institut Teknologi Bandung"]

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 3. INTERFACE UTAMA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Kelola Data Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Menggunakan session_state agar saat pilih "Input Manual", Tab tidak balik ke awal
    tabs = ["📊 Database", "📥 Import Kolektif", "✍️ Tambah Manual"]
    
    # Logic agar tab tetap di posisi saat ini
    tab1, tab2, tab3 = st.tabs(tabs)

    # --- TAB 1 & 2 (Daftar & Import) ---
    with tab1:
        st.subheader("Daftar Mahasiswa")
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id DESC")
        res = cur.fetchall()
        if res:
            st.dataframe(pd.DataFrame(res, columns=["ID", "Nama", "Divisi", "Universitas"]), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Import Massal")
        st.file_uploader("Upload CSV", type=["csv"], key="uploader")

    # --- TAB 3: TAMBAH MANUAL (TARGET PERBAIKAN) ---
    with tab3:
        st.subheader("Registrasi Mahasiswa Baru")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Teks label di atas box tetap ada
            nama_m = st.text_input("Nama Lengkap Mahasiswa", placeholder="Contoh: Andi Pratama", key="input_nama")
            div_m = st.selectbox("Divisi", ["Web Developer", "Data Science", "AI Engineer"], key="input_div")

        with col2:
            # Mengambil data dari universitas_indonesia.csv
            univ_data = get_univ_list()
            
            # Selectbox Universitas
            pilihan_univ = st.selectbox(
                "Pilih Universitas", 
                options=["-- Pilih --"] + univ_data + ["➕ Input Manual"],
                key="univ_select" # Key ini penting agar tidak reset
            )

            # BOX TEKS TAMBAHAN: Muncul otomatis di bawah selectbox tanpa pindah halaman
            univ_final = ""
            if pilihan_univ == "➕ Input Manual":
                univ_final = st.text_input("Ketik Nama Universitas Baru", placeholder="Masukkan nama universitas...", key="univ_manual_box")
            elif pilihan_univ != "-- Pilih --":
                univ_final = pilihan_univ

        st.write("") # Spasi
        
        if st.button("Simpan Data Mahasiswa", key="btn_save_final"):
            if nama_m and univ_final:
                try:
                    cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_final))
                    conn.commit()
                    
                    new_id = cur.lastrowid
                    u, p = generate_credentials(nama_m, new_id)
                    cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                    conn.commit()
                    
                    st.success(f"Berhasil Terdaftar! User: {u}")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Pastikan semua kolom (Nama & Universitas) sudah terisi.")

    conn.close()

# Panggil fungsi
if __name__ == "__main__":
    mahasiswa_page()

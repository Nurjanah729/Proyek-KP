import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. UI ENGINE (HIGH CONTRAST & CLEAN)
# ==========================================
st.markdown("""
    <style>
    /* 1. Paksa Latar Belakang Putih */
    .stApp { background-color: #FFFFFF !important; }

    /* 2. Paksa SEMUA teks (Tab, Label, Input) berwarna HITAM PEKAT */
    * { color: #000000 !important; }
    
    /* 3. Perbaikan TAB agar terlihat jelas tanpa klik */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #F0F2F6 !important;
        margin-right: 5px !important;
        border-radius: 5px 5px 0 0 !important;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px !important;
        font-weight: 800 !important;
    }

    /* 4. Menghilangkan Teks Label di atas Box Input */
    div[data-testid="stWidgetLabel"] { display: none !important; }

    /* 5. Mempertegas Box Input (Border Abu-abu Gelap) */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border: 2px solid #333333 !important; 
        border-radius: 6px !important;
        height: 45px !important;
    }

    /* 6. Perbaikan Tombol (Biru Royal, Teks Putih) */
    div.stButton > button {
        background-color: #0045AD !important;
        color: #FFFFFF !important; /* Paksa teks tombol tetap putih */
        border: none !important;
        font-weight: 700 !important;
        width: 100% !important;
        height: 48px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. HALAMAN UTAMA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Manajemen Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    tab_list, tab_import, tab_manual = st.tabs([
        "📊 Database", "📤 Import Kolektif", "➕ Tambah Manual"
    ])

    # --- TAB 1: DATABASE ---
    with tab_list:
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id DESC")
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Nama", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 2: IMPORT KOLEKTIF ---
    with tab_import:
        st.subheader("Registrasi via File")
        # Tooltip menggantikan teks manual
        uploaded_file = st.file_uploader("", type=["csv", "xlsx"], help="Format: id, name, division, university")
        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                if st.button("Proses Data Kolektif"):
                    for _, row in df_up.iterrows():
                        sid, sname, sdiv, suniv = row['id'], row['name'], row['division'], row['university']
                        u, p = generate_credentials(sname, sid)
                        cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                        cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (u, p, "mahasiswa", sid))
                    conn.commit()
                    st.success("Selesai.")
                    st.rerun()
            except Exception as e: st.error(f"Gagal: {e}")

    # --- TAB 3: PENDAFTARAN MANUAL (TANPA CSV UNIV) ---
    with tab_manual:
        st.subheader("Input Data Mahasiswa Baru")
        
        col1, col2 = st.columns(2)
        with col1:
            nama_m = st.text_input("N1", placeholder="Nama Lengkap", key="m1")
            div_m = st.selectbox("D1", ["Web Developer", "Data Science", "AI Engineer"], key="m2")
        
        with col2:
            # Universitas murni input manual tanpa file eksternal
            univ_m = st.text_input("U1", placeholder="Asal Universitas / Instansi", key="m3")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Simpan ke Database", key="m4"):
            if nama_m and univ_m:
                try:
                    cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                    conn.commit()
                    new_id = cur.lastrowid
                    u, p = generate_credentials(nama_m, new_id)
                    cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                    conn.commit()
                    st.success(f"Berhasil! User: {u}")
                except Exception as e: st.error(f"Database Error: {e}")
            else:
                st.warning("Kotak input tidak boleh kosong.")

    conn.close()

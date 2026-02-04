import streamlit as st
import pandas as pd
from db import get_db

# ==========================================
# 1. UI ENGINE (PROFESSIONAL LIGHT MODE)
# ==========================================
st.markdown("""
    <style>
    /* Paksa teks Tab berwarna hitam pekat dan tebal agar terlihat jelas */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }
    
    /* MENGHILANGKAN SEMUA LABEL DI ATAS BOX INPUT */
    div[data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* Mempertegas tampilan box input */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border: 1.5px solid #DDE1E6 !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 6px !important;
        height: 48px !important;
    }

    /* TOMBOL SIMPAN: Biru Royal Solid (Bukan Kuning/Hitam) */
    div.stButton > button {
        background-color: #0045AD !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        width: 100% !important;
        height: 50px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #002D70 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. CORE LOGIC & INTERFACE
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Administrasi Mahasiswa")
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Tab dengan label yang dipaksa terlihat hitam
    tab_list, tab_import, tab_manual = st.tabs([
        "📊 Database Utama", 
        "📤 Registrasi Kolektif", 
        "➕ Pendaftaran Manual"
    ])

    # --- TAB 1: DATABASE ---
    with tab_list:
        cur.execute("""
            SELECT s.id, u.username, s.name, s.division, s.university 
            FROM students s 
            JOIN users u ON s.id = u.student_id 
            WHERE u.role = 'mahasiswa' 
            ORDER BY s.id DESC
        """)
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Username", "Nama", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Database kosong.")

    # --- TAB 2: IMPORT KOLEKTIF ---
    with tab_import:
        st.write("### Unggah Laporan Data")
        # Format kolom dipindahkan ke help agar tampilan bersih
        uploaded_file = st.file_uploader("", type=["csv", "xlsx"], 
                                         help="Header wajib: id, name, division, university")
        
        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                df_up.columns = [c.strip().lower() for c in df_up.columns]
                
                # Cek Kolom
                required = ['id', 'name', 'division', 'university']
                if all(col in df_up.columns for col in required):
                    st.dataframe(df_up.head(5), use_container_width=True)
                    if st.button("Daftarkan Semua Data", key="btn_bulk"):
                        for _, row in df_up.iterrows():
                            sid, sname = int(row['id']), str(row['name'])
                            sdiv, suniv = str(row['division']), str(row['university'])
                            uname, upass = generate_credentials(sname, sid)
                            cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                            cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                        conn.commit()
                        st.success("Sinkronisasi database berhasil.")
                        st.rerun()
                else:
                    st.error(f"Kolom tidak sesuai. Dibutuhkan: {', '.join(required)}")
            except Exception as e:
                st.error(f"Kesalahan file: {e}")

    # --- TAB 3: PENDAFTARAN MANUAL (CLEAN UI) ---
    with tab_manual:
        st.write("### Registrasi Mahasiswa Baru")
    
        col1, col2 = st.columns(2)
    
        # ===== KOLOM KIRI =====
        with col1:
            st.markdown("**Nama Lengkap**")
            nama_m = st.text_input(
                "",
                placeholder="Masukkan nama lengkap",
                key="in_nama"
            )
    
            st.markdown("**Divisi**")
            div_m = st.selectbox(
                "",
                ["Web Developer", "Data Science", "AI Engineer"],
                key="in_div"
            )
    
        # ===== KOLOM KANAN =====
        with col2:
            st.markdown("**Universitas**")
            univ_p = st.selectbox(
                "",
                options=[
                    "Universitas Indonesia",
                    "Institut Teknologi Bandung",
                    "➕ Input Manual"
                ],
                index=None,
                placeholder="Pilih Universitas",
                key="in_univ_s"
            )
    
            if univ_p == "➕ Input Manual":
                st.markdown("**Nama Universitas**")
                univ_m = st.text_input(
                    "",
                    placeholder="Ketik nama universitas",
                    key="in_univ_t"
                )
            else:
                univ_m = univ_p


        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Simpan ke Database", key="in_save"):
            if nama_m and univ_m:
                try:
                    cur.execute("INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", (nama_m, div_m, univ_m))
                    conn.commit()
                    new_id = cur.lastrowid
                    u, p = generate_credentials(nama_m, new_id)
                    cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", (u, p, "mahasiswa", new_id))
                    conn.commit()
                    st.success(f"Berhasil! Akun: {u} | Sandi: {p}")
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.warning("Mohon isi semua data di dalam box.")

    conn.close()


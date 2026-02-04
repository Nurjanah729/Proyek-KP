import streamlit as st
import pandas as pd
from db import get_db
import random

# ==========================================
# 1. UI CUSTOMIZATION (CLEAN LIGHT MODE)
# ==========================================
st.markdown("""
    <style>
    /* Latar belakang halaman putih bersih */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Warna Tab yang tegas dan kontras */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 2px solid #F0F2F6;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        color: #4A4A4A !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0045AD !important;
        border-bottom: 3px solid #0045AD !important;
    }

    /* Styling Input Box */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: #F8F9FA !important;
        border: 1px solid #E9ECEF !important;
        color: #212529 !important;
        border-radius: 8px !important;
    }

    /* Tombol Utama */
    div.stButton > button {
        background-color: #0045AD !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 1rem;
    }
    div.stButton > button:hover {
        background-color: #003385 !important;
        box-shadow: 0 4px 12px rgba(0,69,173,0.2);
    }

    /* Label styling */
    .custom-label {
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 8px;
        display: block;
        font-size: 14px;
    }
    
    /* Manual input container */
    .manual-input-box {
        padding: 1.5rem;
        background-color: #F8FAFC;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-top: 1rem;
    }
    
    /* Section spacing */
    .form-section {
        margin-bottom: 1.5rem;
    }
    
    /* Required field indicator */
    .required::after {
        content: " *";
        color: #E74C3C;
    }
    
    /* Info box */
    .info-box {
        background-color: #E8F4FC;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid #3498DB;
        margin-top: 1rem;
        font-size: 14px;
    }
    
    /* Fix for form state persistence */
    .stSelectbox div[data-baseweb="select"] {
        z-index: 999 !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def get_list_universitas():
    try:
        df = pd.read_csv("universitas_indonesia.csv")
        list_univ = sorted(df['nama_universitas'].dropna().unique().tolist())
        list_univ.append("➕ Input Manual")
        return list_univ
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return ["➕ Input Manual"]

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. MAIN INTERFACE - ENTRI MANDIRI TAB
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Manajemen Mahasiswa")
    st.markdown("<p style='color: #6C757D; font-size: 1.1em;'>Sistem administrasi pusat untuk pengelolaan data mahasiswa dan kredensial akses.</p>", unsafe_allow_html=True)
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Inisialisasi session state untuk form
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'nama': '',
            'divisi': 'Web Developer',
            'universitas_selected': None,
            'universitas_manual': ''
        }
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # Navigasi Tab
    tab_list, tab_import, tab_manual = st.tabs([
        "📁 Database Terpusat", 
        "📤 Registrasi Kolektif", 
        "➕ Entri Mandiri"
    ])

    # --- TAB 1: DATABASE ---
    with tab_list:
        st.subheader("Daftar Entitas Terdaftar")
        cur.execute("""
            SELECT s.id, u.username, s.name, s.division, s.university 
            FROM students s 
            JOIN users u ON s.id = u.student_id 
            WHERE u.role = 'mahasiswa' 
            ORDER BY s.id DESC
        """)
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["ID", "Username", "Nama Mahasiswa", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Tidak ada data mahasiswa yang ditemukan dalam database.")

    # --- TAB 2: IMPORT KOLEKTIF ---
    with tab_import:
        st.subheader("Unggah Data Massal")
        uploaded_file = st.file_uploader("Pilih file CSV atau Excel", type=["csv", "xlsx"], 
                                         help="Header wajib: id, name, division, university")
        
        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file, sep=None, engine='python') if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                df_up.columns = [c.strip().lower() for c in df_up.columns]
                
                st.write("**Pratinjau Berkas:**")
                st.dataframe(df_up.head(3), use_container_width=True)

                if st.button("Lakukan Integrasi Data", key="btn_bulk"):
                    for _, row in df_up.iterrows():
                        sid, sname = int(row['id']), str(row['name'])
                        sdiv, suniv = str(row['division']), str(row['university'])
                        uname, upass = generate_credentials(sname, sid)

                        cur.execute("INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (sid, sname, sdiv, suniv))
                        cur.execute("INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=VALUES(username)", (uname, upass, "mahasiswa", sid))
                    
                    conn.commit()
                    st.success("Sinkronisasi database berhasil.")
                    st.rerun()
            except Exception as e:
                st.error(f"Kesalahan sistem: {e}")

    # --- TAB 3: ENTRI MANDIRI ---
    with tab_manual:
        st.subheader("Registrasi Mahasiswa Baru")
        
        # Container utama untuk form
        with st.container():
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            
            # Grid Layout dalam 2 kolom
            c1, c2 = st.columns(2)
            
            with c1:
                # NAMA LENGKAP
                st.markdown('<span class="custom-label required">Nama Lengkap</span>', unsafe_allow_html=True)
                nama_input = st.text_input(
                    "", 
                    placeholder="Contoh: Budi Santoso", 
                    key="m_nama",
                    label_visibility="collapsed",
                    value=st.session_state.form_data['nama']
                )
                if nama_input != st.session_state.form_data['nama']:
                    st.session_state.form_data['nama'] = nama_input
                
                # DIVISI
                st.markdown('<span class="custom-label required">Divisi</span>', unsafe_allow_html=True)
                div_input = st.selectbox(
                    "", 
                    ["Web Developer", "Data Science", "AI Engineer"], 
                    index=["Web Developer", "Data Science", "AI Engineer"].index(
                        st.session_state.form_data['divisi']
                    ) if st.session_state.form_data['divisi'] in ["Web Developer", "Data Science", "AI Engineer"] else 0,
                    key="m_div",
                    label_visibility="collapsed"
                )
                if div_input != st.session_state.form_data['divisi']:
                    st.session_state.form_data['divisi'] = div_input
            
            with c2:
                # UNIVERSITAS - menggunakan key yang unik
                st.markdown('<span class="custom-label required">Universitas</span>', unsafe_allow_html=True)
                univ_list = get_list_universitas()
                
                # Temukan index yang sesuai dengan session state
                default_index = 0
                if st.session_state.form_data['universitas_selected']:
                    try:
                        default_index = univ_list.index(st.session_state.form_data['universitas_selected'])
                    except:
                        default_index = 0
                
                univ_selected = st.selectbox(
                    "", 
                    options=univ_list, 
                    index=default_index if default_index < len(univ_list) else 0,
                    placeholder="Pilih dari daftar...", 
                    key="m_univ_select",  # Key yang unik
                    label_visibility="collapsed"
                )
                
                # Simpan ke session state
                if univ_selected != st.session_state.form_data['universitas_selected']:
                    st.session_state.form_data['universitas_selected'] = univ_selected
                
                # Input manual jika dipilih
                if univ_selected == "➕ Input Manual":
                    st.markdown('<div class="manual-input-box">', unsafe_allow_html=True)
                    st.markdown('<span class="custom-label">✏️ Input Nama Universitas Manual</span>', unsafe_allow_html=True)
                    univ_manual = st.text_input(
                        "", 
                        placeholder="Ketik nama universitas lengkap...", 
                        key="m_univ_manual",
                        label_visibility="collapsed",
                        value=st.session_state.form_data['universitas_manual']
                    )
                    if univ_manual != st.session_state.form_data['universitas_manual']:
                        st.session_state.form_data['universitas_manual'] = univ_manual
                    
                    st.caption("Pastikan nama universitas ditulis dengan benar dan lengkap")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Set universitas yang akan disimpan
                    universitas_final = st.session_state.form_data['universitas_manual']
                else:
                    universitas_final = univ_selected
                    
                    # Tampilkan preview universitas yang dipilih
                    if universitas_final and universitas_final != "➕ Input Manual":
                        st.markdown(f'''
                        <div class="info-box">
                        ✅ <strong>Universitas terpilih:</strong> {universitas_final}
                        </div>
                        ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Spacer
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Validasi dan tombol simpan
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("💾 Simpan ke Database", key="btn_save_manual", type="primary", use_container_width=True):
                    # Validasi input
                    if not st.session_state.form_data['nama']:
                        st.error("Nama lengkap wajib diisi")
                    elif not universitas_final or universitas_final == "➕ Input Manual":
                        st.error("Universitas wajib diisi atau pilih dari daftar")
                    else:
                        # Simpan ke database
                        try:
                            cur.execute(
                                "INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", 
                                (st.session_state.form_data['nama'], st.session_state.form_data['divisi'], universitas_final)
                            )
                            conn.commit()
                            new_id = cur.lastrowid
                            u, p = generate_credentials(st.session_state.form_data['nama'], new_id)
                            cur.execute(
                                "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", 
                                (u, p, "mahasiswa", new_id)
                            )
                            conn.commit()
                            
                            # Tampilkan hasil sukses
                            st.success("✅ Data berhasil disimpan!")
                            st.session_state.submitted = True
                            
                            # Tampilkan detail dalam expander
                            with st.expander("📋 Detail Pendaftaran", expanded=True):
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("ID Mahasiswa", new_id)
                                with col_b:
                                    st.metric("Username", u)
                                with col_c:
                                    st.metric("Password", p)
                                
                                st.markdown(f"""
                                **Data Mahasiswa:**
                                - **Nama:** {st.session_state.form_data['nama']}
                                - **Divisi:** {st.session_state.form_data['divisi']}
                                - **Universitas:** {universitas_final}
                                """)
                            
                            # Reset form setelah submit berhasil
                            st.session_state.form_data = {
                                'nama': '',
                                'divisi': 'Web Developer',
                                'universitas_selected': None,
                                'universitas_manual': ''
                            }
                            
                        except Exception as e:
                            st.error(f"Error saat menyimpan data: {str(e)}")
                
                # Tombol reset form
                if st.button("🔄 Reset Form", key="btn_reset", type="secondary", use_container_width=True):
                    st.session_state.form_data = {
                        'nama': '',
                        'divisi': 'Web Developer',
                        'universitas_selected': None,
                        'universitas_manual': ''
                    }
                    st.rerun()

    conn.close()

# Jalankan aplikasi
if __name__ == "__main__":
    mahasiswa_page()

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
        padding: 10px 14px !important;
    }
    
    /* Focus state untuk input */
    .stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus {
        border-color: #0045AD !important;
        box-shadow: 0 0 0 2px rgba(0, 69, 173, 0.1) !important;
    }

    /* Tombol Utama */
    .primary-button {
        background-color: #0045AD !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 1rem;
    }
    .primary-button:hover {
        background-color: #003385 !important;
        box-shadow: 0 4px 12px rgba(0,69,173,0.2);
    }
    
    /* Tombol Secondary */
    .secondary-button {
        background-color: #F8F9FA !important;
        color: #0045AD !important;
        border-radius: 8px !important;
        border: 1px solid #0045AD !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease;
        width: 100%;
    }
    .secondary-button:hover {
        background-color: #E8F4FC !important;
    }

    /* Label styling */
    .form-label {
        font-weight: 600 !important;
        color: #2C3E50 !important;
        margin-bottom: 8px !important;
        display: block !important;
        font-size: 14px !important;
    }
    
    /* Required field indicator */
    .required-field::before {
        content: "* ";
        color: #E74C3C;
    }
    
    /* Manual input container */
    .manual-input-container {
        padding: 1.2rem;
        background-color: #F8FAFC;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Info box */
    .info-box {
        background-color: #E8F4FC;
        padding: 10px 14px;
        border-radius: 6px;
        border-left: 4px solid #3498DB;
        margin-top: 0.5rem;
        font-size: 13px;
    }
    
    /* Help text */
    .help-text {
        color: #6C757D;
        font-size: 12px;
        font-style: italic;
        margin-top: 4px;
    }
    
    /* Form container */
    .form-container {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #E9ECEF;
        margin-bottom: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def get_list_universitas():
    try:
        df = pd.read_csv("universitas_indonesia.csv")
        list_univ = sorted(df['nama_universitas'].dropna().unique().tolist())
        return list_univ
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return []

def generate_credentials(nama, s_id):
    u_name = f"vinix_{nama.lower().split()[0]}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

# ==========================================
# 2. MAIN INTERFACE
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Manajemen Mahasiswa")
    st.markdown("<p style='color: #6C757D; font-size: 1.1em;'>Sistem administrasi pusat untuk pengelolaan data mahasiswa dan kredensial akses.</p>", unsafe_allow_html=True)
    st.divider()

    conn = get_db()
    cur = conn.cursor()

    # Inisialisasi session state
    if 'form_nama' not in st.session_state:
        st.session_state.form_nama = ''
    if 'form_divisi' not in st.session_state:
        st.session_state.form_divisi = 'Web Developer'
    if 'form_univ_mode' not in st.session_state:
        st.session_state.form_univ_mode = 'select'  # 'select' atau 'manual'
    if 'form_univ_selected' not in st.session_state:
        st.session_state.form_univ_selected = None
    if 'form_univ_manual' not in st.session_state:
        st.session_state.form_univ_manual = ''

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
        
        # Container untuk form
        with st.container():
            # Grid Layout
            col1, col2 = st.columns(2)
            
            with col1:
                # NAMA LENGKAP
                st.markdown('<div class="form-label required-field">Nama Lengkap</div>', unsafe_allow_html=True)
                nama_input = st.text_input(
                    "Nama Lengkap",
                    value=st.session_state.form_nama,
                    placeholder="Contoh: Siti Nurjanah",
                    label_visibility="collapsed",
                    key="input_nama"
                )
                st.session_state.form_nama = nama_input
                
                # DIVISI
                st.markdown('<div class="form-label required-field">Divisi</div>', unsafe_allow_html=True)
                divisi_options = ["Web Developer", "Data Science", "AI Engineer"]
                divisi_index = divisi_options.index(st.session_state.form_divisi) if st.session_state.form_divisi in divisi_options else 0
                
                divisi_input = st.selectbox(
                    "Divisi",
                    options=divisi_options,
                    index=divisi_index,
                    label_visibility="collapsed",
                    key="select_divisi"
                )
                st.session_state.form_divisi = divisi_input
            
            with col2:
                # PILIHAN UNIVERSITAS
                st.markdown('<div class="form-label required-field">Pilih Universitas</div>', unsafe_allow_html=True)
                
                # Radio button untuk pilihan mode
                univ_mode = st.radio(
                    "",
                    options=["Pilih dari daftar", "Input manual"],
                    index=0 if st.session_state.form_univ_mode == 'select' else 1,
                    horizontal=True,
                    label_visibility="collapsed",
                    key="radio_univ_mode"
                )
                
                if univ_mode == "Pilih dari daftar":
                    st.session_state.form_univ_mode = 'select'
                    
                    # Dropdown untuk memilih dari daftar
                    univ_list = get_list_universitas()
                    
                    # Temukan index yang sesuai
                    default_index = 0
                    if st.session_state.form_univ_selected and st.session_state.form_univ_selected in univ_list:
                        default_index = univ_list.index(st.session_state.form_univ_selected)
                    
                    selected_univ = st.selectbox(
                        "Pilih Universitas",
                        options=univ_list,
                        index=default_index,
                        placeholder="🔍 Cari atau pilih universitas...",
                        label_visibility="collapsed",
                        key="select_universitas"
                    )
                    st.session_state.form_univ_selected = selected_univ
                    
                    if selected_univ:
                        st.markdown(f'''
                        <div class="info-box">
                        ✅ <strong>Universitas terpilih:</strong> {selected_univ}
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        universitas_final = selected_univ
                    else:
                        universitas_final = None
                        
                else:  # Input manual
                    st.session_state.form_univ_mode = 'manual'
                    
                    # Container untuk input manual
                    st.markdown('<div class="manual-input-container">', unsafe_allow_html=True)
                    st.markdown('<div class="form-label">Nama Universitas</div>', unsafe_allow_html=True)
                    
                    manual_input = st.text_input(
                        "Nama Universitas Manual",
                        value=st.session_state.form_univ_manual,
                        placeholder="Ketik nama universitas lengkap di sini...",
                        label_visibility="collapsed",
                        key="input_univ_manual"
                    )
                    st.session_state.form_univ_manual = manual_input
                    
                    st.markdown('<div class="help-text">Pastikan nama universitas ditulis dengan benar dan lengkap</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if manual_input:
                        universitas_final = manual_input
                    else:
                        universitas_final = None
            
            # Spacer
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Tombol Aksi
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            
            with col_btn2:
                # Tombol Simpan
                if st.button("💾 **Simpan ke Database**", 
                           key="btn_save",
                           use_container_width=True):
                    
                    # Validasi input
                    errors = []
                    
                    if not st.session_state.form_nama or st.session_state.form_nama.strip() == "":
                        errors.append("Nama lengkap wajib diisi")
                    
                    if st.session_state.form_univ_mode == 'select':
                        if not st.session_state.form_univ_selected:
                            errors.append("Pilih universitas dari daftar")
                        else:
                            universitas_final = st.session_state.form_univ_selected
                    else:  # manual mode
                        if not st.session_state.form_univ_manual or st.session_state.form_univ_manual.strip() == "":
                            errors.append("Nama universitas wajib diisi untuk input manual")
                        else:
                            universitas_final = st.session_state.form_univ_manual
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        try:
                            # Simpan ke database
                            cur.execute(
                                "INSERT INTO students (name, division, university) VALUES (%s, %s, %s)", 
                                (st.session_state.form_nama.strip(), 
                                 st.session_state.form_divisi, 
                                 universitas_final.strip())
                            )
                            conn.commit()
                            new_id = cur.lastrowid
                            u, p = generate_credentials(st.session_state.form_nama.strip(), new_id)
                            
                            cur.execute(
                                "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", 
                                (u, p, "mahasiswa", new_id)
                            )
                            conn.commit()
                            
                            # Tampilkan sukses
                            st.success("✅ **Data berhasil disimpan!**")
                            
                            # Tampilkan detail
                            with st.expander("📋 **Detail Pendaftaran**", expanded=True):
                                st.markdown(f"""
                                **Data Mahasiswa:**
                                - **ID Mahasiswa:** {new_id}
                                - **Nama Lengkap:** {st.session_state.form_nama.strip()}
                                - **Divisi:** {st.session_state.form_divisi}
                                - **Universitas:** {universitas_final.strip()}
                                - **Username:** `{u}`
                                - **Password:** `{p}`
                                """)
                            
                            # Reset form
                            st.session_state.form_nama = ''
                            st.session_state.form_univ_selected = None
                            st.session_state.form_univ_manual = ''
                            st.session_state.form_univ_mode = 'select'
                            
                        except Exception as e:
                            st.error(f"❌ **Gagal menyimpan data:** {str(e)}")
                
                # Tombol Reset
                if st.button("🔄 **Reset Form**", 
                           key="btn_reset",
                           type="secondary",
                           use_container_width=True):
                    # Reset semua session state
                    st.session_state.form_nama = ''
                    st.session_state.form_divisi = 'Web Developer'
                    st.session_state.form_univ_selected = None
                    st.session_state.form_univ_manual = ''
                    st.session_state.form_univ_mode = 'select'
                    st.rerun()

    conn.close()

# Jalankan aplikasi
if __name__ == "__main__":
    mahasiswa_page()

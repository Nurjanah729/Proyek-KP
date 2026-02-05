import streamlit as st
import pandas as pd
from db import get_db
import io
import time

# ==========================================
# 1. LOAD DATA UNIVERSITAS DARI CSV
# ==========================================
def load_universitas_data():
    """Load universitas data from CSV file"""
    try:
        # Baca dari file CSV
        df = pd.read_csv("universitas_indonesia.csv")
        
        # Pastikan kolom yang diperlukan ada
        if 'nama_universitas' in df.columns:
            universities = df['nama_universitas'].tolist()
            return sorted(universities)  # Urutkan alfabet
        else:
            st.error("Format CSV tidak valid. Kolom 'nama_universitas' tidak ditemukan.")
            return []
    except FileNotFoundError:
        st.error("File universitas_indonesia.csv tidak ditemukan.")
        return []
    except Exception as e:
        st.error(f"Error membaca file CSV: {str(e)}")
        return []

# ==========================================
# 2. FIX INTERFACE: TEKS PUTIH & TOMBOL KUNING
# ==========================================
st.markdown("""
    <style>
    /* 1. Paksa teks label dan tulisan umum menjadi HITAM/GELAP agar kontras */
    [data-testid="stWidgetLabel"] p, label, .stMarkdown p, h3, h2, h1, span {
        color: #1F2937 !important; 
        font-weight: 600 !important;
    }
    
    /* 2. Tombol Kuning tetap, tapi teks di dalamnya dibuat gelap */
    div.stButton > button {
        background-color: #FFCC00 !important;
        color: #1F2937 !important;
        font-weight: bold !important;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #FFD633 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* 3. Perbaiki warna teks di Sidebar agar tidak putih di background terang */
    [data-testid="stSidebar"] .stMarkdown p {
        color: #1F2937 !important;
    }
    
    /* 4. Styling untuk radio button horizontal */
    .stRadio > div {
        display: flex;
        gap: 1rem;
        padding: 1rem 0;
    }
    
    /* 5. Styling untuk form */
    .stForm {
        background-color: #F8FAFC;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* 6. Styling untuk table */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* 7. Styling untuk selectbox */
    .stSelectbox {
        margin-bottom: 1rem;
    }
    
    /* 8. Styling untuk success/error messages */
    .stAlert {
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* 9. Custom styling untuk expander */
    .streamlit-expanderHeader {
        background-color: #F1F5F9 !important;
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_credentials(nama, s_id):
    """Generate username and password for new student"""
    nama_clean = str(nama).lower().split()[0].replace(" ", "_")
    u_name = f"vinix_{nama_clean}_{s_id}"
    u_pass = f"VNX-{s_id}X"
    return u_name, u_pass

def validate_student_data(m_id, m_nama, m_div, m_univ):
    """Validate student input data"""
    errors = []
    
    if not m_id:
        errors.append("❌ ID Mahasiswa (NIM) wajib diisi")
    elif len(m_id) < 5:
        errors.append("❌ ID Mahasiswa minimal 5 karakter")
    
    if not m_nama:
        errors.append("❌ Nama Lengkap wajib diisi")
    elif len(m_nama) < 2:
        errors.append("❌ Nama Lengkap terlalu pendek")
    
    if not m_div:
        errors.append("❌ Divisi wajib dipilih")
    
    if not m_univ:
        errors.append("❌ Asal Universitas wajib diisi")
    elif m_univ == "Other" and 'universitas_custom' not in st.session_state:
        errors.append("❌ Silakan isi nama universitas di bagian 'Nama Universitas Lainnya'")
    
    return errors

# ==========================================
# 3. FUNGSI UTAMA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa")
    st.divider()

    # Load data universitas sekali di awal
    if 'universitas_list' not in st.session_state:
        st.session_state.universitas_list = load_universitas_data()
    
    # Inisialisasi session state untuk custom university
    if 'universitas_custom' not in st.session_state:
        st.session_state.universitas_custom = ""
    if 'show_custom_univ' not in st.session_state:
        st.session_state.show_custom_univ = False

    # Navigasi tetap di tempat
    menu = st.radio(
        "Pilih Menu:", 
        ["📊 Mahasiswa Terdaftar", "📝 Input Mahasiswa", "📤 Unggah Data Mahasiswa"], 
        horizontal=True, 
        key="nav_final_stable"
    )
    
    conn = get_db()
    cur = conn.cursor()

    if menu == "📝 Input Mahasiswa":
        st.subheader("Registrasi Mahasiswa Baru")
        
        with st.form("form_input_mahasiswa", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                m_id = st.text_input("ID Mahasiswa (NIM)*", 
                                   placeholder="Contoh: 12345678",
                                   help="Masukkan NIM mahasiswa")
                m_nama = st.text_input("Nama Lengkap*", 
                                     placeholder="Contoh: Ahmad Budi",
                                     help="Masukkan nama lengkap mahasiswa")
            
            with col2:
                m_div = st.selectbox("Divisi*", 
                                   ["", "AI Engineering", "Web Development", "Data Science", "Mobile Development", "UI/UX Design"],
                                   help="Pilih divisi untuk mahasiswa")
                
                # Dropdown Universitas dari CSV + opsi Other
                univ_options = ["Pilih Universitas..."] + st.session_state.universitas_list + ["Other (Lainnya)"]
                
                selected_univ = st.selectbox(
                    "Asal Universitas*",
                    options=univ_options,
                    index=0,
                    help="Pilih universitas dari daftar atau pilih 'Other' untuk universitas lain"
                )
                
                # Jika memilih "Other", tampilkan input text
                if selected_univ == "Other (Lainnya)":
                    st.session_state.show_custom_univ = True
                    custom_univ = st.text_input(
                        "Nama Universitas Lainnya*",
                        placeholder="Masukkan nama universitas",
                        help="Masukkan nama universitas yang tidak ada dalam daftar",
                        key="custom_univ_input"
                    )
                    if custom_univ:
                        st.session_state.universitas_custom = custom_univ
                        final_univ = custom_univ
                    else:
                        final_univ = None
                elif selected_univ == "Pilih Universitas...":
                    final_univ = ""
                    st.session_state.show_custom_univ = False
                else:
                    final_univ = selected_univ
                    st.session_state.show_custom_univ = False
            
            # Info jumlah universitas yang tersedia
            with st.expander("ℹ️ Info Daftar Universitas", expanded=False):
                st.write(f"**Total Universitas dalam Database:** {len(st.session_state.universitas_list)}")
                st.write("Universitas terdaftar (A-Z):")
                
                # Tampilkan dalam beberapa kolom untuk readability
                col_univ1, col_univ2 = st.columns(2)
                middle_index = len(st.session_state.universitas_list) // 2
                
                with col_univ1:
                    for univ in st.session_state.universitas_list[:middle_index]:
                        st.write(f"• {univ}")
                
                with col_univ2:
                    for univ in st.session_state.universitas_list[middle_index:]:
                        st.write(f"• {univ}")
            
            st.caption("*Wajib diisi")
            
            submitted = st.form_submit_button("💾 Simpan Mahasiswa", type="primary")
            
            if submitted:
                # Gunakan final_univ untuk validasi
                validation_errors = validate_student_data(m_id, m_nama, m_div, final_univ)
                
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    # Cek apakah ID sudah ada
                    cur.execute("SELECT id FROM students WHERE id = %s", (m_id,))
                    existing_student = cur.fetchone()
                    
                    if existing_student:
                        st.error(f"❌ ID Mahasiswa {m_id} sudah terdaftar!")
                    else:
                        try:
                            uname, upass = generate_credentials(m_nama, m_id)
                            
                            # Simpan ke database
                            cur.execute(
                                "INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s)", 
                                (m_id, m_nama, m_div, final_univ)
                            )
                            cur.execute(
                                "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", 
                                (uname, upass, "mahasiswa", m_id)
                            )
                            conn.commit()
                            
                            # Tampilkan success message dengan detail
                            st.success("✅ Data mahasiswa berhasil disimpan!")
                            
                            # Tampilkan detail credentials
                            with st.expander("📋 Detail Akun Mahasiswa", expanded=True):
                                st.write(f"**ID Mahasiswa:** {m_id}")
                                st.write(f"**Nama:** {m_nama}")
                                st.write(f"**Divisi:** {m_div}")
                                st.write(f"**Universitas:** {final_univ}")
                                st.write(f"**Username:** `{uname}`")
                                st.write(f"**Password:** `{upass}`")
                                st.warning("⚠️ Catat username dan password ini! Informasikan ke mahasiswa.")
                            
                            # Reset session state untuk custom university
                            st.session_state.universitas_custom = ""
                            st.session_state.show_custom_univ = False
                            
                            st.balloons()
                            
                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ Gagal menyimpan data: {str(e)}")

    elif menu == "📤 Unggah Data Mahasiswa":
        st.subheader("Registrasi Kolektif via CSV")
        st.info("📥 **Template CSV:** Pastikan file CSV memiliki kolom: `id`, `name`, `division`, `university`")
        
        # Informasi tentang universitas
        with st.expander("📚 Daftar Universitas yang Didukung", expanded=False):
            st.write(f"**Total:** {len(st.session_state.universitas_list)} universitas terdaftar")
            st.write("**Format universitas:** Gunakan nama lengkap universitas sesuai daftar")
            if st.button("📋 Lihat Daftar Lengkap"):
                df_univ = pd.DataFrame(st.session_state.universitas_list, columns=["Nama Universitas"])
                st.dataframe(df_univ, use_container_width=True)
        
        # Template download dengan contoh universitas dari CSV
        example_universities = st.session_state.universitas_list[:5] if st.session_state.universitas_list else ["Universitas Indonesia", "Universitas Gadjah Mada"]
        
        template_data = {
            'id': ['12345678', '87654321', '23456789'],
            'name': ['Ahmad Budi', 'Siti Nurhaliza', 'Budi Santoso'],
            'division': ['AI Engineering', 'Web Development', 'Data Science'],
            'university': example_universities[:3]  # Ambil 3 contoh
        }
        template_df = pd.DataFrame(template_data)
        
        csv_template = template_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Template CSV",
            data=csv_template,
            file_name="template_mahasiswa.csv",
            mime="text/csv",
            help="Download template untuk mengisi data mahasiswa"
        )
        
        uploaded_file = st.file_uploader(
            "Pilih Berkas CSV", 
            type=["csv"], 
            key="uploader_csv_v3",
            help="Unggah file CSV sesuai template"
        )

        if uploaded_file is not None:
            try:
                # Membaca file CSV
                content = uploaded_file.getvalue().decode('utf-8')
                
                # Coba berbagai separator
                separators = [',', ';', '\t']
                df = None
                
                for sep in separators:
                    try:
                        df = pd.read_csv(io.StringIO(content), sep=sep)
                        if len(df.columns) >= 4:  # Minimal 4 kolom
                            break
                    except:
                        continue
                
                if df is None:
                    # Fallback ke deteksi otomatis
                    df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
                
                # Membersihkan nama kolom
                df.columns = df.columns.str.strip().str.lower()
                
                # Membersihkan data string
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.strip()
                
                st.write("### Pratinjau Data")
                st.dataframe(df.head(), use_container_width=True)
                
                # Validasi kolom yang diperlukan
                required = ['id', 'name', 'division', 'university']
                missing_cols = [col for col in required if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Kolom berikut tidak ditemukan: {', '.join(missing_cols)}")
                    st.write("Kolom yang terbaca:", list(df.columns))
                else:
                    st.success(f"✅ Format CSV valid. {len(df)} data ditemukan.")
                    
                    # Validasi data universitas
                    invalid_univ = []
                    valid_univ_set = set(st.session_state.universitas_list)
                    
                    for idx, univ in enumerate(df['university']):
                        if univ and univ not in valid_univ_set:
                            invalid_univ.append((idx + 2, univ))  # +2 karena header + index 0-based
                    
                    if invalid_univ:
                        st.warning(f"⚠️ {len(invalid_univ)} universitas tidak terdaftar dalam database utama.")
                        with st.expander("Lihat universitas tidak terdaftar"):
                            for row, univ_name in invalid_univ[:20]:  # Tampilkan maksimal 20
                                st.write(f"Baris {row}: {univ_name}")
                            if len(invalid_univ) > 20:
                                st.write(f"... dan {len(invalid_univ) - 20} lainnya")
                    
                    if st.button("🚀 Konfirmasi & Impor ke Database", type="primary"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        success_count = 0
                        error_count = 0
                        error_details = []
                        
                        total_rows = len(df)
                        
                        for idx, row in df.iterrows():
                            try:
                                sid = str(row['id']).strip()
                                sname = str(row['name']).strip()
                                sdiv = str(row['division']).strip()
                                suniv = str(row['university']).strip()
                                
                                # Validasi baris
                                if not sid:
                                    error_details.append(f"Baris {idx+2}: ID tidak boleh kosong")
                                    error_count += 1
                                    continue
                                
                                if not sname:
                                    error_details.append(f"Baris {idx+2}: Nama tidak boleh kosong")
                                    error_count += 1
                                    continue
                                
                                if not sdiv:
                                    error_details.append(f"Baris {idx+2}: Divisi tidak boleh kosong")
                                    error_count += 1
                                    continue
                                
                                if not suniv:
                                    error_details.append(f"Baris {idx+2}: Universitas tidak boleh kosong")
                                    error_count += 1
                                    continue
                                
                                # Cek duplikasi
                                cur.execute("SELECT id FROM students WHERE id = %s", (sid,))
                                if cur.fetchone():
                                    error_details.append(f"Baris {idx+2}: ID {sid} sudah terdaftar")
                                    error_count += 1
                                    continue
                                
                                uname, upass = generate_credentials(sname, sid)
                                
                                # Simpan ke database
                                cur.execute(
                                    "INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s)", 
                                    (sid, sname, sdiv, suniv)
                                )
                                cur.execute(
                                    "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", 
                                    (uname, upass, "mahasiswa", sid)
                                )
                                
                                success_count += 1
                                
                            except Exception as e:
                                error_details.append(f"Baris {idx+2}: {str(e)}")
                                error_count += 1
                            
                            # Update progress
                            progress_bar.progress((idx + 1) / total_rows)
                            status_text.text(f"Memproses {idx + 1}/{total_rows} data...")
                        
                        conn.commit()
                        
                        # Tampilkan hasil
                        st.success(f"✅ Import selesai!")
                        
                        col_success, col_error = st.columns(2)
                        with col_success:
                            st.metric("Berhasil Disimpan", f"{success_count} data")
                        with col_error:
                            st.metric("Gagal", f"{error_count} data")
                        
                        if error_details:
                            with st.expander("📝 Detail Error", expanded=False):
                                for error in error_details[:50]:  # Tampilkan maksimal 50 error
                                    st.error(error)
                                if len(error_details) > 50:
                                    st.write(f"... dan {len(error_details) - 50} error lainnya")
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        if success_count > 0:
                            st.balloons()
            
            except Exception as e:
                st.error(f"❌ Gagal membaca file CSV: {str(e)}")
                st.info("Pastikan format file CSV benar dan coba download template di atas.")

    else:  # Menu: 📊 Mahasiswa Terdaftar
        st.subheader("Daftar Mahasiswa Terdaftar")
        
        # Filter options
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            search_term = st.text_input("🔍 Cari (ID/Nama)", placeholder="Cari mahasiswa...")
        
        with col_filter2:
            division_filter = st.selectbox(
                "Filter Divisi", 
                ["Semua Divisi"] + ["AI Engineering", "Web Development", "Data Science", "Mobile Development", "UI/UX Design"]
            )
        
        with col_filter3:
            university_filter = st.selectbox(
                "Filter Universitas",
                ["Semua Universitas"] + sorted(st.session_state.universitas_list)
            )
        
        # Query dengan filter
        query = "SELECT id, name, division, university FROM students WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (id LIKE %s OR name LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if division_filter != "Semua Divisi":
            query += " AND division = %s"
            params.append(division_filter)
        
        if university_filter != "Semua Universitas":
            query += " AND university = %s"
            params.append(university_filter)
        
        query += " ORDER BY id ASC"
        
        cur.execute(query, tuple(params))
        res = cur.fetchall()
        
        if res:
            df = pd.DataFrame(res, columns=["ID", "Nama", "Divisi", "Universitas"])
            
            # Tampilkan statistik
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Mahasiswa", len(df))
            with col2:
                st.metric("Jumlah Divisi", df['Divisi'].nunique())
            with col3:
                st.metric("Jumlah Universitas", df['Universitas'].nunique())
            with col4:
                # Hitung universitas yang tidak ada di daftar utama
                univ_in_list = [univ for univ in df['Universitas'].unique() if univ in st.session_state.universitas_list]
                st.metric("Univ Terdaftar", f"{len(univ_in_list)}/{df['Universitas'].nunique()}")
            
            # Tampilkan tabel
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.TextColumn(width="medium"),
                    "Nama": st.column_config.TextColumn(width="large"),
                    "Divisi": st.column_config.TextColumn(width="medium"),
                    "Universitas": st.column_config.TextColumn(width="large")
                }
            )
            
            # Download button
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data sebagai CSV",
                data=csv_data,
                file_name="data_mahasiswa.csv",
                mime="text/csv"
            )
            
            # Tampilkan distribusi universitas
            with st.expander("📊 Distribusi Universitas", expanded=False):
                univ_counts = df['Universitas'].value_counts().head(20)
                if not univ_counts.empty:
                    st.bar_chart(univ_counts)
                else:
                    st.info("Tidak ada data untuk ditampilkan")
        else:
            st.info("📭 Tidak ada data mahasiswa yang ditemukan.")
    
    conn.close()

if __name__ == "__main__":
    mahasiswa_page()

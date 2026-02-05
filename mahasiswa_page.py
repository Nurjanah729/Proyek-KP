import streamlit as st
import pandas as pd
from db import get_db
import io

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
            return []
    except FileNotFoundError:
        return []
    except Exception as e:
        return []

# ==========================================
# 2. FUNGSI UTAMA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa")
    
    # Load data universitas sekali di awal
    if 'universitas_list' not in st.session_state:
        st.session_state.universitas_list = load_universitas_data()

    # Navigasi - 3 MENU
    menu = st.radio(
        "Pilih Menu:", 
        ["📊 Mahasiswa Terdaftar", "📝 Input Mahasiswa", "📤 Unggah Data Mahasiswa"], 
        horizontal=True, 
        key="nav_mahasiswa"
    )
    
    conn = get_db()
    cur = conn.cursor()

    if menu == "📝 Input Mahasiswa":
        st.header("📝 Input Mahasiswa Baru")
        st.write("Silakan isi form di bawah untuk mendaftarkan mahasiswa baru.")
        
        # Buat form
        with st.form("form_input_mahasiswa", clear_on_submit=True):
            st.subheader("Data Mahasiswa")
            
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
                                   ["Pilih Divisi...", "AI Engineering", "Web Development", "Data Science", "Mobile Development", "UI/UX Design"],
                                   help="Pilih divisi untuk mahasiswa")
                
                # Dropdown Universitas dari CSV + opsi Other
                univ_options = ["Pilih Universitas..."] + st.session_state.universitas_list + ["Other (Lainnya)"]
                
                selected_univ = st.selectbox(
                    "Asal Universitas*",
                    options=univ_options,
                    index=0,
                    help="Pilih universitas dari daftar atau 'Other' untuk universitas lain"
                )
                
                # Jika memilih "Other", tampilkan input text
                if selected_univ == "Other (Lainnya)":
                    custom_univ = st.text_input(
                        "Nama Universitas Lainnya*",
                        placeholder="Masukkan nama universitas yang tidak ada di daftar",
                        help="Ketik nama universitas lengkap",
                        value=""
                    )
                    final_univ = custom_univ
                elif selected_univ == "Pilih Universitas...":
                    final_univ = ""
                else:
                    final_univ = selected_univ
            
            st.markdown("---")
            st.caption("*) Wajib diisi")
            
            submitted = st.form_submit_button("💾 Simpan Data Mahasiswa", type="primary")
            
            if submitted:
                # Validasi input
                errors = []
                if not m_id or m_id.strip() == "":
                    errors.append("❌ ID Mahasiswa wajib diisi")
                if not m_nama or m_nama.strip() == "":
                    errors.append("❌ Nama Lengkap wajib diisi")
                if m_div == "Pilih Divisi...":
                    errors.append("❌ Divisi wajib dipilih")
                if not final_univ or final_univ.strip() == "":
                    errors.append("❌ Asal Universitas wajib diisi")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Cek apakah ID sudah ada
                    cur.execute("SELECT id FROM students WHERE id = %s", (m_id,))
                    existing_student = cur.fetchone()
                    
                    if existing_student:
                        st.error(f"❌ ID Mahasiswa {m_id} sudah terdaftar!")
                    else:
                        try:
                            # Generate username dan password
                            nama_clean = str(m_nama).lower().split()[0].replace(" ", "_")
                            u_name = f"vinix_{nama_clean}_{m_id}"
                            u_pass = f"VNX-{m_id}X"
                            
                            # Simpan ke database
                            cur.execute(
                                "INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s)", 
                                (m_id, m_nama, m_div, final_univ)
                            )
                            cur.execute(
                                "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", 
                                (u_name, u_pass, "mahasiswa", m_id)
                            )
                            conn.commit()
                            
                            st.success("✅ Data mahasiswa berhasil disimpan!")
                            
                            # Tampilkan detail akun
                            with st.expander("📋 Detail Akun Mahasiswa", expanded=True):
                                st.write(f"**ID Mahasiswa:** {m_id}")
                                st.write(f"**Nama:** {m_nama}")
                                st.write(f"**Divisi:** {m_div}")
                                st.write(f"**Universitas:** {final_univ}")
                                st.write(f"**Username:** `{u_name}`")
                                st.write(f"**Password:** `{u_pass}`")
                                st.warning("⚠️ Simpan username dan password ini!")
                            
                            st.balloons()
                            
                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ Gagal menyimpan data: {str(e)}")

    elif menu == "📤 Unggah Data Mahasiswa":
        st.header("📤 Unggah Data Mahasiswa")
        st.write("Unggah file CSV berisi data mahasiswa untuk registrasi kolektif.")
        
        st.info("""
        **Format CSV yang diperlukan:**
        - Kolom 1: `id` (ID Mahasiswa/NIM)
        - Kolom 2: `name` (Nama Lengkap)
        - Kolom 3: `division` (Divisi: AI Engineering, Web Development, Data Science, dll)
        - Kolom 4: `university` (Asal Universitas)
        """)
        
        uploaded_file = st.file_uploader(
            "Pilih File CSV", 
            type=["csv"], 
            help="Unggah file CSV dengan format yang sesuai"
        )

        if uploaded_file is not None:
            try:
                # Membaca file CSV
                content = uploaded_file.getvalue().decode('utf-8')
                df = pd.read_csv(io.StringIO(content))
                
                # Membersihkan nama kolom
                df.columns = df.columns.str.strip().str.lower()
                
                st.subheader("Pratinjau Data")
                st.dataframe(df.head())
                
                # Validasi kolom yang diperlukan
                required = ['id', 'name', 'division', 'university']
                missing_cols = [col for col in required if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Kolom berikut tidak ditemukan: {', '.join(missing_cols)}")
                    st.write(f"Kolom yang terbaca: {list(df.columns)}")
                else:
                    st.success(f"✅ Format CSV valid. Ditemukan {len(df)} data mahasiswa.")
                    
                    if st.button("🚀 Proses dan Simpan Semua Data", type="primary"):
                        success_count = 0
                        error_count = 0
                        error_messages = []
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in df.iterrows():
                            try:
                                sid = str(row['id']).strip()
                                sname = str(row['name']).strip()
                                sdiv = str(row['division']).strip()
                                suniv = str(row['university']).strip()
                                
                                # Validasi data
                                if not sid or not sname or not sdiv or not suniv:
                                    error_count += 1
                                    error_messages.append(f"Baris {idx+2}: Data tidak lengkap")
                                    continue
                                
                                # Cek apakah ID sudah ada
                                cur.execute("SELECT id FROM students WHERE id = %s", (sid,))
                                if cur.fetchone():
                                    error_count += 1
                                    error_messages.append(f"Baris {idx+2}: ID {sid} sudah terdaftar")
                                    continue
                                
                                # Generate username dan password
                                nama_clean = str(sname).lower().split()[0].replace(" ", "_")
                                u_name = f"vinix_{nama_clean}_{sid}"
                                u_pass = f"VNX-{sid}X"
                                
                                # Simpan ke database
                                cur.execute(
                                    "INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s)", 
                                    (sid, sname, sdiv, suniv)
                                )
                                cur.execute(
                                    "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)", 
                                    (u_name, u_pass, "mahasiswa", sid)
                                )
                                
                                success_count += 1
                                
                            except Exception as e:
                                error_count += 1
                                error_messages.append(f"Baris {idx+2}: {str(e)}")
                            
                            # Update progress
                            progress = (idx + 1) / len(df)
                            progress_bar.progress(progress)
                            status_text.text(f"Memproses {idx + 1}/{len(df)} data...")
                        
                        conn.commit()
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        st.success(f"✅ Proses selesai! Berhasil menyimpan {success_count} data mahasiswa.")
                        
                        if error_count > 0:
                            st.warning(f"⚠️ {error_count} data gagal diproses")
                            with st.expander("Lihat detail error"):
                                for error in error_messages[:10]:  # Tampilkan maksimal 10 error
                                    st.error(error)
                                if len(error_messages) > 10:
                                    st.write(f"... dan {len(error_messages) - 10} error lainnya")
                        
                        if success_count > 0:
                            st.balloons()
            
            except Exception as e:
                st.error(f"❌ Gagal membaca file CSV: {str(e)}")

    else:  # Menu: 📊 Mahasiswa Terdaftar
        st.header("📊 Mahasiswa Terdaftar")
        st.write("Berikut adalah daftar mahasiswa yang telah terdaftar.")
        
        # Query semua data mahasiswa
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id ASC")
        res = cur.fetchall()
        
        if res:
            df = pd.DataFrame(res, columns=["ID", "Nama", "Divisi", "Universitas"])
            
            # Tampilkan statistik singkat
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Mahasiswa", len(df))
            with col2:
                st.metric("Jumlah Universitas", df['Universitas'].nunique())
            
            # Tampilkan tabel
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("📭 Belum ada data mahasiswa yang terdaftar.")
    
    conn.close()

if __name__ == "__main__":
    mahasiswa_page()

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
            st.error("Format CSV tidak valid. Kolom 'nama_universitas' tidak ditemukan.")
            return []
    except FileNotFoundError:
        st.error("File universitas_indonesia.csv tidak ditemukan.")
        return []
    except Exception as e:
        st.error(f"Error membaca file CSV: {str(e)}")
        return []

# ==========================================
# 2. FUNGSI UTAMA
# ==========================================
def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa")
    
    # Load data universitas sekali di awal
    if 'universitas_list' not in st.session_state:
        st.session_state.universitas_list = load_universitas_data()
    
    # Inisialisasi session state untuk custom university
    if 'universitas_custom' not in st.session_state:
        st.session_state.universitas_custom = ""

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
        st.subheader("Registrasi Mahasiswa Baru")
        st.write("Masukkan data mahasiswa baru secara manual:")
        
        with st.form("form_input_mahasiswa", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                m_id = st.text_input("ID Mahasiswa (NIM)*", 
                                   placeholder="Contoh: 12345678")
                m_nama = st.text_input("Nama Lengkap*", 
                                     placeholder="Contoh: Ahmad Budi")
            
            with col2:
                m_div = st.selectbox("Divisi*", 
                                   ["", "AI Engineering", "Web Development", "Data Science", "Mobile Development", "UI/UX Design"])
                
                # Dropdown Universitas dari CSV + opsi Other
                univ_options = ["Pilih Universitas..."] + st.session_state.universitas_list + ["Other (Lainnya)"]
                
                selected_univ = st.selectbox(
                    "Asal Universitas*",
                    options=univ_options,
                    index=0
                )
                
                # Jika memilih "Other", tampilkan input text
                if selected_univ == "Other (Lainnya)":
                    custom_univ = st.text_input(
                        "Nama Universitas Lainnya*",
                        placeholder="Masukkan nama universitas",
                        key="custom_univ_input"
                    )
                    if custom_univ:
                        final_univ = custom_univ
                    else:
                        final_univ = None
                elif selected_univ == "Pilih Universitas...":
                    final_univ = ""
                else:
                    final_univ = selected_univ
            
            st.caption("*Wajib diisi")
            
            submitted = st.form_submit_button("💾 Simpan Mahasiswa", type="primary")
            
            if submitted:
                # Validasi input
                errors = []
                if not m_id:
                    errors.append("❌ ID Mahasiswa wajib diisi")
                if not m_nama:
                    errors.append("❌ Nama Lengkap wajib diisi")
                if not m_div:
                    errors.append("❌ Divisi wajib dipilih")
                if not final_univ or final_univ == "":
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
                            st.info(f"**Username:** {u_name} | **Password:** {u_pass}")
                            st.balloons()
                            
                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ Gagal menyimpan data: {str(e)}")

    elif menu == "📤 Unggah Data Mahasiswa":
        st.subheader("Registrasi Kolektif via CSV")
        st.write("Unggah file CSV berisi data mahasiswa:")
        
        uploaded_file = st.file_uploader(
            "Pilih Berkas CSV", 
            type=["csv"], 
            help="Format CSV harus memiliki kolom: id, name, division, university"
        )

        if uploaded_file is not None:
            try:
                # Membaca file CSV
                content = uploaded_file.getvalue().decode('utf-8')
                df = pd.read_csv(io.StringIO(content))
                
                # Membersihkan nama kolom
                df.columns = df.columns.str.strip().str.lower()
                
                st.write("### Pratinjau Data:")
                st.dataframe(df.head())
                
                # Validasi kolom yang diperlukan
                required = ['id', 'name', 'division', 'university']
                missing_cols = [col for col in required if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Kolom berikut tidak ditemukan: {', '.join(missing_cols)}")
                else:
                    if st.button("💾 Simpan Semua Data", type="primary"):
                        success_count = 0
                        error_count = 0
                        
                        for _, row in df.iterrows():
                            try:
                                sid = str(row['id']).strip()
                                sname = str(row['name']).strip()
                                sdiv = str(row['division']).strip()
                                suniv = str(row['university']).strip()
                                
                                # Cek apakah ID sudah ada
                                cur.execute("SELECT id FROM students WHERE id = %s", (sid,))
                                if cur.fetchone():
                                    error_count += 1
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
                                continue
                        
                        conn.commit()
                        
                        st.success(f"✅ Berhasil menyimpan {success_count} data mahasiswa!")
                        if error_count > 0:
                            st.warning(f"⚠️ {error_count} data gagal disimpan (mungkin ID duplikat)")
                        st.balloons()
            
            except Exception as e:
                st.error(f"❌ Gagal membaca file CSV: {str(e)}")

    else:  # Menu: 📊 Mahasiswa Terdaftar
        st.subheader("Daftar Mahasiswa Terdaftar")
        
        # Query semua data mahasiswa
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id ASC")
        res = cur.fetchall()
        
        if res:
            df = pd.DataFrame(res, columns=["ID", "Nama", "Divisi", "Universitas"])
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📭 Tidak ada data mahasiswa yang ditemukan.")
    
    conn.close()

if __name__ == "__main__":
    mahasiswa_page()

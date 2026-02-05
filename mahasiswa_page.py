import streamlit as st
import pandas as pd
from db import get_db
import io

# Load data universitas
def load_universitas():
    try:
        df = pd.read_csv("universitas_indonesia.csv")
        if 'nama_universitas' in df.columns:
            return sorted(df['nama_universitas'].tolist())
        return []
    except:
        return []

# Main function
def mahasiswa_page():
    st.title("👨‍🎓 Panel Pendaftaran Mahasiswa")
    
    # Load universitas data
    universitas_list = load_universitas()
    
    # Menu
    menu = st.radio("Pilih Menu:", 
                   ["📊 Mahasiswa Terdaftar", "📝 Input Mahasiswa", "📤 Unggah Data CSV"], 
                   horizontal=True)
    
    conn = get_db()
    cur = conn.cursor()
    
    if menu == "📝 Input Mahasiswa":
        st.header("Input Data Mahasiswa")
        
        # Form input
        m_id = st.text_input("ID Mahasiswa (NIM)*", placeholder="Contoh: 12345678")
        m_nama = st.text_input("Nama Lengkap*", placeholder="Contoh: Ahmad Budi")
        m_div = st.selectbox("Divisi*", ["Pilih Divisi", "AI Engineering", "Web Development", "Data Science", "Mobile Development", "UI/UX Design"])
        
        # Universitas - SEDERHANA: Radio button untuk pilihan
        st.write("**Asal Universitas***")
        pilihan_univ = st.radio(
            "Pilih opsi:",
            ["Pilih dari daftar", "Input manual"],
            horizontal=True
        )
        
        final_univ = ""
        
        if pilihan_univ == "Pilih dari daftar":
            if universitas_list:
                selected = st.selectbox("Pilih Universitas:", ["Pilih..."] + universitas_list)
                if selected != "Pilih...":
                    final_univ = selected
            else:
                st.warning("Daftar universitas tidak tersedia")
                final_univ = st.text_input("Masukkan nama universitas:", placeholder="Nama universitas")
        else:
            final_univ = st.text_input("Masukkan nama universitas:", placeholder="Nama universitas")
        
        st.caption("*Wajib diisi")
        
        if st.button("💾 Simpan Data", type="primary"):
            # Validasi
            if not m_id or not m_nama or m_div == "Pilih Divisi" or not final_univ:
                st.error("Harap isi semua field yang wajib!")
            else:
                # Cek duplikasi
                cur.execute("SELECT id FROM students WHERE id = %s", (m_id,))
                if cur.fetchone():
                    st.error(f"ID {m_id} sudah terdaftar!")
                else:
                    # Generate credentials
                    nama_clean = str(m_nama).lower().split()[0].replace(" ", "_")
                    username = f"vinix_{nama_clean}_{m_id}"
                    password = f"VNX-{m_id}X"
                    
                    # Insert ke database
                    cur.execute(
                        "INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s)",
                        (m_id, m_nama, m_div, final_univ)
                    )
                    cur.execute(
                        "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)",
                        (username, password, "mahasiswa", m_id)
                    )
                    conn.commit()
                    
                    st.success("✅ Data berhasil disimpan!")
                    st.info(f"**Username:** {username} | **Password:** {password}")
    
    elif menu == "📤 Unggah Data CSV":
        st.header("Unggah Data CSV")
        
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview data:")
                st.dataframe(df)
                
                if st.button("💾 Simpan Semua Data", type="primary"):
                    success = 0
                    failed = 0
                    
                    for _, row in df.iterrows():
                        try:
                            sid = str(row.get('id', '')).strip()
                            sname = str(row.get('name', '')).strip()
                            sdiv = str(row.get('division', '')).strip()
                            suniv = str(row.get('university', '')).strip()
                            
                            if sid and sname and sdiv and suniv:
                                # Generate credentials
                                nama_clean = str(sname).lower().split()[0].replace(" ", "_")
                                username = f"vinix_{nama_clean}_{sid}"
                                password = f"VNX-{sid}X"
                                
                                # Insert ke database
                                cur.execute(
                                    "INSERT INTO students (id, name, division, university) VALUES (%s, %s, %s, %s)",
                                    (sid, sname, sdiv, suniv)
                                )
                                cur.execute(
                                    "INSERT INTO users (username, password, role, student_id) VALUES (%s, %s, %s, %s)",
                                    (username, password, "mahasiswa", sid)
                                )
                                success += 1
                            else:
                                failed += 1
                        except:
                            failed += 1
                    
                    conn.commit()
                    st.success(f"✅ {success} data berhasil disimpan")
                    if failed > 0:
                        st.warning(f"⚠️ {failed} data gagal")
                    
            except Exception as e:
                st.error(f"Error: {e}")
    
    else:  # Mahasiswa Terdaftar
        st.header("Data Mahasiswa Terdaftar")
        
        cur.execute("SELECT id, name, division, university FROM students ORDER BY id")
        results = cur.fetchall()
        
        if results:
            df = pd.DataFrame(results, columns=["ID", "Nama", "Divisi", "Universitas"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada data mahasiswa")
    
    conn.close()

if __name__ == "__main__":
    mahasiswa_page()

import streamlit as st
import mysql.connector

# Nama fungsi diubah sedikit agar lebih konsisten
def pengaturan_page(student_id, conn):
    """
    Halaman pengaturan akun mahasiswa.
    student_id: ID mahasiswa dari session_state
    conn: koneksi MySQL yang dikirim dari app.py atau dashboard
    """
    if not student_id:
        st.error("ID mahasiswa tidak tersedia")
        return

    st.title("⚙️ Pengaturan Akun")

    try:
        cur = conn.cursor()

        # Ambil data untuk memastikan user ada
        cur.execute("SELECT password FROM students WHERE id = %s", (student_id,))
        result = cur.fetchone()
        
        if not result:
            st.error("Data mahasiswa tidak ditemukan di database.")
            return

        # Form pengaturan menggunakan Card Style agar senada dengan UI kamu
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            with st.form("form_pengaturan"):
                st.subheader("Ganti Password")
                new_pass = st.text_input("Password baru", type="password", placeholder="Masukkan password baru")
                confirm_pass = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password baru")
                
                submit = st.form_submit_button("Simpan Perubahan")

                if submit:
                    if not new_pass:
                        st.warning("Password baru tidak boleh kosong!")
                    elif new_pass != confirm_pass:
                        st.error("Konfirmasi password tidak cocok!")
                    else:
                        cur.execute(
                            "UPDATE students SET password=%s WHERE id=%s",
                            (new_pass, student_id)
                        )
                        conn.commit()
                        st.success("✅ Password berhasil diperbarui!")
            st.markdown('</div>', unsafe_allow_html=True)

    except mysql.connector.Error as e:
        st.error(f"Terjadi kesalahan database: {e}")
    finally:
        if 'cur' in locals():
            cur.close()

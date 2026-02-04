import streamlit as st
import mysql.connector

def pengaturan_page(student_id, conn):
    if not student_id:
        st.error("ID mahasiswa tidak tersedia")
        return

    st.title("⚙️ Pengaturan Akun")

    try:
        cur = conn.cursor()

        # 🔴 PERBAIKAN: Ambil password dari tabel 'users' menggunakan 'student_id'
        cur.execute("SELECT password FROM users WHERE student_id = %s", (student_id,))
        result = cur.fetchone()
        
        if not result:
            st.error("Data akun tidak ditemukan di tabel users.")
            return

        with st.container():
            with st.form("form_pengaturan"):
                st.subheader("Ganti Password")
                new_pass = st.text_input("Password baru", type="password")
                confirm_pass = st.text_input("Konfirmasi Password baru", type="password")
                
                submit = st.form_submit_button("Simpan Perubahan")

                if submit:
                    if not new_pass:
                        st.warning("Password baru tidak boleh kosong!")
                    elif new_pass != confirm_pass:
                        st.error("Konfirmasi password tidak cocok!")
                    else:
                        # 🔴 PERBAIKAN: Update password di tabel 'users'
                        cur.execute(
                            "UPDATE users SET password=%s WHERE student_id=%s",
                            (new_pass, student_id)
                        )
                        conn.commit()
                        st.success("✅ Password berhasil diperbarui!")

    except mysql.connector.Error as e:
        st.error(f"Terjadi kesalahan database: {e}")
    finally:
        if 'cur' in locals():
            cur.close()

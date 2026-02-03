import streamlit as st
import mysql.connector

def pengaturan_page(student_id, conn):
    """
    Halaman pengaturan akun mahasiswa.
    student_id: ID mahasiswa dari session_state
    conn: koneksi MySQL
    """
    if not student_id:
        st.error("ID mahasiswa tidak tersedia")
        return

    st.title("Pengaturan Akun")

    try:
        cur = conn.cursor()

        # Ambil password lama (opsional)
        cur.execute("SELECT password FROM students WHERE id = %s", (student_id,))
        result = cur.fetchone()
        if not result:
            st.error("Mahasiswa tidak ditemukan")
            return
        old_pass = result[0]

        # Form pengaturan
        with st.form("form_pengaturan"):
            new_pass = st.text_input("Password baru", type="password")
            submit = st.form_submit_button("Simpan")

            if submit:
                if not new_pass:
                    st.warning("Password baru tidak boleh kosong")
                else:
                    try:
                        cur.execute(
                            "UPDATE students SET password=%s WHERE id=%s",
                            (new_pass, student_id)
                        )
                        conn.commit()
                        st.success("Password berhasil diperbarui")
                    except mysql.connector.Error as e:
                        st.error(f"Terjadi kesalahan saat menyimpan data: {e}")

    except mysql.connector.Error as e:
        st.error(f"Terjadi kesalahan database: {e}")
    finally:
        try:
            cur.close()
        except:
            pass

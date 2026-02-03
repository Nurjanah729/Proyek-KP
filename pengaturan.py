import streamlit as st
import mysql.connector

def pengaturan_page(student_id, conn):
    """
    Halaman pengaturan akun mahasiswa.
    student_id: ID mahasiswa dari session_state
    conn: koneksi MySQL
    """
    st.title("Pengaturan Akun")

    # Ambil password lama dari database (opsional, bisa ditampilkan jika perlu)
    try:
        cur = conn.cursor()
        cur.execute("SELECT password FROM students WHERE id = %s", (student_id,))
        result = cur.fetchone()
        if result:
            old_pass = result[0]
        else:
            st.error("Mahasiswa tidak ditemukan")
            return
    except mysql.connector.Error as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {e}")
        return

    # Form pengaturan
    with st.form("form_pengaturan"):
        new_pass = st.text_input("Password baru", type="password")
        submit = st.form_submit_button("Simpan")

        if submit:
            # Validasi input
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
    cur.close()

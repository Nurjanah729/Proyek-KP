import streamlit as st
from db import get_db

def pengaturan_page(student_id):

    st.markdown("## ⚙️ Ubah Password")

    with st.form("ubah_password"):
        password_lama = st.text_input("Password Lama", type="password")
        password_baru = st.text_input("Password Baru", type="password")

        submit = st.form_submit_button("Simpan")

        if submit:
            if not password_lama or not password_baru:
                st.error("Semua field wajib diisi")
                return

            conn = get_db()
            cur = conn.cursor()

            cur.execute(
                "SELECT password FROM students WHERE id = %s",
                (student_id,)
            )
            data = cur.fetchone()

            if not data or data[0] != password_lama:
                st.error("Password lama salah")
            else:
                cur.execute(
                    "UPDATE students SET password = %s WHERE id = %s",
                    (password_baru, student_id)
                )
                conn.commit()
                st.success("Password berhasil diubah")

            conn.close()

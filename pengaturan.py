import streamlit as st
from db import get_db
import hashlib


def pengaturan_page():
    st.markdown("## ⚙️ Pengaturan Akun")
    st.markdown("### 🔐 Ubah Password")

    password_baru = st.text_input(
        "Password Baru",
        type="password"
    )

    konfirmasi_password = st.text_input(
        "Konfirmasi Password",
        type="password"
    )

    if st.button("💾 Simpan Password"):
        if not password_baru or not konfirmasi_password:
            st.error("Password tidak boleh kosong")
            return

        if password_baru != konfirmasi_password:
            st.error("Password tidak sama")
            return

        hashed_password = hashlib.sha256(password_baru.encode()).hexdigest()

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE students SET password = %s WHERE id = %s",
            (hashed_password, st.session_state.student_id)
        )
        conn.commit()
        conn.close()

        st.success("✅ Password berhasil diubah")

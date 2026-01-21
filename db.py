import streamlit as st
import mysql.connector

def get_db():
    db = st.secrets["mysql"]

    conn = mysql.connector.connect(
        host=db["host"],
        port=db["port"],
        user=db["user"],
        password=db["password"],
        database=db["database"],
        ssl_disabled=True   # ⬅️ KUNCI UTAMA
    )

    return conn


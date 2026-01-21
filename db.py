import mysql.connector
import streamlit as st

def get_db():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=st.secrets["mysql"]["port"],
        database=st.secrets["mysql"]["database"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        ssl_ca=st.secrets["mysql"]["ssl_ca"],
        ssl_verify_cert=True,
        use_pure=True,
        connection_timeout=5
    )

    
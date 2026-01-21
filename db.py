import mysql.connector
import streamlit as st
import tempfile

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
    ssl_ca_content = mysql_secrets.get("ssl_ca")
            if ssl_ca_content:
                with tempfile.NamedTemporaryFile(delete=False) as ca_file:
                    ca_file.write(ssl_ca_content.encode("utf-8"))
                    ca_path = ca_file.name
            
                connection_config["ssl_ca"] = ca_path
                connection_config["ssl_verify_cert"] = True
            else:
                st.error("❌ SSL CA tidak ditemukan di secrets")
                return None

    


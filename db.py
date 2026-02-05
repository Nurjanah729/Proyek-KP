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
    
def get_latest_prediction(student_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT result
        FROM predictions
        WHERE student_id = %s
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,))

    data = cursor.fetchone()
    conn.close()
    return data



import streamlit as st
import pandas as pd
from ml_model import run_analysis

st.title("😎 Analisis Performa Akademik")
st.write("Analisis performa mahasiswa menggunakan pendekatan Machine Learning")

# Data mahasiswa (contoh)
data = {
    "Modul": list(range(1, 11)),
    "Nilai": [80, 85, 79, 84, 63, 81, 81, 82, 95, 87]
}

df = pd.DataFrame(data)

st.text_input(
    "Mahasiswa",
    "Ira Rosdiana | AI Engineer | Universitas Parahyangan",
    disabled=True
)

st.table(df)

# Tombol analisis
if st.button("🔍 Menjalankan Analisis"):
    result, weak_modules, avg_score = run_analysis(df)

    st.success(f"✅ Hasil Analisis: {result}")
    st.write(f"📊 Rata-rata Nilai: {avg_score}")

    if weak_modules:
        st.warning(f"⚠ Modul lemah: {', '.join(map(str, weak_modules))}")
    else:
        st.info("🎉 Tidak ada modul lemah")

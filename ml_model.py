import numpy as np
import pandas as pd
import joblib

# =========================
# LOAD MODEL
# =========================
model = joblib.load("random_forest_model (2).pkl")


# =========================
# ANALISIS PERFORMA AKADEMIK
# =========================
def run_analysis(scores_df: pd.DataFrame):
    """
    Input:
        scores_df -> DataFrame dengan kolom:
        - Modul
        - Nilai

    Output:
        result (str)
        weak_modules (list)
        avg_score (float)
    """

    # pastikan data numerik & urut
    scores_df["Modul"] = pd.to_numeric(scores_df["Modul"])
    scores_df["Nilai"] = pd.to_numeric(scores_df["Nilai"])
    scores_df = scores_df.sort_values("Modul")

    # ambil nilai saja (sesuai fitur model)
    X = scores_df["Nilai"].values.reshape(1, -1)

    # =========================
    # PREDIKSI MODEL
    # =========================
    prediction = model.predict(X)[0]

    # =========================
    # RATA-RATA NILAI
    # =========================
    avg_score = round(scores_df["Nilai"].mean(), 2)

    # =========================
    # MODUL LEMAH (<70)
    # =========================
    weak_modules = scores_df[scores_df["Nilai"] < 70]["Modul"].tolist()

    return prediction, weak_modules, avg_score

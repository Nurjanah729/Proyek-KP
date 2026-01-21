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
        confidence (float)
        weak_modules (list)
        avg_score (float)
    """

    # pastikan data numerik & urut
    scores_df["Modul"] = pd.to_numeric(scores_df["Modul"])
    scores_df["Nilai"] = pd.to_numeric(scores_df["Nilai"])
    scores_df = scores_df.sort_values("Modul")

    # ambil nilai saja (harus sesuai jumlah fitur model)
    X = scores_df["Nilai"].values.reshape(1, -1)

    # =========================
    # PREDIKSI MODEL
    # =========================
    prediction = model.predict(X)[0]

    # confidence
    if hasattr(model, "predict_proba"):
        confidence = model.predict_proba(X).max()
    else:
        confidence = 0.8

    # =========================
    # RATA-RATA
    # =========================
    avg_score = scores_df["Nilai"].mean()

    # =========================
    # MODUL LEMAH
    # =========================
    weak_modules = scores_df[scores_df["Nilai"] < 70]["Modul"].tolist()

    return prediction, round(confidence, 2), weak_modules, round(avg_score, 2)

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

    # pastikan numerik & urut
    scores_df["Modul"] = pd.to_numeric(scores_df["Modul"])
    scores_df["Nilai"] = pd.to_numeric(scores_df["Nilai"])
    scores_df = scores_df.sort_values("Modul")

    # =========================
    # SIAPKAN FITUR
    # =========================
    X = scores_df["Nilai"].values

    # jumlah fitur yang DIHARAPKAN model
    expected_features = model.n_features_in_

    # kalau nilai kurang → padding 0
    if len(X) < expected_features:
        X = np.pad(X, (0, expected_features - len(X)))

    # kalau nilai lebih → potong
    elif len(X) > expected_features:
        X = X[:expected_features]

    X = X.reshape(1, -1)

    # =========================
    # PREDIKSI
    # =========================
    prediction = model.predict(X)[0]

    if hasattr(model, "predict_proba"):
        confidence = model.predict_proba(X).max()
    else:
        confidence = 0.8

    # =========================
    # ANALISIS TAMBAHAN
    # =========================
    avg_score = scores_df["Nilai"].mean()
    weak_modules = scores_df[scores_df["Nilai"] < 70]["Modul"].tolist()

    return prediction, round(confidence, 2), weak_modules, round(avg_score, 2)

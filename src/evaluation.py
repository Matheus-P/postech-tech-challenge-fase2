"""Métricas e comparação entre modelos."""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.config import METRICS, RANDOM_STATE


def score(y_true, y_proba, threshold: float = 0.5) -> dict[str, float]:
    """Conjunto de métricas para classificação binária.

    Acurácia sozinha engana em base desbalanceada — por isso ROC-AUC, PR-AUC,
    MCC, F1, precisão e recall vêm junto.
    """
    y_pred = (np.asarray(y_proba) >= threshold).astype(int)
    return {
        "roc_auc": roc_auc_score(y_true, y_proba),
        "pr_auc": average_precision_score(y_true, y_proba),
        "mcc": matthews_corrcoef(y_true, y_pred),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "accuracy": accuracy_score(y_true, y_pred),
    }


def threshold_sweep(y_true, y_proba, grid=None) -> pd.DataFrame:
    """Métricas dependentes de limiar ao longo de uma grade de cortes."""
    if grid is None:
        grid = np.round(np.arange(0.05, 0.96, 0.01), 2)
    linhas = []
    for t in grid:
        s = score(y_true, y_proba, t)
        linhas.append({"limiar": t, "mcc": s["mcc"], "f1": s["f1"],
                       "recall": s["recall"], "precision": s["precision"]})
    return pd.DataFrame(linhas)


def bootstrap_auc(y_true, y_proba, n: int = 1000, seed: int = RANDOM_STATE) -> tuple[float, float]:
    """Intervalo de 95% para o ROC-AUC por reamostragem do conjunto avaliado."""
    y_true = np.asarray(y_true)
    y_proba = np.asarray(y_proba)
    rng = np.random.default_rng(seed)
    aucs = []
    for _ in range(n):
        idx = rng.integers(0, len(y_true), len(y_true))
        if y_true[idx].min() == y_true[idx].max():
            continue
        aucs.append(roc_auc_score(y_true[idx], y_proba[idx]))
    return float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))


def save_table(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Salva uma tabela de resultados em results/metrics/ e a devolve."""
    METRICS.mkdir(parents=True, exist_ok=True)
    df.to_csv(METRICS / f"{name}.csv")
    return df

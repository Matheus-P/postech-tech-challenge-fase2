"""Limpeza e feature engineering."""

import numpy as np
import pandas as pd

from src.config import GROUP

# Gravidade do STATUS em escala ordinal: 0 = em dia, 6 = atraso de 150+ dias.
SEVERIDADE = {"X": 0, "C": 0, "0": 1, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6}

CATEGORICAS = [
    "CODE_GENDER",
    "FLAG_OWN_CAR",
    "FLAG_OWN_REALTY",
    "NAME_INCOME_TYPE",
    "NAME_EDUCATION_TYPE",
    "NAME_FAMILY_STATUS",
    "NAME_HOUSING_TYPE",
    "OCCUPATION_TYPE",
]

CADASTRAIS = [
    "IDADE_ANOS",
    "ANOS_EMPREGO",
    "SEM_VINCULO",
    "AMT_INCOME_TOTAL",
    "RENDA_PER_CAPITA",
    "CNT_CHILDREN",
    "CNT_FAM_MEMBERS",
    "FLAG_WORK_PHONE",
    "FLAG_PHONE",
    "FLAG_EMAIL",
]

HISTORICO = [
    "TEM_HISTORICO",
    "HIST_CONTAS",
    "HIST_MESES",
    "HIST_TEMPO_CASA",
    "HIST_PIOR_STATUS",
    "HIST_PIOR_STATUS_6M",
    "HIST_MESES_ATRASO",
    "HIST_MESES_ATRASO_30",
    "HIST_TEVE_ATRASO_60",
    "HIST_TAXA_ATRASO",
    "HIST_TAXA_QUITADO",
    "HIST_TAXA_SEM_USO",
]


def check_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo de nulos por coluna, em contagem e percentual."""
    total = df.isna().sum()
    pct = (total / len(df) * 100).round(2)
    return (
        pd.DataFrame({"nulos": total, "pct": pct})
        .query("nulos > 0")
        .sort_values("nulos", ascending=False)
    )


def add_application_features(df: pd.DataFrame) -> pd.DataFrame:
    """Variáveis derivadas do formulário de solicitação."""
    out = df.copy()
    sem_vinculo = out["DAYS_EMPLOYED"] > 0          # código 365243 = sem emprego
    out["IDADE_ANOS"] = -out["DAYS_BIRTH"] / 365.25
    out["SEM_VINCULO"] = sem_vinculo.astype(int)
    out["ANOS_EMPREGO"] = np.where(sem_vinculo, 0.0, -out["DAYS_EMPLOYED"] / 365.25)
    out["RENDA_PER_CAPITA"] = out["AMT_INCOME_TOTAL"] / out["CNT_FAM_MEMBERS"]
    out["OCCUPATION_TYPE"] = out["OCCUPATION_TYPE"].fillna("Nao informado")
    return out


def add_history_features(df: pd.DataFrame, credit: pd.DataFrame) -> pd.DataFrame:
    """Comportamento do proponente nas contas que ele já tinha antes desta.

    Para cada conta, usa apenas registros de OUTRAS contas do mesmo proponente
    com data anterior ao mês de abertura desta conta. Nada do que acontece
    depois da abertura, nem na própria conta, entra aqui: é a informação que o
    banco de fato teria no momento da decisão.
    """
    registros = credit.merge(df[["ID", GROUP]], on="ID", how="inner")
    registros["sev"] = registros["STATUS"].map(SEVERIDADE)

    pares = df[["ID", GROUP, "MES_ABERTURA"]].merge(
        registros, on=GROUP, suffixes=("", "_outra")
    )
    pares = pares[
        (pares["ID"] != pares["ID_outra"])
        & (pares["MONTHS_BALANCE"] < pares["MES_ABERTURA"])
    ].copy()
    pares["recente"] = pares["MONTHS_BALANCE"] >= pares["MES_ABERTURA"] - 6
    pares["sev_recente"] = pares["sev"].where(pares["recente"], 0)
    pares["atraso"] = (pares["sev"] >= 1).astype(int)
    pares["atraso_30"] = (pares["sev"] >= 2).astype(int)
    pares["atraso_60"] = (pares["sev"] >= 3).astype(int)
    pares["quitado"] = (pares["STATUS"] == "C").astype(int)
    pares["sem_uso"] = (pares["STATUS"] == "X").astype(int)

    hist = pares.groupby("ID").agg(
        HIST_CONTAS=("ID_outra", "nunique"),
        HIST_MESES=("sev", "size"),
        primeiro_mes=("MONTHS_BALANCE", "min"),
        HIST_PIOR_STATUS=("sev", "max"),
        HIST_PIOR_STATUS_6M=("sev_recente", "max"),
        HIST_MESES_ATRASO=("atraso", "sum"),
        HIST_MESES_ATRASO_30=("atraso_30", "sum"),
        HIST_TEVE_ATRASO_60=("atraso_60", "max"),
        HIST_TAXA_ATRASO=("atraso", "mean"),
        HIST_TAXA_QUITADO=("quitado", "mean"),
        HIST_TAXA_SEM_USO=("sem_uso", "mean"),
    )

    out = df.merge(hist, left_on="ID", right_index=True, how="left")
    out["TEM_HISTORICO"] = out["HIST_CONTAS"].notna().astype(int)
    out["HIST_TEMPO_CASA"] = out["MES_ABERTURA"] - out["primeiro_mes"]
    out = out.drop(columns="primeiro_mes")
    # Sem contas anteriores não há eventos: zero é o valor correto, e a
    # coluna TEM_HISTORICO distingue esse caso de "tem histórico limpo".
    out[HISTORICO] = out[HISTORICO].fillna(0)
    return out

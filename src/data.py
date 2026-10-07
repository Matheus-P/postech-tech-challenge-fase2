"""Carregamento dos dados brutos e montagem da base de contas."""

import pandas as pd

from src.config import (
    BAD_STATUS,
    DATA_PROCESSED,
    GROUP,
    JANELA_MESES,
    PROCESSED_FILE,
    RAW_APP,
    RAW_CREDIT,
    TARGET,
)


def load_raw() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê os dois arquivos brutos de data/raw/ sem nenhuma transformação."""
    for arquivo in (RAW_APP, RAW_CREDIT):
        if not arquivo.exists():
            raise FileNotFoundError(
                f"{arquivo} não encontrado. Veja data/README.md para baixar o dataset."
            )
    return pd.read_csv(RAW_APP), pd.read_csv(RAW_CREDIT)


def build_accounts(app: pd.DataFrame, credit: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por conta (ID), com dados cadastrais e resumo do histórico.

    Colunas criadas:
    - PROPONENTE: contas com cadastro idêntico em todas as colunas recebem o
      mesmo número. É a chave usada para separar treino e teste.
    - MES_ABERTURA: primeiro mês com registro (MONTHS_BALANCE mínimo).
    - MESES_OBSERVADOS: meses entre a abertura e a data de extração.
    - MES_PRIMEIRO_ATRASO: meses desde a abertura até o primeiro atraso 60+.
    - target_qualquer_momento: atraso 60+ em qualquer mês observado.
    """
    # IDs repetidos no cadastro com dados diferentes são ambíguos: descartados.
    app = app.drop_duplicates("ID", keep=False)

    credit = credit.assign(mau=credit["STATUS"].isin(BAD_STATUS))
    resumo = credit.groupby("ID").agg(
        MES_ABERTURA=("MONTHS_BALANCE", "min"),
        target_qualquer_momento=("mau", "max"),
    )
    primeiro = (
        credit[credit["mau"]].groupby("ID")["MONTHS_BALANCE"].min().rename("mes_mau")
    )
    resumo = resumo.join(primeiro)
    resumo["MESES_OBSERVADOS"] = -resumo["MES_ABERTURA"]
    resumo["MES_PRIMEIRO_ATRASO"] = resumo["mes_mau"] - resumo["MES_ABERTURA"]
    resumo["target_qualquer_momento"] = resumo["target_qualquer_momento"].astype(int)
    resumo = resumo.drop(columns="mes_mau").reset_index()

    df = app.merge(resumo, on="ID", how="inner").sort_values("ID").reset_index(drop=True)

    cadastro = [c for c in app.columns if c != "ID"]
    df[GROUP] = df.groupby(cadastro, dropna=False, sort=True).ngroup()
    return df


def add_target(df: pd.DataFrame, janela: int = JANELA_MESES) -> pd.DataFrame:
    """Mantém contas com a janela completa e cria o alvo dentro dela.

    Uma conta aberta há menos de `janela` meses ainda não teve tempo de mostrar
    se é boa ou má; mantê-la como "boa" contaminaria o alvo.
    """
    out = df[df["MESES_OBSERVADOS"] >= janela].copy()
    out[TARGET] = (out["MES_PRIMEIRO_ATRASO"] <= janela).astype(int)
    return out.reset_index(drop=True)


def save_processed(df: pd.DataFrame) -> None:
    """Grava o dataset tratado em data/processed/."""
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)


def load_processed() -> pd.DataFrame:
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError(
            f"{PROCESSED_FILE} não encontrado. Rode o notebook 02 antes."
        )
    return pd.read_csv(PROCESSED_FILE)

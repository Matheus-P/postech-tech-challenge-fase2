"""Configuração central do projeto: caminhos, semente e constantes.

Importe daqui em todos os notebooks para que os resultados sejam reproduzíveis.
"""

from pathlib import Path

# --- Semente -----------------------------------------------------------------
# Use em TODO ponto que envolva aleatoriedade: split, modelos, CV, permutação.
RANDOM_STATE = 42

# --- Caminhos ----------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
MODELS = RESULTS / "models"
METRICS = RESULTS / "metrics"

# --- Dataset -----------------------------------------------------------------
RAW_APP = DATA_RAW / "application_record.csv"
RAW_CREDIT = DATA_RAW / "credit_record.csv"
PROCESSED_FILE = DATA_PROCESSED / "dataset_tratado.csv"

TARGET = "target"
GROUP = "PROPONENTE"          # identificador do proponente (perfil cadastral)

# --- Definição do alvo -------------------------------------------------------
# STATUS 2..5 = atraso de 60 dias ou mais. O alvo é 1 quando a conta atinge
# esse atraso dentro da janela de desempenho, contada a partir da abertura.
BAD_STATUS = ("2", "3", "4", "5")
JANELA_MESES = 12

# --- Split -------------------------------------------------------------------
TEST_FOLDS = 5                # 1 de 5 partes vira teste (20%)
CV_FOLDS = 5

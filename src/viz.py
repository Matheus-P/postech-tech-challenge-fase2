"""Estilo único para os gráficos dos notebooks e da apresentação."""

import matplotlib.pyplot as plt

from src.config import FIGURES

AZUL = "#2a78d6"
LARANJA = "#eb6834"
VERDE = "#1baf7a"
CINZA = "#898781"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
GRADE = "#e1e0d9"
FUNDO = "#fcfcfb"
AZUIS = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]


def set_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": FUNDO,
        "axes.facecolor": FUNDO,
        "savefig.facecolor": FUNDO,
        "figure.dpi": 110,
        "savefig.dpi": 160,
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelcolor": TINTA_2,
        "axes.edgecolor": "#c3c2b7",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRADE,
        "grid.linewidth": 0.6,
        "xtick.color": CINZA,
        "ytick.color": CINZA,
        "text.color": TINTA,
        "legend.frameon": False,
        "lines.linewidth": 2,
    })


def save(fig, name: str) -> None:
    """Grava a figura em results/figures/ para uso na apresentação."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{name}.png", bbox_inches="tight")
